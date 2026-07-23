# Product Requirements Document: Open Brain

**A Personal Cognitive Operating System**

**Version:** 0.1 (Draft)
**Author:** Richard
**Date:** March 4, 2026
**Status:** Draft — Pending review of assumptions and open questions

---

## 1. Executive Summary

Open Brain is a personal knowledge infrastructure that combines a human-authored Obsidian vault with a Supabase/Postgres persistence layer, connected to all AI tools via MCP. It applies four concepts from the AgentOS research paper—semantic slicing, perception alignment, drift detection, and cognitive synchronization—to create a system where every AI tool a solo developer uses shares a single, structured, semantically searchable knowledge base that the user fully owns and controls.

The system serves all domains simultaneously: venture capital research and due diligence (Just Value, RWJF/LMI funding), software development (Claude Code, agent workflows, app building), personal knowledge management (parenting, tutoring, meditation research), and organizational psychology work.

### Core Design Principles

1. **Human authorship boundary.** The user writes into the vault. Agents read from it and write outputs to a separated space. This prevents feedback loops where agents discover patterns in their own prior outputs.
2. **Agent-readable by default.** Every note is structured for both human comprehension and machine retrieval. Markdown is the universal format.
3. **Platform independence.** No single AI vendor owns the context. Any MCP-compatible client can read and search.
4. **Compounding value.** Every captured thought makes future retrieval smarter and cross-domain connections more likely.

---

## 2. Problem Statement

### 2.1 Current Pain Points

**Context fragmentation.** Knowledge is distributed across Claude.ai memory, ChatGPT memory, scattered markdown files, prior research documents, and ephemeral chat sessions. Switching between tools means re-explaining context. Starting a new session means starting from zero.

**No agent-readable memory.** Autonomous agents (Claude Code, OpenClaw) cannot access a structured representation of the user's projects, decisions, constraints, and relationships. This limits delegation to tasks that can be fully specified in a single prompt.

**No drift visibility.** There is no mechanism to compare stated priorities (e.g., "I'm focused on the RWJF funding meeting") against actual behavior patterns (e.g., spending 80% of time on agent system research). Misalignment between intention and action compounds silently.

**Context window waste.** Significant cognitive bandwidth is spent on context transfer—explaining background, constraints, and prior decisions—rather than on the actual reasoning task. This is the human-scale version of the AgentOS paper's observation that treating context as a monolithic block is the root cause of system failures.

### 2.2 What Success Looks Like

A new Claude Code session on any project can be loaded with full relevant context in under 30 seconds via a single command. Any AI tool (Claude.ai, ChatGPT, Cursor) can search the user's complete knowledge base semantically via MCP. Weekly drift reports surface misalignment between stated priorities and actual activity. Cross-domain pattern detection surfaces connections the user hasn't explicitly made (e.g., a concept from organizational psychology research that applies to Just Value's underwriting approach).

---

## 3. Architecture

### 3.1 System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    HUMAN AUTHORING LAYER                 │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Obsidian Vault (Local)              │    │
│  │                                                  │    │
│  │  /domains/       ← Domain-specific knowledge     │    │
│  │  /projects/      ← Active project context files  │    │
│  │  /people/        ← Relationship notes            │    │
│  │  /decisions/     ← Decision log with rationale   │    │
│  │  /daily/         ← Daily notes & reflections     │    │
│  │  /hypotheses/    ← Confidence-rated theories     │    │
│  │                                                  │    │
│  │  /agent-outputs/ ← WRITE-ONLY zone for agents   │    │
│  │  (Human reviews, promotes to vault as needed)    │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │                               │
│                    Obsidian CLI                          │
│                    (backlinks, graph structure)          │
└─────────────────────────┼───────────────────────────────┘
                          │
              ┌───────────▼───────────┐
              │    SYNC / EMBED LAYER │
              │                       │
              │  Edge Function:       │
              │  • Extract metadata   │
              │  • Generate vectors   │
              │  • Classify tier      │
              │  • Store structured   │
              └───────────┬───────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                 PERSISTENCE LAYER (L3)                   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │         Supabase / Postgres + pgvector           │    │
│  │                                                  │    │
│  │  thoughts        (raw content + embeddings)      │    │
│  │  graph_edges     (backlink relationships)        │    │
│  │  context_tiers   (L1/L2/L3 classification)       │    │
│  │  drift_log       (intention vs behavior tracking)│    │
│  │  sync_state      (last-known state per tool)     │    │
│  └──────────────────────┬──────────────────────────┘    │
│                         │                               │
└─────────────────────────┼───────────────────────────────┘
                          │
              ┌───────────▼───────────┐
              │   RETRIEVAL LAYER     │
              │                       │
              │  MCP Server:          │
              │  • Semantic search    │
              │  • Context loader     │
              │  • Perception align   │
              │  • Drift report       │
              │  • Sync check         │
              └───────────┬───────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │  Claude  │   │  Claude  │   │  ChatGPT │
    │  Code    │   │  .ai     │   │  Cursor  │
    └──────────┘   └──────────┘   └──────────┘
```

### 3.2 The Authorship Boundary (Critical Design Decision)

The vault is divided into two zones with a hard enforcement rule:

**Human-authored zone** (`/domains/`, `/projects/`, `/people/`, `/decisions/`, `/daily/`, `/hypotheses/`): Only the user writes here. Agents can read all files in this zone. This ensures that when agents detect patterns, they are detecting patterns in the user's thinking, not in prior agent outputs.

**Agent-output zone** (`/agent-outputs/`): Agents write analysis, reports, idea generation, and recommendations here. The user reviews agent outputs and manually promotes any content worth preserving into the human-authored zone, rewriting it in their own voice and understanding. This is the "graduation" process.

**Rationale (from Vin's insight):** If agents write directly into the knowledge base that other agents read from, the system develops feedback loops. Patterns detected become patterns in the agent's own language rather than the user's thinking. The authorship boundary prevents this contamination while still allowing agents to produce useful output.

### 3.3 AgentOS-Inspired Subsystems

#### 3.3.1 Semantic Slicing — Tiered Memory Hierarchy

Every note in the vault is classified into a retrieval tier based on relevance and recency. This is the practical implementation of AgentOS's L1/L2/L3 memory hierarchy.

**Tier 1 — Active Context (L1 equivalent)**
Notes that should be loaded into every relevant session automatically. These are the "always-on" context files.

Contents: Active project context files (e.g., `just-value-context.md`, `rwjf-funding-prep.md`), current weekly priorities, active hypotheses with high confidence ratings, today's daily note.

Loading mechanism: The `/context` command in Claude Code reads all T1 files plus their immediate backlinks. This is the equivalent of paging semantic slices into the model's active attention span.

**Tier 2 — Deep Context (L2 equivalent)**
Notes that are relevant to specific domains or projects but not needed in every session. Retrieved on demand via semantic search or explicit reference.

Contents: Domain knowledge files, decision logs from the past 90 days, person notes for active collaborators, research summaries, prior project retrospectives.

Loading mechanism: Semantic search via MCP, or explicit file reference in Claude Code. The retrieval function summarizes and structures results before returning them (Perception Alignment — see 3.3.2).

**Tier 3 — Cold Storage (L3 equivalent)**
Historical notes, archived projects, old research. Searchable but never auto-loaded.

Contents: Completed project archives, historical decision logs, old daily notes beyond 90 days, reference material.

Loading mechanism: Explicit semantic search only. Results are compressed summaries, not full notes.

**Tier classification** is determined by a combination of:
- Recency (notes from the last 7 days default to T1, 8-90 days to T2, 90+ to T3)
- Explicit tagging (`#active`, `#archive`)
- Backlink density (highly connected notes are promoted)
- Domain relevance to declared current priorities

#### 3.3.2 Perception Alignment — Structured Retrieval Formatting

When context is retrieved from the database and delivered to an AI tool via MCP, it is not returned as raw note dumps. Instead, the retrieval layer performs **Perception Alignment**: formatting and compressing the results to fit the current task's semantic requirements.

**Implementation:**

The MCP server exposes a `search_brain` tool that accepts a query and a `task_context` parameter. The retrieval function:

1. Performs semantic search across the vector database
2. Retrieves matching notes with their tier classification and backlink graph
3. Compresses results into a structured format:
   - **For T1 results:** Full content, preserving structure and backlinks
   - **For T2 results:** Summary paragraph + key decisions/facts + link to full note
   - **For T3 results:** One-sentence summary + date + link
4. Orders results by relevance to the `task_context`, not just vector similarity
5. Includes a "graph context" section showing how retrieved notes connect to each other and to active projects

**Example retrieval response format:**

```markdown
## Brain Search: "lending regulations state compliance"

### Active Context (T1)
**just-value-regulatory-framework.md** (updated 2 days ago)
[Full content of the note, including backlinks to state-specific files]

### Related Knowledge (T2)
**state-lending-regs-ohio.md** (updated 3 weeks ago)
Summary: Ohio requires $50K surety bond, 25% net worth requirement...
Key decision: Decided to prioritize OH after AL and GA based on market size.
Connected to: just-value-market-analysis.md, lending-ops-blueprint.md

### Historical (T3)
- **alt-lending-research-dec2025.md**: Early-stage research on alternative lending
  regulatory landscape across 12 states. (Dec 2025)

### Graph Context
just-value-regulatory-framework → links to → 6 state-specific files, 
lending-ops-blueprint, rwjf-funding-prep
```

#### 3.3.3 Drift Detection — Intention vs. Behavior Tracking

**Purpose:** Surface misalignment between declared priorities and actual behavior before it compounds. This is the human-scale implementation of AgentOS's cognitive drift monitoring.

**Mechanism:**

The user declares priorities in a `priorities.md` file in the vault root, structured as:

```markdown
## Current Priorities (Week of March 3, 2026)
1. RWJF funding meeting prep (target: March 25)
2. Just Value operational blueprint finalization
3. [Child's name] second grade readiness assessment
4. Open Brain system build-out

## Confidence Ratings
- RWJF deal closes: 0.6 (need stronger narrative on de-biased underwriting)
- LMI credit facility: 0.4 (dependent on RWJF guarantee)
- Second grade transition: 0.8 (on track with current plan)
```

The system tracks:
- **Daily note topics:** What domains the user actually writes about each day
- **Claude Code session topics:** What projects sessions are opened for (inferred from `/context` loads and file references)
- **Time distribution:** Approximate time allocation across domains based on session length and note volume

**The `/drift` command** (run weekly or on-demand) generates a report:

```markdown
## Drift Report: Feb 24 - March 3, 2026

### Declared vs. Actual Allocation
| Priority | Declared Rank | Actual Time % | Status |
|----------|--------------|---------------|--------|
| RWJF prep | 1 | 15% | ⚠️ UNDER-INVESTED |
| JV ops blueprint | 2 | 22% | ✅ On track |
| Education planning | 3 | 8% | ✅ Proportional |
| Open Brain build | 4 | 40% | ⚠️ OVER-INDEXED |
| Agent/AI research | (undeclared) | 15% | 🔍 UNLISTED |

### Flags
- RWJF meeting is in 22 days. Current preparation rate suggests
  insufficient coverage of regulatory compliance narrative.
- "Agent/AI research" is consuming significant time but is not
  a declared priority. Promote to priorities list or reduce.
- Confidence rating on RWJF (0.6) has not changed in 2 weeks
  despite being listed as top priority. Stale assessment?

### Suggested Rebalance
[Specific recommendations based on deadline proximity and current gaps]
```

#### 3.3.4 Cognitive Synchronization — Cross-Tool State Coherence

**Purpose:** Ensure that all AI tools share the same version of the user's context, preventing the "five sticky notes on five desks" problem.

**Mechanism:**

The `sync_state` table in Supabase tracks the last-known context state per tool:

```
| tool        | last_sync       | context_version | notes_loaded      |
|-------------|-----------------|-----------------|-------------------|
| claude_code | 2026-03-04 10:30| v47             | [list of T1 files]|
| claude_ai   | 2026-03-04 09:15| v46             | [list of T1 files]|
| chatgpt     | 2026-03-03 16:00| v44             | [list of T1 files]|
```

When a new session is opened in any tool:
1. The MCP `context_load` function checks the current vault version against the tool's last sync
2. If there's a delta, it provides a "sync brief" — a summary of what changed since the tool's last session
3. This ensures the user doesn't have to re-explain recent decisions or context shifts

**Sync brief example:**

```markdown
## Context Update (since your last ChatGPT session, March 3)

### New/Changed (3 items):
- Updated RWJF prep with revised de-biasing methodology narrative
- New decision: Prioritize Alabama market entry before Georgia
- New person note: [Contact] from LMI, met at conference

### Priority Shift:
- Open Brain build promoted from #4 to #4 (unchanged)
- RWJF prep flagged as under-invested in latest drift report
```

---

## 4. Vault Structure

```
open-brain-vault/
├── CLAUDE.md                    # Claude Code instructions and command definitions
├── priorities.md                # Current declared priorities + confidence ratings
├── README.md                    # Vault structure guide
│
├── domains/                     # Domain knowledge (long-lived)
│   ├── venture-capital/
│   ├── fintech-lending/
│   ├── organizational-psychology/
│   ├── data-science/
│   ├── education/
│   ├── mindfulness-research/
│   └── ai-agents/
│
├── projects/                    # Active project context files
│   ├── just-value/
│   │   ├── just-value-context.md        # Master context file (T1)
│   │   ├── rwjf-funding-prep.md         # Funding meeting prep (T1)
│   │   ├── lmi-credit-facility.md
│   │   ├── ops-blueprint.md
│   │   ├── regulatory-framework.md
│   │   └── market-analysis/
│   ├── open-brain/
│   │   ├── open-brain-context.md
│   │   └── prd.md
│   ├── education-planning/
│   │   ├── second-grade-readiness.md
│   │   └── tutoring-curriculum/
│   └── _archived/                       # Completed projects (T3)
│
├── people/                      # Relationship notes
│   ├── professional/
│   └── personal/
│
├── decisions/                   # Decision log with rationale
│   ├── 2026-03/
│   └── _template.md
│
├── daily/                       # Daily notes (Obsidian daily notes plugin)
│   └── 2026-03-04.md
│
├── hypotheses/                  # Confidence-rated theories
│   ├── active/
│   └── resolved/
│
└── agent-outputs/               # AGENTS WRITE HERE ONLY
    ├── drift-reports/
    ├── idea-generation/
    ├── pattern-analysis/
    ├── search-results/
    └── sync-briefs/
```

---

## 5. Claude Code Commands

These are defined in `CLAUDE.md` at the vault root and invoked as slash commands in Claude Code sessions.

### 5.1 Context Management

| Command | Purpose | Reads |
|---------|---------|-------|
| `/context` | Load full active context for a session | All T1 files + backlinks + priorities.md |
| `/context [project]` | Load project-specific context | Project context file + related T1/T2 files |
| `/sync` | Show what changed since last session in this tool | sync_state table + recent vault changes |

### 5.2 Capture

| Command | Purpose | Writes To |
|---------|---------|-----------|
| `/decision [description]` | Log a decision with rationale | /decisions/YYYY-MM/ |
| `/hypothesis [claim] [confidence]` | Record a theory with confidence rating | /hypotheses/active/ |
| `/note [person] [content]` | Capture a person note | /people/ |
| `/daily` | Open today's daily note for writing | /daily/ |

### 5.3 Analysis (AgentOS-Informed)

| Command | Purpose | Output Location |
|---------|---------|-----------------|
| `/drift` | Compare declared priorities vs actual behavior (30 days) | /agent-outputs/drift-reports/ |
| `/emerge` | Surface latent ideas the vault implies but never states | /agent-outputs/pattern-analysis/ |
| `/connect [domain-a] [domain-b]` | Find bridges between two domains using vault link graph | /agent-outputs/pattern-analysis/ |
| `/trace [concept]` | Track how an idea has evolved over time across the vault | /agent-outputs/pattern-analysis/ |
| `/ideas` | Deep vault scan with cross-domain pattern detection | /agent-outputs/idea-generation/ |
| `/challenge [belief]` | Pressure test a belief using vault history and contradictions | /agent-outputs/pattern-analysis/ |
| `/graduate` | Scan daily notes for ideas worth promoting to standalone notes | /agent-outputs/ (suggestions only; user promotes manually) |

### 5.4 Operations

| Command | Purpose |
|---------|---------|
| `/today` | Morning review: calendar + tasks + daily notes → prioritized plan |
| `/close` | End of day: extract action items, surface connections, update drift log |
| `/weekly` | Weekly synthesis: cluster by topic, find unresolved items, detect patterns |

---

## 6. MCP Server Tools

The MCP server exposes these tools to any compatible AI client:

| Tool | Parameters | Returns |
|------|-----------|---------|
| `search_brain` | `query` (string), `task_context` (string, optional), `tier_filter` (T1/T2/T3/all) | Perception-aligned results with graph context |
| `load_context` | `project` (string, optional) | T1 context bundle + sync brief |
| `list_recent` | `days` (int, default 7), `domain` (string, optional) | Recent captures organized by domain |
| `get_drift` | `days` (int, default 30) | Drift report comparing priorities vs activity |
| `get_priorities` | — | Current priorities.md content + confidence ratings |
| `capture_thought` | `content` (string), `domain` (string, optional) | Stores in Supabase with embedding + metadata |
| `get_graph` | `node` (string), `depth` (int, default 2) | Backlink graph around a specific note |
| `get_sync_state` | `tool` (string) | Last sync time + delta summary |

---

## 7. Data Model (Supabase/Postgres)

### 7.1 Core Tables

**`thoughts`** — Primary content store with vector embeddings

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| content | text | Raw note content |
| embedding | vector(1536) | OpenAI or local embedding |
| vault_path | text | Corresponding Obsidian file path |
| domain | text | Classified domain (vc, fintech, education, etc.) |
| tier | enum (T1, T2, T3) | Current retrieval tier |
| note_type | text | decision, hypothesis, person, daily, domain, project |
| confidence | float | For hypotheses: 0.0-1.0 confidence rating |
| people | text[] | Extracted person references |
| tags | text[] | Obsidian tags |
| backlinks | text[] | Connected note paths |
| created_at | timestamptz | Creation time |
| updated_at | timestamptz | Last modification |

**`graph_edges`** — Explicit relationships (mirrors Obsidian backlinks)

| Column | Type | Description |
|--------|------|-------------|
| source_path | text | Source note vault path |
| target_path | text | Target note vault path |
| edge_type | text | backlink, tag, domain, manual |
| created_at | timestamptz | When link was created |

**`drift_log`** — Behavior tracking for drift detection

| Column | Type | Description |
|--------|------|-------------|
| date | date | Day |
| domain | text | Domain of activity |
| activity_type | text | note, session, decision, search |
| duration_estimate | interval | Estimated time spent |
| tool | text | Which AI tool was used |

**`sync_state`** — Cross-tool synchronization tracking

| Column | Type | Description |
|--------|------|-------------|
| tool | text | Tool identifier (claude_code, claude_ai, chatgpt, cursor) |
| last_sync | timestamptz | Last context load time |
| context_version | int | Vault version counter at last sync |
| notes_loaded | text[] | Which T1 files were loaded |

**`priorities`** — Structured priority tracking (mirrors priorities.md)

| Column | Type | Description |
|--------|------|-------------|
| priority | text | Priority description |
| rank | int | Declared importance ranking |
| confidence | float | Confidence rating (0.0-1.0) |
| deadline | date | Target date if applicable |
| domain | text | Associated domain |
| active | boolean | Currently active |
| updated_at | timestamptz | Last update |

---

## 8. Sync Pipeline

### 8.1 Vault → Database Sync

A sync process runs on-demand (via Claude Code command) or on a schedule:

1. **Scan vault** for new or modified `.md` files since last sync
2. **Parse** each file: extract frontmatter, backlinks, tags, people references
3. **Classify tier** based on recency, tags, backlink density, and domain relevance to current priorities
4. **Generate embedding** via API call (OpenAI `text-embedding-3-small` or local alternative)
5. **Upsert** to Supabase `thoughts` table
6. **Update** `graph_edges` table with any new or changed backlinks
7. **Increment** vault version counter

### 8.2 Quick Capture → Database (Bypass Vault)

For rapid capture from Slack or other messaging apps, thoughts can be sent directly to Supabase via edge function without first writing to the Obsidian vault. These are flagged as `vault_path: null` and can be reviewed and optionally promoted to vault notes during the `/weekly` review.

### 8.3 Database → Vault (Reverse Sync — Optional)

Agent outputs stored in Supabase can be synced to `/agent-outputs/` in the vault for review. This is one-directional: the agent-outputs directory is never synced back to the database as human-authored content.

---

## 9. Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Goal:** Obsidian vault set up with structure, Claude Code commands for context loading and capture, basic sync to Supabase.

- [ ] Create vault with directory structure from Section 4
- [ ] Write `CLAUDE.md` with command definitions
- [ ] Migrate existing Claude.ai memory into vault notes
- [ ] Migrate existing ChatGPT memory into vault notes
- [ ] Migrate existing research files and markdown notes
- [ ] Set up Supabase project with schema from Section 7
- [ ] Build initial sync script (vault → database)
- [ ] Implement `/context`, `/context [project]`, `/daily`, `/decision` commands

### Phase 2: MCP + Retrieval (Week 3-4)

**Goal:** MCP server operational, any AI tool can search and retrieve context with perception alignment.

- [ ] Build MCP server with `search_brain` and `load_context` tools
- [ ] Implement perception alignment formatting in retrieval responses
- [ ] Implement tier-aware retrieval (T1 full content, T2 summary, T3 one-liner)
- [ ] Connect Claude.ai to MCP server
- [ ] Connect ChatGPT to MCP server
- [ ] Connect Cursor to MCP server
- [ ] Implement `capture_thought` for quick capture from any tool
- [ ] Implement sync state tracking

### Phase 3: Analysis Commands (Week 5-6)

**Goal:** Full analysis toolkit operational — drift, emerge, connect, trace, ideas.

- [ ] Implement `/drift` with drift_log tracking and reporting
- [ ] Implement `/emerge` (latent pattern detection across vault)
- [ ] Implement `/connect` (cross-domain bridge finding via graph)
- [ ] Implement `/trace` (idea evolution tracking over time)
- [ ] Implement `/ideas` (comprehensive idea generation from vault context)
- [ ] Implement `/challenge` (belief pressure testing)
- [ ] Implement `/graduate` (daily note idea extraction)
- [ ] Implement `/today`, `/close`, `/weekly` operational commands

### Phase 4: Refinement (Week 7-8)

**Goal:** Tune tier classification, sync reliability, drift detection accuracy. Add Slack/messaging quick capture.

- [ ] Set up Slack integration for quick capture
- [ ] Tune tier classification rules based on actual usage patterns
- [ ] Build weekly review dashboard (vault stats, drift trends, connection density)
- [ ] Implement automatic tier reclassification based on access patterns
- [ ] Stress test sync pipeline with full vault
- [ ] Document the system for future reference

---

## 10. Open Questions and Assumptions

### Assumptions (To Be Validated)

1. **Embedding model:** Defaulting to OpenAI `text-embedding-3-small` for cost efficiency. May switch to local model if privacy concerns outweigh convenience.
2. **Sync frequency:** On-demand sync is sufficient for Phase 1. May need automated sync (file watcher) if manual sync becomes friction.
3. **Tier boundaries:** 7-day / 90-day thresholds for T1/T2/T3 are initial guesses. Will need tuning based on actual retrieval patterns.
4. **Agent-output boundary:** Assuming strict separation is correct. May relax to allow agents to create draft notes in a staging area within the human zone if the review bottleneck becomes too high.

### Open Questions

1. **Embedding cost budget:** At ~20 notes/day with `text-embedding-3-small`, embedding costs are negligible (~$0.02/month). But bulk migration of existing notes could be a one-time spike. Acceptable?
2. **Obsidian plugin ecosystem:** Should the system use existing Obsidian plugins (e.g., Obsidian Git for vault backup, Templater for note templates) or minimize dependencies?
3. **Voice capture:** Should the system support voice-to-text capture (e.g., via MacWhisper or phone dictation → Slack → edge function)? This would dramatically lower capture friction.
4. **Multi-vault vs single vault:** The current design assumes a single vault for all domains. Would separate vaults for professional vs. personal contexts be preferable for privacy/compartmentalization?
5. **Child's educational content:** Should tutoring and mentoring materials (curriculum notes, student progress tracking) live in this vault or in a separate system given that it involves minors?
6. **Backup strategy:** What is the backup and versioning strategy for the vault? Git-based versioning? Supabase automatic backups?

---

## 11. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Context load time | < 30 seconds for full T1 load | Time from `/context` to ready state |
| Re-explanation rate | < 1 per week | Instances where user must re-explain context an AI should already have |
| Cross-tool retrieval parity | Same answer quality regardless of tool | Qualitative assessment over first month |
| Drift detection accuracy | Flags genuine misalignment > 80% of the time | Weekly review of drift reports |
| Weekly capture volume | 15-25 notes/week across all domains | Database count |
| Cross-domain connections surfaced | 2-3 novel connections per week | `/ideas` and `/emerge` output review |
| Time to new tool adoption | < 10 minutes to connect a new AI tool | Time from "I want to try X" to X having full context |

---

## 12. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Capture habit doesn't stick | High | Critical — system is useless without input | Start with one domain only despite "all domains" goal; build habit before breadth |
| Over-engineering before using | High | High — weeks spent building instead of capturing | Phase 1 is deliberately minimal; capture starts day 1 |
| Tier misclassification degrades retrieval | Medium | Medium — wrong context loaded, wasted tokens | Conservative defaults (promote to T1 too easily rather than too rarely); tune with usage |
| Supabase free tier limits hit | Low | Medium — need to migrate or pay | Free tier is generous (500MB DB, 1GB storage); monitor usage |
| Privacy exposure via MCP | Medium | High — sensitive VC/personal data exposed | MCP server runs locally; Supabase Row Level Security enabled; review what tools can access |
| Agent output feedback loops | Low (with boundary) | High — corrupts pattern detection | Strict authorship boundary; agent-outputs never synced as human content |
| Vault becomes overwhelming | Medium | Medium — too many notes, hard to maintain | Weekly `/graduate` + `/weekly` review as maintenance ritual; aggressive archiving |

---

## Appendix A: Relationship to Source Concepts

| Concept | AgentOS Paper | Open Brain Video | Obsidian + Claude Code | This PRD |
|---------|--------------|-----------------|----------------------|----------|
| Memory hierarchy | L1/L2/L3 with S-MMU | Postgres + pgvector | Context files + backlinks | Tiered vault + DB with classification |
| Context as addressable space | Semantic slicing via attention | Vector embeddings | Obsidian backlink graph | Both: graph structure + embeddings |
| Tool isolation | Reasoning Interrupt Cycle | MCP protocol | Obsidian CLI + Claude Code | MCP server + authorship boundary |
| Drift management | Cognitive Sync Pulses | N/A | `/drift` command | Drift log + weekly reporting |
| Retrieval formatting | Perception Alignment | Edge function metadata | N/A | Tier-aware structured retrieval |
| Cross-system coherence | Global State Reconciliation | Single brain, every AI | N/A | Sync state tracking + sync briefs |
| Contamination prevention | N/A | N/A | No agent writes to vault | Authorship boundary + agent-outputs zone |
