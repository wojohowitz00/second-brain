# Research Summary

**Date:** 2026-01-30

## Key Findings

### Stack Recommendations

| Component | Recommendation | Confidence | Alternative |
|-----------|---------------|------------|-------------|
| macOS Packaging | py2app + pkgbuild | 60% | PyInstaller (not native enough) |
| Ollama Integration | ollama-python 0.3.0+ | 90% | Direct HTTP (more work) |
| Menu Bar UI | rumps 0.4.0 | 55% | PyObjC (more robust, complex) |
| LLM Model | Llama 3.2 3B | 85% | Mistral 7B (too large for 8GB) |

**Critical Finding:** rumps is unmaintained (last release Aug 2023). May need PyObjC fallback for macOS 15+ compatibility.

### Architecture Pattern

**7 Components:**
1. Menu Bar App (rumps) — UI layer, lifecycle management
2. Backend Worker (asyncio) — event loop replacing cron
3. Ollama Client — LLM abstraction layer
4. Vault Scanner — dynamic domain/PARA/subject discovery
5. Slack Integration — existing (preserved)
6. State Management — existing (preserved)
7. First-Run Wizard — setup UX for Ollama

**Key Architectural Decisions:**
- Multi-process: menu bar spawns worker (isolation, responsive UI)
- File-based IPC: command queue for manual triggers (simple, debuggable)
- Event-driven: polling every 2 min, not Slack webhooks (no public endpoint needed)

### Features Priority

**Table Stakes (already implemented):**
- Message ingestion with idempotency ✓
- Basic classification ✓
- Markdown file creation ✓
- Confirmation feedback ✓
- Correction mechanism (fix:) ✓

**New Requirements:**
- Multi-level classification (domain → PARA → subject → category)
- Dynamic vault vocabulary from folder scanning
- Local LLM (Ollama) replacing Claude API
- Menu bar presence with status display
- First-run wizard for dependency setup
- .pkg installer for distribution

### Critical Pitfalls to Avoid

1. **Dependency Bundling Hell** — Test bundling early, don't wait until end
2. **Code Signing/Notarization** — Get Apple Developer ID if targeting non-technical users ($99/yr)
3. **File System Permissions (TCC)** — iCloud Documents folder needs explicit entitlements
4. **Ollama Model Loading Delays** — First classification after cold start takes 10-30s
5. **Classification Drift** — LLM may return unexpected values; validate strictly

### Suggested Build Order

| Phase | Focus | Risk | Days |
|-------|-------|------|------|
| 1 | Foundation — validate existing backend | Low | 0 |
| 2 | Vault Scanner — dynamic discovery | Low | 1-2 |
| 3 | Ollama Integration — replace Claude | **High** | 2-3 |
| 4 | Backend Worker — event loop refactor | Medium | 2-3 |
| 5 | Menu Bar App — rumps UI | Medium | 1-2 |
| 6 | First-Run Wizard — setup UX | Low | 1-2 |
| 7 | Packaging — .pkg installer | **High** | 2-3 |

**Critical Path:** Phase 3 (Ollama) is highest risk — validate classification quality before UI/packaging investment.

## What NOT to Use

- ❌ Electron/Tauri — 100+ MB overhead
- ❌ Docker — breaks Ollama GPU access
- ❌ Homebrew distribution — requires CLI
- ❌ App Store — sandboxing conflicts with vault access
- ❌ Slack webhooks — requires public endpoint

## Open Questions for Requirements

1. Apple Developer ID — needed for notarization ($99/yr)?
2. Python version — stick with 3.13 or drop to 3.12 for py2app compatibility?
3. rumps vs PyObjC — accept maintenance risk or invest in more complex alternative?

---

*Synthesized from: STACK.md, ARCHITECTURE.md, FEATURES.md, PITFALLS.md*
