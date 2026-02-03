import state


def _setup_state_paths(temp_state_dir, monkeypatch):
    monkeypatch.setattr(state, "STATE_DIR", temp_state_dir)
    monkeypatch.setattr(state, "YOUTUBE_URLS_FILE", temp_state_dir / "youtube_urls.json")


def test_ingest_youtube_creates_note_and_transcript(tmp_path, monkeypatch, temp_state_dir):
    import youtube_ingest

    _setup_state_paths(temp_state_dir, monkeypatch)
    monkeypatch.setattr(youtube_ingest, "VAULT_ROOT", tmp_path)
    monkeypatch.setattr(
        youtube_ingest.VaultScanner,
        "get_structure",
        lambda self: {"Personal": {"3_Resources": ["VideoNotes"]}},
    )
    monkeypatch.setattr(
        youtube_ingest,
        "fetch_youtube_metadata",
        lambda url: {
            "id": "abc123",
            "title": "Test Video",
            "uploader": "Test Channel",
            "upload_date": "20260101",
        },
    )

    def fake_download_captions(url, transcripts_dir):
        captions = transcripts_dir / "abc123.vtt"
        captions.write_text("WEBVTT\n\n00:00.000 --> 00:01.000\nHello world\n")
        return captions

    monkeypatch.setattr(youtube_ingest, "_download_captions", fake_download_captions)
    monkeypatch.setattr(youtube_ingest, "_download_audio", lambda url, assets_dir: None)

    note_path = youtube_ingest.ingest_youtube(
        "https://youtu.be/abc123",
        domain="Personal",
        transcript_mode=youtube_ingest.TRANSCRIPT_CAPTIONS,
        summarize=False,
    )

    assert note_path is not None
    assert note_path.exists()
    content = note_path.read_text()
    assert "source: youtube" in content

    transcript_path = (
        tmp_path / "Personal" / "3_Resources" / "VideoNotes" / "_transcripts" / "abc123.txt"
    )
    assert transcript_path.exists()


def test_ingest_skips_when_already_processed(tmp_path, monkeypatch, temp_state_dir):
    import youtube_ingest

    _setup_state_paths(temp_state_dir, monkeypatch)
    monkeypatch.setattr(youtube_ingest, "VAULT_ROOT", tmp_path)

    note_path = tmp_path / "Personal" / "3_Resources" / "VideoNotes" / "note.md"
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text("existing")
    state.record_youtube_url_success("https://youtu.be/abc123", note_path)

    def fail_metadata(_):
        raise AssertionError("fetch_youtube_metadata should not be called")

    monkeypatch.setattr(youtube_ingest, "fetch_youtube_metadata", fail_metadata)

    result = youtube_ingest.ingest_youtube(
        "https://youtu.be/abc123",
        domain="Personal",
        transcript_mode=youtube_ingest.TRANSCRIPT_CAPTIONS,
        summarize=False,
    )
    assert result == note_path
