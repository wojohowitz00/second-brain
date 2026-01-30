# Second Brain

## What This Is

A macOS app that connects Slack to Obsidian, using local LLM (Ollama) to classify and route notes into a PARA-structured vault across three domains.

## Core Value

**Capture thoughts anywhere, have them automatically organized.**

The friction of manual filing kills capture habits. This app removes that friction: send a message to Slack from any device, and it appears in the right place in your Obsidian vault — classified by domain, PARA type, subject, and category — without touching your laptop.

## The Problem

Extemporaneous thoughts are the hardest to capture. You're walking, driving, in a meeting — an idea hits, but your second brain system lives on your laptop in Obsidian. By the time you can file it properly, the thought is gone or stale.

Current workarounds (Apple Notes, voice memos, email-to-self) create orphaned capture points that never get processed. The inbox zero dream dies in scattered apps.

## The Solution

**Slack as universal inbox → Local LLM classification → Obsidian as organized vault**

1. User sends message to dedicated Slack channel (works from any device)
2. macOS app pulls messages when machine is available (Slack = queue)
3. Ollama classifies: domain → PARA type → subject → category
4. Creates `.md` file with proper frontmatter in correct folder
5. User can reply with `fix:` to correct misclassification

## Vault Structure

Three domains, each with PARA structure and subject subfolders:

```
Home/
├── Personal/
│   ├── Projects/[subjects]/
│   ├── Areas/[subjects]/
│   ├── Resources/[subjects]/
│   └── Archives/[subjects]/
├── CCBH/
│   └── [same PARA structure]
└── Just Value/
    └── [same PARA structure]
```

**Vault location:** `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Home`

Every `.md` file tagged with: `domain`, `para`, `subject`, `category`

## Target User

You (Richard). Secondary: technically moderate users who can install Ollama but shouldn't need CLI.

## Requirements

### Validated

- ✓ Slack message fetching with retry/rate limiting — existing
- ✓ State management for idempotency (message tracking, mapping) — existing
- ✓ Obsidian file writing with YAML frontmatter — existing
- ✓ Correction flow via `fix:` thread replies — existing
- ✓ Health monitoring and failure alerts — existing
- ✓ Daily digest generation — existing
- ✓ Weekly review generation — existing
- ✓ Entity extraction and wikilink generation — existing

### Active

- [ ] Dynamic vault scanner — builds domain/PARA/subject map from actual folder structure
- [ ] Periodic map refresh — keeps classification vocabulary current as vault evolves
- [ ] Local LLM classification — replace Claude API with Ollama for privacy and offline
- [ ] Three-domain routing — Personal, CCBH, Just Value instead of flat categories
- [ ] PARA-aware classification — Projects/Areas/Resources/Archives assignment
- [ ] Subject classification — route to correct subject subfolder within PARA
- [ ] Category tagging — assign semantic category tag to each note
- [ ] Event-driven processing — trigger on Slack webhook or process backlog on startup
- [ ] macOS .pkg installer — single installer for non-technical distribution
- [ ] First-run setup wizard — check Ollama, guide model installation, configure vault path
- [ ] Menu bar presence — lightweight UI showing status, last sync, manual trigger

### Out of Scope

- iOS native app — Slack's iOS app handles mobile capture adequately
- Real-time sync — event-driven with backlog processing is sufficient
- Multi-user support — personal tool, single vault
- Cloud sync of state — local-only, Obsidian handles vault sync via iCloud
- Custom LLM training — use off-the-shelf Ollama models

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Ollama over Claude API | Privacy, offline capability, no API costs | — Pending model selection |
| .pkg installer | Target users can't use CLI, need double-click install | — Pending build tooling |
| Slack as queue | No separate queue infra; messages persist until Mac is available | Approved |
| Vault scanning | Dynamic discovery vs manual config; adapts as vault evolves | Approved |
| Event-driven over daemon | Resource efficient, use case doesn't need instant processing | Approved |
| First-run wizard | Bridge Ollama installation without CLI exposure | Approved |

## Constraints

- **Platform:** macOS only (10.15+)
- **Dependencies:** Ollama must be installed separately (not bundled)
- **Vault location:** iCloud-synced Obsidian vault (fixed path)
- **Model size:** Must run on MacBook Air M1 (8GB RAM constraint)

## Open Questions

1. Which Ollama model? Llama 3.2 (3B) vs Mistral vs others — need to test classification quality
2. Webhook vs polling? Slack webhooks require public endpoint; polling simpler but less immediate
3. What triggers "startup"? Login item? Menu bar app launch? LaunchAgent?

## Success Criteria

1. User sends Slack message → appears in correct vault location within 5 minutes of Mac wake
2. Classification accuracy >90% across domain/PARA/subject (measured by fix: rate)
3. Non-technical user can install from .pkg without terminal usage
4. First-run wizard successfully guides Ollama + model setup

---

*Last updated: 2026-01-30 after initialization*
