# Slack-to-Knowledge-Base Features Research

**Research Date:** 2026-01-30
**Context:** Adding LLM classification intelligence to existing Slack → Obsidian pipeline
**Scope:** Identify table stakes, differentiators, and anti-features for PARA-based classification

---

## Executive Summary

Slack-to-knowledge-base tools fall into three categories:
1. **Search/retrieval** (Guru, Tettra, Notion AI) - Help find existing knowledge
2. **Auto-documentation** (Donut, Slite) - Convert conversations into documentation
3. **Personal knowledge capture** (Mem, Reflect, this system) - Organize individual thoughts

**Our position:** Personal knowledge capture with PARA routing + local-first privacy.

**Key insight:** Classification accuracy matters less than classification transparency + easy correction. Users tolerate 80% accuracy if they can fix mistakes in <5 seconds and trust the system won't silently corrupt their vault.

---

## Feature Categories

### 1. Table Stakes (Must Have or Users Frustrated)

These are baseline expectations. Missing any of these creates immediate friction.

#### 1.1 Message Ingestion
**Complexity:** Low
**Status:** ✓ Implemented

- Fetch messages from designated Slack channel
- Handle rate limits and retries
- Idempotency (don't duplicate on re-run)
- Support threaded replies
- Filter bot messages

**Why table stakes:** Without reliable ingestion, nothing else matters. Users need to trust that posting to Slack = eventual processing.

**Dependencies:** None

---

#### 1.2 Basic Classification
**Complexity:** Medium
**Status:** ✓ Implemented (simple 4-category)

- Route to 2-5 stable categories (people/projects/ideas/admin OR Projects/Areas/Resources/Archives)
- Return confidence score
- Handle ambiguous input gracefully
- Classification prompt that matches user's mental model

**Why table stakes:** This is the core value prop. Without classification, it's just a manual filing system with extra steps.

**Dependencies:** LLM API or local model

---

#### 1.3 Markdown File Creation
**Complexity:** Low
**Status:** ✓ Implemented

- Create files with YAML frontmatter
- Sanitize filenames (no path traversal, invalid chars)
- Handle duplicate filenames (append timestamp)
- Preserve original capture text
- Write to correct folder based on classification

**Why table stakes:** Output must be valid Obsidian markdown or the vault becomes unusable.

**Dependencies:** Filesystem access

---

#### 1.4 Confirmation Feedback
**Complexity:** Low
**Status:** ✓ Implemented

- Reply in Slack with where the note was filed
- Show confidence score
- Include filename/link for reference
- Fast feedback (<30 seconds)

**Why table stakes:** Without feedback, users don't trust the system and keep checking manually.

**Dependencies:** Slack API write access

---

#### 1.5 Correction Mechanism
**Complexity:** Medium
**Status:** ✓ Implemented (`fix:` command)

- Allow user to override classification
- Move file to correct location
- Update metadata/frontmatter
- Confirm correction in Slack
- Preserve original capture

**Why table stakes:** No classifier is perfect. Without corrections, misclassifications become permanent vault pollution.

**Dependencies:** State management (message-to-file mapping)

---

#### 1.6 State Management
**Complexity:** Medium
**Status:** ✓ Implemented

- Track processed messages (prevent duplicates)
- Map messages to created files (enable corrections)
- Handle concurrent access safely
- Persist across restarts
- Cleanup old state (avoid unbounded growth)

**Why table stakes:** Without state, system either duplicates work or loses ability to correct mistakes.

**Dependencies:** Atomic file operations with locking

---

#### 1.7 Error Handling & Logging
**Complexity:** Medium
**Status:** ✓ Implemented

- Log all processing attempts (audit trail)
- Capture failures with full context
- Dead letter queue for manual review
- Don't silently drop messages
- Surface errors to user (DM alerts)

**Why table stakes:** Users need to trust the system. Silent failures = abandonment.

**Dependencies:** Logging infrastructure, alert mechanism

---

### 2. Differentiators (Competitive Advantage)

These features separate good implementations from great ones.

#### 2.1 PARA-Aware Classification
**Complexity:** High
**Status:** ⏳ Planned (current milestone)

- Distinguish Projects (has deadline) from Areas (ongoing)
- Route Resources (reference material) separately from Archives
- Understand temporal vs perpetual context
- Classify across domain dimensions (Personal/Work/Side Project)

**Why differentiating:** Most tools use flat categories or tags. PARA routing requires understanding project lifecycle and temporal boundaries. This matches how GTD/BASB users think.

**Implementation challenges:**
- Distinguishing "project" (has end state) from "area" (ongoing responsibility)
- Detecting when something is reference material vs actionable
- Determining domain from context (work vs personal vs side project)

**Dependencies:**
- Richer prompt engineering
- Possibly multi-stage classification
- Domain vocabulary scanning from vault

**Reference:** Tiago Forte's PARA method (Projects/Areas/Resources/Archives)

---

#### 2.2 Dynamic Vault Scanning
**Complexity:** High
**Status:** ⏳ Planned

- Scan existing vault structure at startup
- Build domain/PARA/subject map from actual folders
- Keep classification vocabulary current as vault evolves
- Periodic refresh (daily or on-demand)
- Discover subject categories without hardcoding

**Why differentiating:** Static configuration breaks as vaults grow. Dynamic scanning means classification vocabulary grows with the user's knowledge graph.

**Implementation challenges:**
- Parsing folder structure reliably
- Distinguishing structure from content folders (e.g., `_templates`)
- Handling inconsistent naming
- Performance at scale (1000+ folders)
- Caching to avoid re-scanning on every message

**Dependencies:**
- Filesystem traversal
- Configuration for ignored paths
- Caching layer

---

#### 2.3 Subject Classification
**Complexity:** Medium-High
**Status:** ⏳ Planned

- Route to subject subfolder within PARA category
- Learn subjects from existing vault structure
- Handle multi-subject ambiguity
- Default to general folder if unclear

**Why differentiating:** Flat PARA is still too broad. "Projects" with 50 items is overwhelming. Subject folders (e.g., Projects/Health/, Projects/App Development/) add one more layer of automatic organization.

**Implementation challenges:**
- Subject vocabulary is personal and emergent
- Subject boundaries are fuzzy (is "learning science" Research or Professional Development?)
- Multi-subject notes (solution: pick primary, add tags for secondary)

**Dependencies:**
- Vault scanner (to discover subjects)
- Extended classification prompt

---

#### 2.4 Entity Extraction & Wikilinks
**Complexity:** Medium
**Status:** ✓ Implemented

- Extract people and project names from text
- Auto-generate `[[wikilinks]]` in body
- Create stub files for new entities
- Build knowledge graph automatically
- Link related notes bidirectionally

**Why differentiating:** Most tools create isolated documents. Wikilinks create a network. Over time, this compounds into a genuine "second brain" instead of a dumping ground.

**Enhancement opportunities:**
- Extract more entity types (books, companies, concepts)
- Confidence scores for entity extraction
- Alias matching (Sara/Sarah, Project X/ProjectX)

**Dependencies:**
- Entity recognition (via LLM)
- Stub file templates

---

#### 2.5 Confidence Thresholds & Review Queue
**Complexity:** Medium
**Status:** ✓ Partially implemented (logs low confidence, but no review UI)

- Set confidence threshold (e.g., 0.6)
- Below threshold → hold for review
- Daily digest includes needs-review items
- User approves/corrects in batch
- Learn from corrections (future: feedback loop)

**Why differentiating:** Prevents bad classifications from polluting vault. Shows respect for user's trust.

**Enhancement opportunities:**
- Dedicated review UI (vs scanning inbox logs)
- One-click approve in Slack
- Track fix patterns to improve prompts

**Dependencies:**
- State management for pending items
- Review interface (Slack interactive messages or Obsidian dashboard)

---

#### 2.6 Local LLM (Ollama) Support
**Complexity:** High
**Status:** ⏳ Planned

- Privacy: No data leaves machine
- Offline capability: Works without internet
- Cost: No API fees
- Model selection: Llama 3.2 (3B) or Mistral
- Trade-off: Slightly lower accuracy for privacy/cost

**Why differentiating:** Privacy-conscious users won't use cloud APIs for personal thoughts. Local LLM = trust.

**Implementation challenges:**
- Model selection (accuracy vs resource usage)
- Prompt engineering for smaller models
- Setup complexity (Ollama installation)
- Performance on M1 MacBook Air (8GB RAM)

**Dependencies:**
- Ollama installed separately
- Model download and management
- Fallback to cloud if local unavailable

---

#### 2.7 Daily Digest & Weekly Review
**Complexity:** Medium
**Status:** ✓ Implemented

- Morning summary of yesterday's captures
- Weekly rollup with patterns and insights
- Surface stale projects (not touched in 14+ days)
- Highlight pending follow-ups
- Delivered via Slack DM

**Why differentiating:** Capture is 10% of the value. Surfacing is 90%. Most tools stop at capture.

**Enhancement opportunities:**
- AI-generated insights (patterns across captures)
- Suggested connections between notes
- "Automation opportunities" detection
- Prioritization recommendations

**Dependencies:**
- Vault scanning
- LLM for summarization
- Slack DM delivery

---

#### 2.8 Multi-Domain Routing
**Complexity:** Medium
**Status:** ⏳ Planned (current milestone)

- Route to Personal/CCBH/Just Value domains
- Each domain has independent PARA structure
- Infer domain from content (project names, keywords)
- Support explicit domain hints (prefix or tagging)

**Why differentiating:** Knowledge workers juggle multiple contexts. Mixing personal/work/side-project notes creates cognitive overhead. Clean separation = mental clarity.

**Implementation challenges:**
- Domain inference (keywords? tone? explicit markers?)
- Handling ambiguous cases (is "meeting notes" work or personal?)
- Balancing automatic routing with explicit overrides

**Dependencies:**
- Domain vocabulary (scanned or configured)
- Extended classification prompt

---

#### 2.9 Health Monitoring & Alerts
**Complexity:** Low
**Status:** ✓ Implemented

- Track last successful run
- Alert if system hasn't processed messages in N hours
- Alert if failure rate exceeds threshold (3+ per day)
- Send DM alerts via Slack
- Log health check results

**Why differentiating:** Silent failure = abandoned tool. Proactive alerts = trust.

**Dependencies:**
- State management (run history)
- Slack DM capability

---

### 3. Nice-to-Haves (Not Critical)

Features that add polish but aren't necessary for core value prop.

#### 3.1 Natural Language Dates
**Complexity:** Low
**Status:** Not implemented

- Parse "next Tuesday", "in 2 weeks", "EOD Friday"
- Convert to ISO dates for frontmatter
- Support relative dates ("tomorrow", "next month")

**Why nice-to-have:** Users can type "2026-02-15" if needed. Convenience, not necessity.

**Dependencies:** Date parsing library (dateutil, parsedatetime)

---

#### 3.2 Rich Media Handling
**Complexity:** Medium
**Status:** Not implemented

- Extract images/attachments from Slack
- Download and store in vault `_attachments/` folder
- Embed in markdown with `![]()`
- Handle file size limits

**Why nice-to-have:** Text captures are 90% of usage. Images add complexity.

**Dependencies:**
- Slack file download API
- Storage management
- Obsidian asset handling

---

#### 3.3 Smart Filename Generation
**Complexity:** Low
**Status:** ✓ Partially implemented (basic kebab-case)

- Generate memorable filenames from content
- Avoid generic names like "idea-123"
- Use dates for temporal notes
- Deduplicate intelligently

**Why nice-to-have:** Filenames matter for Obsidian graph view, but users can rename in vault.

**Enhancement opportunities:**
- Context-aware naming (e.g., "meeting-sarah-q2-roadmap" vs "idea-automation")

---

#### 3.4 Template Support
**Complexity:** Medium
**Status:** ✓ Implemented (basic templates)

- Use different templates per destination type
- Support variables in templates
- Custom frontmatter schemas
- Template per domain or subject

**Why nice-to-have:** Default templates work. Power users want customization.

**Dependencies:**
- Template engine (Jinja2) or simple string replacement

---

#### 3.5 Bulk Operations
**Complexity:** Medium
**Status:** Not implemented

- Bulk reclassify (select multiple, move to new category)
- Bulk tag application
- Batch corrections via Slack thread
- "Undo last 5 classifications"

**Why nice-to-have:** Single-item corrections are sufficient for 95% of cases.

**Dependencies:**
- UI for selection (Slack interactive messages or Obsidian dashboard)

---

#### 3.6 Search Integration
**Complexity:** Medium
**Status:** Not implemented

- Search vault from Slack ("find notes about Sarah")
- Return snippets with links
- Full-text search across all notes
- Filter by domain/PARA/subject/date

**Why nice-to-have:** Obsidian's native search is excellent. Adding Slack search is redundant.

**Dependencies:**
- Full-text indexing (ripgrep, SQLite FTS)
- Slack command interface

---

#### 3.7 Voice Capture
**Complexity:** High
**Status:** Not implemented

- Voice message in Slack → transcription → classification
- Support voice notes from mobile
- Handle transcription errors gracefully

**Why nice-to-have:** Slack already supports voice messages. Transcription via Whisper API is feasible but adds complexity and latency.

**Dependencies:**
- Whisper API or local transcription
- Audio file download from Slack

---

### 4. Anti-Features (Deliberately NOT Building)

These are features we could build but shouldn't. They add complexity without commensurate value or violate core principles.

#### 4.1 Real-Time Sync
**Why anti-feature:** Event-driven with backlog processing is sufficient. Messages queue in Slack. Processing lag of 2-5 minutes is acceptable for a personal knowledge system.

**Cost if built:** Webhook infrastructure, public endpoint, SSL certificates, always-on server.

---

#### 4.2 Multi-User Support
**Why anti-feature:** Personal knowledge systems are inherently single-user. Multi-user = shared vaults = permissions = complexity explosion.

**Cost if built:** User management, permissions, conflict resolution, privacy boundaries.

---

#### 4.3 Custom LLM Training
**Why anti-feature:** Off-the-shelf models (Llama 3.2, Mistral) handle classification well. Custom training requires datasets, GPU infrastructure, ongoing maintenance.

**Cost if built:** Data pipeline, training infrastructure, model versioning, drift detection.

---

#### 4.4 iOS Native App (for Capture)
**Why anti-feature:** Slack's iOS app already handles mobile capture perfectly. Building a native app duplicates functionality for marginal UX gain.

**Cost if built:** Swift/SwiftUI development, App Store management, push notifications, background processing.

**Note:** The `ios/` folder exists for initial exploration, but Slack mobile is sufficient.

---

#### 4.5 Cloud Sync of State
**Why anti-feature:** Local-first principle. State lives on machine, vault syncs via Obsidian iCloud. Adding cloud state = privacy leak, sync conflicts, infrastructure costs.

**Cost if built:** Backend API, database, sync logic, conflict resolution, auth.

---

#### 4.6 Advanced Analytics
**Why anti-feature:** Daily digest and weekly review provide sufficient insight. Dashboards with graphs, heatmaps, time-tracking add visual polish but don't change behavior.

**Cost if built:** Data aggregation, visualization library, dashboard UI, query optimization.

---

#### 4.7 Integration with Other Note Apps (Notion, Roam, Logseq)
**Why anti-feature:** Obsidian's markdown + local files are universal. Supporting other formats = maintaining N integrations, each with breaking changes.

**Cost if built:** API adapters for each platform, schema translation, testing matrix explosion.

---

#### 4.8 Automatic Summarization of Every Capture
**Why anti-feature:** Daily digest already summarizes. Per-note summarization is redundant when original capture is <500 words.

**Cost if built:** LLM API costs per message, latency increase, prompts to maintain.

---

#### 4.9 Link Preview Generation
**Why anti-feature:** When URLs are pasted, extract title/description/image. This is eye candy. Obsidian already renders markdown links.

**Cost if built:** Web scraping, rate limiting, metadata extraction, storage.

---

## Classification Accuracy: What Works

Based on research into LLM classification for personal knowledge systems:

### What Makes Classification Accurate

1. **Clear category definitions**
   - Provide concrete examples in prompt
   - Define boundaries between categories
   - Use user's own language (not academic jargon)

2. **Context from vault**
   - Include list of existing projects/areas when classifying
   - Reference user's subject taxonomy
   - Show examples of similar notes (few-shot learning)

3. **Explicit signals in capture**
   - Prefixes: "project:", "idea:", "admin:"
   - Temporal markers: "due Friday", "next quarter" → suggests project
   - Tone: questions/speculation → ideas, concrete tasks → admin

4. **Multi-stage classification**
   - Stage 1: Domain (Personal/Work/Side Project)
   - Stage 2: PARA type (Projects/Areas/Resources/Archives)
   - Stage 3: Subject folder
   - Each stage narrows context for next

5. **Confidence calibration**
   - Don't just return 0.9 for everything
   - Low confidence when ambiguous → hold for review
   - Train on correction feedback (future enhancement)

### What Doesn't Work

1. **Too many categories** (>10)
   - Accuracy drops exponentially with category count
   - Users also struggle with >10 mental buckets

2. **Vague category names**
   - "Miscellaneous", "Other", "General" → dumping grounds

3. **No feedback loop**
   - If corrections don't inform future classifications, same mistakes repeat

4. **Single-shot classification**
   - Trying to determine domain + PARA + subject in one prompt = worse results than sequential classification

5. **Ignoring user corrections**
   - Users fix misclassifications, but system doesn't learn → frustration

---

## PARA-Specific Classification Challenges

### Projects vs Areas
**Challenge:** Both are work-related, but projects have end states.

**Signals for Projects:**
- Mentions deadline or timeline
- Phrased as noun + verb ("Website redesign", "Q2 planning")
- Has next action or milestone
- Temporary by nature

**Signals for Areas:**
- Ongoing responsibility ("Health", "Finances", "Team management")
- No end date
- Standards to maintain rather than goals to achieve

**Example ambiguity:**
- "Improve marketing" → Area (ongoing optimization)
- "Launch marketing campaign" → Project (has end state)

---

### Resources vs Archives
**Challenge:** Both are reference material.

**Signals for Resources:**
- Currently relevant
- Actively referenced
- Might need again

**Signals for Archives:**
- Completed project artifacts
- Historical records
- No longer active but worth keeping

**Default rule:** Classify as Resources. Archive is a manual action (user decides when something is truly done).

---

### Cross-Domain Ambiguity
**Challenge:** "Meeting with Sarah" could be Personal (friend), CCBH (colleague), or Just Value (client).

**Signals for domain:**
- Keywords: "client", "work", "team" → work domain
- Relationship context from existing vault (scan people/ folders)
- Time/location: "office", "Slack call" → work

**Fallback:** Prompt user to add domain prefix if ambiguous.

---

## Recommended Phasing

Based on complexity and dependencies:

### Phase 1: Foundation (Current)
- ✓ Message ingestion
- ✓ Basic 4-category classification
- ✓ Markdown creation
- ✓ Confirmation feedback
- ✓ Correction mechanism
- ✓ State management
- ✓ Error handling

### Phase 2: Intelligence (Current Milestone)
- ⏳ Dynamic vault scanning
- ⏳ PARA-aware classification
- ⏳ Multi-domain routing
- ⏳ Subject classification
- ⏳ Local LLM (Ollama)

### Phase 3: Polish
- Confidence thresholds with review queue
- Smart filename generation improvements
- Natural language date parsing
- Enhanced entity extraction (books, concepts)

### Phase 4: Learning
- Feedback loop from corrections
- Pattern detection in misclassifications
- Prompt tuning based on usage
- User-specific prompt customization

---

## Success Metrics

### Table Stakes Metrics
- **Uptime:** >99% (no missed messages due to system failure)
- **Feedback latency:** <30 seconds from Slack post to confirmation
- **Crash rate:** <1% of messages (rest go to dead letter queue)

### Differentiator Metrics
- **Classification accuracy:** >80% (measured by fix: rate)
- **Review queue size:** <5 items per day (low confidence holds)
- **Correction time:** <5 seconds (fix: command to confirmation)
- **Trust score:** Subjective, measured by user willingness to capture sensitive thoughts

### Anti-Metrics (Things We Don't Optimize For)
- Real-time latency (2-minute polling is fine)
- Multi-platform support (macOS only)
- Scalability to 1000s of users (single user)

---

## Competitive Landscape

### Search/Retrieval Tools
- **Guru:** Team knowledge base, Slack search integration
- **Tettra:** Wiki + Slack bot for Q&A
- **Notion AI:** Search across workspace

**Our differentiation:** We're capture-first, not search-first. These tools help teams find existing knowledge. We help individuals organize emergent thoughts.

---

### Auto-Documentation Tools
- **Donut:** Slack thread → knowledge base article
- **Slite:** Async team updates with AI summaries

**Our differentiation:** We're personal, they're team-focused. They optimize for broadcast (standup, updates). We optimize for individual capture.

---

### Personal Knowledge Tools
- **Mem:** AI-powered note-taking with automatic tagging
- **Reflect:** Daily notes with backlinks and AI search
- **Notion AI:** Personal workspace with AI writing assistant

**Our differentiation:** Local-first (Obsidian + Ollama) = privacy. PARA structure = GTD/BASB alignment. Slack integration = universal capture from any device.

---

## Key Takeaways

1. **Table stakes are higher than you think.** Users expect reliability, feedback, and correction mechanisms. These aren't nice-to-haves.

2. **PARA classification is the moat.** Most tools use tags or folders. Routing to Projects/Areas/Resources/Archives requires understanding temporal context and lifecycle. Hard to replicate.

3. **Transparency > Accuracy.** Users tolerate 80% accuracy if they can see reasoning, correct mistakes easily, and trust nothing is silently dropped.

4. **Dynamic vault scanning is critical.** Static categories break as vaults grow. Learning vocabulary from existing structure = classification improves over time.

5. **Local LLM is a differentiator.** Privacy-conscious users won't trust cloud APIs with personal thoughts. Ollama support = trust.

6. **Avoid feature creep.** Real-time sync, multi-user support, custom training, iOS app, cloud state = complexity explosion with marginal value.

7. **Daily digest is 90% of the value.** Capture is 10%. Surfacing patterns and surfacing stuck projects = actual productivity gain.

---

## Open Questions for Implementation

1. **Multi-stage vs single-stage classification?**
   - Single-stage: One prompt, returns domain + PARA + subject (simpler, faster)
   - Multi-stage: Three prompts, each narrows context (more accurate, slower, more costly)

2. **How many subjects is too many?**
   - Scanning vault might discover 50+ subjects. Do we:
     - Include all in prompt? (Token cost, accuracy drop)
     - Cluster into meta-subjects? (Health, Finance, Learning)
     - Use two-stage subject classification?

3. **Domain inference or explicit tagging?**
   - Infer domain from content (harder, more magic)
   - Require domain prefix ("Personal: idea about...") (easier, more manual)

4. **How to handle multi-domain notes?**
   - Example: "Idea for CCBH project that uses Just Value framework"
   - Primary domain (CCBH) with tags for others?
   - Duplicate note in multiple domains?
   - Pick one, user moves if wrong?

5. **Review queue UI?**
   - Slack interactive messages? (limited UI)
   - Obsidian dashboard? (requires opening vault)
   - Daily digest with one-click approve? (DM + buttons)

---

**End of Features Research**
**Next Steps:** Feed into requirements definition for milestone 2 (PARA + domain routing)
