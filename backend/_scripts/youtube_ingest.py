#!/usr/bin/env python3
"""
YouTube ingestion script for Second Brain.

Pipeline:
1) Fetch metadata with yt-dlp
2) Download captions or transcribe audio
3) Summarize with local Ollama (optional)
4) Write note + transcript bundle into the vault
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from message_classifier import ClassificationResult, DEFAULT_DOMAIN
from ollama_client import OllamaClient, OllamaError, OllamaServerNotRunning, OllamaTimeout
from vault_scanner import VAULT_ROOT, VaultScanner
from file_writer import sanitize_filename, create_youtube_note_file
from state import (
    get_youtube_url_entry,
    normalize_youtube_url,
    record_youtube_url_failed,
    record_youtube_url_processing,
    record_youtube_url_success,
    should_process_youtube_url,
)

DEFAULT_SUBJECT = "VideoNotes"
DEFAULT_PARA_TYPE = "3_Resources"
DEFAULT_CATEGORY = "reference"
DEFAULT_REASONING = "YouTube ingest"
SUMMARY_MODEL_ENV = "OLLAMA_MODEL_SUMMARY"

TRANSCRIPT_AUTO = "auto"
TRANSCRIPT_CAPTIONS = "captions"
TRANSCRIPT_WHISPER = "whisper"
TRANSCRIPT_NONE = "none"
TRANSCRIPT_MODES = {TRANSCRIPT_AUTO, TRANSCRIPT_CAPTIONS, TRANSCRIPT_WHISPER, TRANSCRIPT_NONE}


def _run_cmd(cmd: list[str], cwd: Optional[Path] = None) -> str:
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        details = stderr or stdout or "unknown error"
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{details}")
    return result.stdout.strip()


def _check_command_available(command: str) -> bool:
    return shutil.which(command) is not None


def _parse_upload_date(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y%m%d").date().isoformat()
    except ValueError:
        return None


def fetch_youtube_metadata(url: str) -> dict:
    if not _check_command_available("yt-dlp"):
        raise RuntimeError("yt-dlp not found. Install it to fetch YouTube metadata.")

    raw = _run_cmd(["yt-dlp", "--no-warnings", "--dump-single-json", url])
    data = json.loads(raw)
    if data.get("_type") == "playlist" and data.get("entries"):
        data = data["entries"][0]
    return data


def _ensure_bundle_dirs(base_dir: Path) -> dict:
    subdirs = {
        "assets": base_dir / "_assets",
        "transcripts": base_dir / "_transcripts",
        "summaries": base_dir / "_summaries",
        "actions": base_dir / "_actions",
    }
    for path in subdirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return subdirs


def _download_audio(url: str, assets_dir: Path) -> Optional[Path]:
    if not _check_command_available("yt-dlp"):
        return None
    if not _check_command_available("ffmpeg"):
        raise RuntimeError("ffmpeg not found. Required for audio extraction.")

    output_template = str(assets_dir / "%(id)s.%(ext)s")
    _run_cmd(
        [
            "yt-dlp",
            "-x",
            "--audio-format",
            "mp3",
            "-o",
            output_template,
            url,
        ]
    )

    matches = list(assets_dir.glob("*.mp3"))
    return matches[0] if matches else None


def _download_captions(url: str, transcripts_dir: Path) -> Optional[Path]:
    if not _check_command_available("yt-dlp"):
        return None

    output_template = str(transcripts_dir / "%(id)s.%(ext)s")
    _run_cmd(
        [
            "yt-dlp",
            "--write-auto-subs",
            "--sub-langs",
            "en",
            "--skip-download",
            "-o",
            output_template,
            url,
        ]
    )

    candidates = list(transcripts_dir.glob("*.vtt")) + list(transcripts_dir.glob("*.srt"))
    return candidates[0] if candidates else None


def _vtt_to_text(raw: str) -> str:
    lines = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if "-->" in stripped:
            continue
        if stripped.isdigit():
            continue
        lines.append(stripped)
    return "\n".join(lines).strip()


def _write_transcript_from_captions(captions_path: Path, transcripts_dir: Path, video_id: str) -> Optional[Path]:
    try:
        raw = captions_path.read_text()
    except Exception:
        return None
    text = _vtt_to_text(raw)
    if not text:
        return None
    transcript_path = transcripts_dir / f"{video_id or 'transcript'}.txt"
    transcript_path.write_text(text)
    return transcript_path


def _transcribe_with_whisper(audio_path: Path, transcripts_dir: Path, video_id: str) -> Optional[Path]:
    if not _check_command_available("whisper"):
        return None
    output_dir = transcripts_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    _run_cmd(
        [
            "whisper",
            str(audio_path),
            "--model",
            "base",
            "--output_format",
            "txt",
            "--output_dir",
            str(output_dir),
        ]
    )

    candidates = list(output_dir.glob("*.txt"))
    if not candidates:
        return None
    transcript_path = candidates[0]
    if video_id:
        target = output_dir / f"{video_id}.txt"
        if transcript_path != target:
            transcript_path.replace(target)
            transcript_path = target
    return transcript_path


def _truncate_text(text: str, max_chars: int = 12000) -> Tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars], True


def summarize_transcript(
    transcript_text: str,
    title: str,
    channel: Optional[str],
    url: str,
    model: Optional[str] = None,
) -> dict:
    client = OllamaClient(model=model)
    prompt = (
        "You are summarizing a YouTube transcript for a personal knowledge system.\n"
        "Return JSON only with keys: summary (string), outline (list of strings), actions (list of strings).\n\n"
        f"Title: {title}\n"
        f"Channel: {channel or 'Unknown'}\n"
        f"URL: {url}\n\n"
        "Transcript:\n"
        f"{transcript_text}\n"
    )
    response = client.chat([{"role": "user", "content": prompt}])
    content = response.get("message", {}).get("content", "").strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Attempt best-effort extraction
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(content[start : end + 1])
            except json.JSONDecodeError:
                pass
        return {"summary": content, "outline": [], "actions": []}


def choose_domain(requested: Optional[str]) -> str:
    if requested:
        return requested
    return DEFAULT_DOMAIN


def ingest_youtube(
    url: str,
    domain: Optional[str] = None,
    subject: str = DEFAULT_SUBJECT,
    category: str = DEFAULT_CATEGORY,
    transcript_mode: str = TRANSCRIPT_AUTO,
    summarize: bool = True,
    force: bool = False,
    keep_audio: bool = False,
    summary_model: Optional[str] = None,
) -> Optional[Path]:
    normalized = normalize_youtube_url(url)
    existing = get_youtube_url_entry(normalized)
    if not should_process_youtube_url(normalized, force=force):
        note_path = existing.get("note_path") if existing else None
        if note_path:
            print(f"Already processed: {note_path}")
        else:
            print("Already processed.")
        return Path(note_path) if note_path else None

    record_youtube_url_processing(normalized, metadata={"url": normalized})

    metadata = fetch_youtube_metadata(normalized)
    video_id = metadata.get("id") or ""
    title = metadata.get("title") or normalized
    channel = metadata.get("uploader") or metadata.get("channel") or metadata.get("uploader_id")
    published = _parse_upload_date(metadata.get("upload_date"))

    vault_scanner = VaultScanner()
    structure = vault_scanner.get_structure()
    resolved_domain = choose_domain(domain)
    if resolved_domain not in structure:
        print(f"Warning: domain '{resolved_domain}' not found in vault; creating folders.")

    base_dir = VAULT_ROOT / resolved_domain / DEFAULT_PARA_TYPE / subject
    subdirs = _ensure_bundle_dirs(base_dir)

    transcript_path = None
    audio_path = None

    try:
        if transcript_mode in {TRANSCRIPT_AUTO, TRANSCRIPT_CAPTIONS}:
            captions_path = _download_captions(normalized, subdirs["transcripts"])
            if captions_path:
                transcript_path = _write_transcript_from_captions(
                    captions_path,
                    subdirs["transcripts"],
                    video_id or sanitize_filename(title),
                )

        if not transcript_path and transcript_mode in {TRANSCRIPT_AUTO, TRANSCRIPT_WHISPER}:
            audio_path = _download_audio(normalized, subdirs["assets"])
            if audio_path:
                transcript_path = _transcribe_with_whisper(
                    audio_path,
                    subdirs["transcripts"],
                    video_id or sanitize_filename(title),
                )

        transcript_text = ""
        truncated = False
        if transcript_path and transcript_path.exists():
            transcript_text = transcript_path.read_text()
            transcript_text, truncated = _truncate_text(transcript_text)
            if truncated:
                transcript_text += "\n\n[Transcript truncated for summarization]"

        summary_data = {"summary": "", "outline": [], "actions": []}
        if summarize and transcript_text:
            model = summary_model or os.environ.get(SUMMARY_MODEL_ENV)
            try:
                summary_data = summarize_transcript(
                    transcript_text=transcript_text,
                    title=title,
                    channel=channel,
                    url=normalized,
                    model=model,
                )
            except (OllamaServerNotRunning, OllamaTimeout, OllamaError) as e:
                print(f"Summary skipped (Ollama error): {e}")

        classification = ClassificationResult(
            domain=resolved_domain,
            para_type=DEFAULT_PARA_TYPE,
            subject=subject,
            category=category,
            confidence=1.0,
            reasoning=DEFAULT_REASONING,
        )

        transcript_rel = None
        if transcript_path and transcript_path.exists():
            try:
                transcript_rel = str(transcript_path.relative_to(base_dir))
            except ValueError:
                transcript_rel = transcript_path.name

        summary_text = summary_data.get("summary") or ""
        outline_items = summary_data.get("outline") or []
        actions_items = summary_data.get("actions") or []
        if not isinstance(outline_items, list):
            outline_items = [str(outline_items)]
        if not isinstance(actions_items, list):
            actions_items = [str(actions_items)]

        note_path = create_youtube_note_file(
            classification=classification,
            title=title,
            source_url=normalized,
            source_title=title,
            source_channel=channel,
            source_published=published,
            summary=str(summary_text),
            outline=outline_items,
            actions=actions_items,
            transcript_rel_path=transcript_rel,
            vault_path=VAULT_ROOT,
            timestamp=datetime.now().isoformat(),
            status="unverified",
            verified=False,
        )

        if audio_path and not keep_audio and audio_path.exists():
            audio_path.unlink()

        record_youtube_url_success(
            normalized,
            note_path=note_path,
            metadata={
                "id": video_id,
                "title": title,
                "channel": channel,
                "published": published,
            },
        )

        print(f"✓ Ingested: {note_path}")
        return note_path

    except Exception as e:
        record_youtube_url_failed(normalized, error=str(e))
        raise


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest a YouTube URL into the vault.")
    parser.add_argument("url", help="YouTube URL to ingest")
    parser.add_argument("--domain", help="Vault domain (e.g., Personal, Work)")
    parser.add_argument("--subject", default=DEFAULT_SUBJECT, help="Subject folder name")
    parser.add_argument("--category", default=DEFAULT_CATEGORY, help="Category tag")
    parser.add_argument(
        "--transcript",
        default=TRANSCRIPT_AUTO,
        choices=sorted(TRANSCRIPT_MODES),
        help="Transcript mode: auto, captions, whisper, none",
    )
    parser.add_argument("--no-summary", action="store_true", help="Skip LLM summarization")
    parser.add_argument("--force", action="store_true", help="Re-ingest even if already processed")
    parser.add_argument("--keep-audio", action="store_true", help="Keep downloaded audio file")
    parser.add_argument("--summary-model", help="Override Ollama model for summarization")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        ingest_youtube(
            url=args.url,
            domain=args.domain,
            subject=args.subject,
            category=args.category,
            transcript_mode=args.transcript,
            summarize=not args.no_summary,
            force=args.force,
            keep_audio=args.keep_audio,
            summary_model=args.summary_model,
        )
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
