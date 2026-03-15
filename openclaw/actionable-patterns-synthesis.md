# Actionable OpenClaw Patterns: Synthesis Guide

**Purpose**: Extract actionable patterns from both NLW's verified implementation and the aspirational guide, clearly marking what's proven vs. theoretical.

---

## Pattern Classification System

- ✅ **PROVEN**: Verified from NLW's actual implementation
- 🔬 **EXPERIMENTAL**: From guide but not verified in NLW's system
- 🎯 **RECOMMENDED**: High value-to-effort ratio based on NLW's experience
- ⚠️ **CAUTION**: NLW tried this and found issues
- 📋 **FUTURE**: NLW plans this for Phase 2

---

## Table of Contents

1. [Infrastructure Patterns](#infrastructure-patterns)
2. [Agent Architecture Patterns](#agent-architecture-patterns)
3. [Agent Types & Use Cases](#agent-types--use-cases)
4. [File Structure Patterns](#file-structure-patterns)
5. [Automation Patterns](#automation-patterns)
6. [Communication Patterns](#communication-patterns)
7. [Quality & Reliability Patterns](#quality--reliability-patterns)
8. [Security Patterns](#security-patterns)
9. [Development Workflow Patterns](#development-workflow-patterns)
10. [Monitoring & Observability Patterns](#monitoring--observability-patterns)

---

## Infrastructure Patterns

### Pattern: Always-On Dedicated Host
**Status**: ✅ PROVEN | 🎯 RECOMMENDED

**Implementation**:
```
Hardware: Mac Mini (or any always-on computer)
Network: Tailscale for secure remote access
Access: From any device (desktop, laptop, mobile)
```

**Why it works** (NLW):
- Clean environment for incremental access grants
- Available 24/7 for persistent agents
- Remote access from anywhere

**Alternative** (NLW):
- Any old laptop works
- Doesn't require powerful resources

**Cost**: Mac Mini ~$600 one-time (optional)

---

### Pattern: Secure Remote Access via Tailscale
**Status**: ✅ PROVEN | 🎯 RECOMMENDED

**Implementation**:
```bash
# On host machine
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up

# On client machines
tailscale up
# Access via Tailscale IP, no public ports
```

**Benefits**:
- Zero Trust identity-based connectivity
- No public port exposure
- Access from phone, laptop, anywhere
- VPN-free secure connections

**NLW's usage**: Access Mac Mini from iMac, MacBook Air, iPhone

---

### Pattern: Container Isolation (Optional)
**Status**: 🔬 EXPERIMENTAL (from guide, not mentioned by NLW)

**Options**:
1. **Docker** (OpenClaw default)
   - Process-level containers
   - Easier setup
   - Less isolation

2. **Incus** (Guide recommendation)
   - System-level containers
   - Stronger isolation
   - UID mapping built-in

**When to use**: Phase 2, when agents get broader system access

---

## Agent Architecture Patterns

### Pattern: The Five Core Files
**Status**: ✅ PROVEN (NLW explicitly describes)

**Structure**:
```
agent-name/
├── IDENTITY.md      # Name, emoji, one-line description
├── SOUL.md          # Personality, behavior, character sheet
├── AGENTS.md        # Operating instructions, employee handbook
├── USER.md          # Everything about you (name, preferences, style)
├── TOOLS.md         # Access permissions (paths, APIs, services)
├── MEMORY.md        # Long-term curated memories
└── HEARTBEAT.md     # Autopilot instructions
```

**Purpose of each**:
- **IDENTITY.md**: Who the agent is
- **SOUL.md**: How the agent thinks and behaves
- **AGENTS.md**: How agents should operate in general
- **USER.md**: What the agent knows about you
- **TOOLS.md**: What the agent can access
- **MEMORY.md**: What the agent should remember
- **HEARTBEAT.md**: What to do when unsupervised

---

### Pattern: Progressive Access Philosophy
**Status**: ✅ PROVEN | 🎯 RECOMMENDED

**Principle**: Start locked down, open up incrementally

**NLW's approach**:
```
Phase 1: Limited access
- No email monitoring
- No extensive system access
- Careful skill vetting
- Simple interactions

Phase 2: Coordinated access (planned)
- System integrations
- Inter-agent communication
- Broader tool access
```

**Key quote**:
> "Fresh environment where I could very incrementally give it access to the systems that I wanted to give it access to without fear of it bleeding into other things"

---

### Pattern: Agent Specialization by Capability Type
**Status**: ✅ PROVEN | 🎯 RECOMMENDED

**Framework**: Match agents to these capability needs

| Capability | When to Use | NLW Example |
|------------|-------------|-------------|
| **Mobile management** | Tasks you want to handle from anywhere | Task agent, PM agents |
| **Persistent work** | 24/7 operations, around-the-clock | Research agents |
| **Scheduled work** | Time-triggered tasks | PM morning briefs (8 AM) |
| **On-demand work** | Interactive, conversational | Task agent, builder |

**Decision process**:
1. List all your work categories
2. Ask: Would this benefit from mobile/persistent/scheduled/on-demand?
3. Build agent if strong match exists

---

## Agent Types & Use Cases

### Pattern: Interactive Task Management Agent
**Status**: ✅ PROVEN | 🎯 RECOMMENDED (NLW's most used)

**Use case**: Natural language to-do list management

**NLW's structure**:
```
Lists:
- Today
- This week
- Next week
- Future
- Icebox (uncertain timing)
```

**Workflow**:
```
Think of task → Tell Telegram → Instant update
```

**Why it works**:
- Maps to your brain's natural organization
- Mobile updates anytime
- No context switching to Notion/Apple Notes

**ROI**: Highest value for lowest effort

---

### Pattern: Specialized Research Agents
**Status**: ✅ PROVEN | 🎯 RECOMMENDED

**Use case**: 24/7 information gathering in narrow domain

**NLW's implementation**:
```
Agent: Maturity Maps Researcher
Domain: AI maturity across organizations
Sources: Studies, surveys, research papers
Output: Proposals for framework updates

Agent: Opportunity Radars Researcher
Domain: AI use cases by business function
Sources: Case studies, implementations
Output: Use case categorization proposals
```

**Pattern structure**:
1. Define narrow research domain
2. Specify source types
3. Set output format (proposals, summaries, etc.)
4. Quality calibration needed

**Quality calibration steps**:
1. Review initial outputs
2. Teach good vs. mediocre source distinction
3. Refine proposal writing standards
4. Iterate over 1-2 weeks

---

### Pattern: Project Manager Agents (Phase 1)
**Status**: ✅ PROVEN

**Current state**: "Glorified to-do list managers" (NLW)

**Implementation**:
```
One PM per major project/initiative

Schedule:
- 8 AM: Status update from previous day
- 5 PM: End-of-day check-in

Features:
- Brain dump repository
- Harassment mode ("send skull emojis until I decide")
- Context segmentation
```

**NLW's honest assessment**: "Personal assistant without access to a phone or email"

**Phase 2 vision** (📋 FUTURE):
- Interact with external systems (Slack, email)
- Coordinate with other people's agents
- True project management vs. task lists

---

### Pattern: Chief of Staff Agent
**Status**: ✅ PROVEN (built but idle) | 📋 FUTURE (pending PM Phase 2)

**Purpose**: Triage across multiple PM agents

**When to activate**: After PM agents reach Phase 2 and have system access

**Function**:
- Aggregate signals from all PMs
- Prioritize what's truly important
- Surface critical decisions
- Morning briefing of key focuses

**Current status**: Sitting idle until PM coordination exists

---

### Pattern: Builder Agent
**Status**: ✅ PROVEN | ⚠️ CAUTION (NLW's least used)

**Original intent**: On-the-go coding + overnight builds

**Reality**:
- Most coding projects are iterative
- Require constant feedback
- Can't run on autopilot
- Works better with Replit/Lovable/Claude Code

**When it works**:
- Discrete, well-defined tasks
- Scripts and utilities
- One-off automation

**When it doesn't**:
- Complex feature development
- UI/design iteration
- Projects requiring design decisions

**Lesson**: Match to your actual workflow, not ideal workflow

---

### Pattern: Finance/Cost Tracking Agent
**Status**: 🔬 EXPERIMENTAL (in NLW's Claude Project files but not mentioned in video)

**Potential use case**:
- Track API costs across agents
- Budget monitoring
- Cost optimization recommendations

**File evidence**: `WHITTY_PODCAST_FINANCE_AGENT.md` in Claude Project

**Status**: Unknown if implemented

---

## File Structure Patterns

### Pattern: Minimal Task Agent Files
**Status**: ✅ PROVEN (NLW Tasks)

**Structure**:
```
nlw-tasks/
├── IDENTITY.md
├── SOUL.md
├── AGENTS.md
├── USER.md
├── TOOLS.md
├── MEMORY.md
├── HEARTBEAT.md
└── lists/
    ├── today.md
    ├── this-week.md
    ├── next-week.md
    ├── future.md
    └── icebox.md
```

**Simplicity**: Focus on core files, simple list structure

---

### Pattern: Research Agent Output Structure
**Status**: ✅ PROVEN (NLW research agents)

**NLW's approach** (implied):
```
research-agent/
├── [core files]
├── findings/
│   ├── maturity-maps/
│   │   ├── 2026-02-10-study-xyz.md
│   │   └── proposals/
│   │       └── 2026-02-11-systems-integration-update.md
│   └── opportunity-radars/
│       ├── 2026-02-09-use-case-abc.md
│       └── proposals/
│           └── 2026-02-10-marketing-radar-update.md
└── MEMORY.md  # Curated insights
```

**Key principle**: Proposals are the output, not just collection

---

### Pattern: Extended File Structure (from guide)
**Status**: 🔬 EXPERIMENTAL (not verified in NLW's system)

**Guide suggests**:
```
agent-name/
├── [core files above]
├── completed/        # Archive of done tasks
├── daily/            # Daily logs
├── WEEKLY/           # Weekly reviews
├── JOURNAL.md        # Activity log
├── STACK.md          # Tech stack
├── STORY.md          # Project narrative
├── VIBES.md          # Cultural guidelines
├── ICEBOX.md         # Future ideas
└── CONTENT_IDEAS.md  # Content planning
```

**Status**: Aspirational, not verified as needed

**Recommendation**: Start with core 7 files, add only if clear need

---

## Automation Patterns

### Pattern: Heartbeat System
**Status**: ✅ PROVEN | ⚠️ CAUTION (reliability issues)

**How it works**:
```markdown
# HEARTBEAT.md

## Check every 30 minutes

1. Review inbox for new research papers
2. Check if any proposals need follow-up
3. Scan for urgent matters

If nothing needs attention: Reply "HEARTBEAT_OK"
If something needs attention: Alert with context
```

**Configuration** (NLW):
- Default interval: 30 minutes
- If nothing to do: Silent (HEARTBEAT_OK)
- If needs attention: Sends notification

**Known issue** (NLW):
> "Heartbeats can be flaky. You will often find that for whatever reason, the agent just drops off for a while and you kind of have to reset it."

**Mitigation**: Plan to reset agents periodically

---

### Pattern: Cron-Based Scheduled Tasks
**Status**: ✅ PROVEN | 🎯 RECOMMENDED

**NLW's PM schedule**:
```
8:00 AM: Status update from previous day
5:00 PM: End-of-day check-in
```

**Use cases**:
- Morning briefings
- End-of-day summaries
- Weekly reviews
- Scheduled research sweeps

**vs. Heartbeat**:
- Heartbeat: Periodic checks (every 30 min)
- Cron: Specific times (8 AM, 5 PM)

---

### Pattern: Multi-Agent Coordination (NOT in NLW's system)
**Status**: 🔬 EXPERIMENTAL | 📋 FUTURE

**Vox's approach** (from screenshot 3, NOT NLW):
```
Agent 1: Research → Proposal
    ↓
Agent 2: Evaluate → Approved/Rejected
    ↓
Agent 3: Implementation → Execution
    ↓
Agent 4: Verification → Feedback
```

**NLW explicitly states he does NOT do this** (line 81-82):
> "I don't have a complex system where agents hand off to one another"

**What NLW has instead**:
- Shared context files
- Chief of Staff reads PM system files
- Manual coordination through him

**When to attempt**: Phase 2+, after mastering simple agents

---

## Communication Patterns

### Pattern: Telegram as Primary Interface
**Status**: ✅ PROVEN | 🎯 RECOMMENDED

**Why Telegram** (NLW):
- Mobile management
- On-the-go instructions
- Instant updates
- No context switching

**Workflow**:
```
Driving → Think of task → Voice message to Telegram → Agent updates
Gym → Remember something → Quick chat to Telegram → Added to list
Meeting → Idea emerges → Telegram message → Captured
```

**Alternative channels** (OpenClaw supports):
- WhatsApp
- Slack
- Discord
- Signal
- iMessage
- Google Chat
- Microsoft Teams

---

### Pattern: Mission Control as Secondary View
**Status**: ✅ PROVEN | ⚠️ CAUTION (NLW unsure if worth it)

**Purpose**: "Complement to my Telegram chat by Telegram chat view"

**What it shows**:
- Scheduled interactions
- Things agents found
- Costs
- Decisions waiting for you

**NLW's assessment**:
> "The most technologically demanding part... this is the part that I'm not sure that I think is actually worth it"

**Recommendation**: Skip initially, use off-the-shelf tools when available

---

### Pattern: USER.md Learning Loop
**Status**: ✅ PROVEN | 🎯 RECOMMENDED

**Example** (NLW):
Claude added to USER.md:
> "We'll push back hard if something feels wrong. Productive, not hostile."

**Pattern**:
1. Agent observes your behavior
2. Updates USER.md with insights
3. Future interactions adapt to your style

**Benefit**: Agent learns your preferences without explicit teaching

---

## Quality & Reliability Patterns

### Pattern: Research Quality Calibration
**Status**: ✅ PROVEN | 🎯 RECOMMENDED

**Process** (NLW's approach):

**Phase 1: Initial output** (weeks 1-2)
- Agent produces research and proposals
- Quality varies widely

**Phase 2: Source calibration** (week 3)
- Review outputs with agent
- Teach difference between good/great/mediocre sources
- Provide examples

**Phase 3: Writing calibration** (week 4)
- Refine proposal justification quality
- Set standards for evidence and reasoning
- Iterate

**Phase 4: Maintenance** (ongoing)
- Occasional spot checks
- Correct drift
- "Certainly wasn't overwhelming" (NLW)

**Timeline**: 3-4 weeks to quality baseline

---

### Pattern: Heartbeat Reliability Management
**Status**: ✅ PROVEN | ⚠️ CAUTION

**Known issue**: Heartbeats drop off unpredictably

**Detection**:
- Agent stops checking in
- No HEARTBEAT_OK messages
- No scheduled alerts

**Resolution**:
1. Check agent is running
2. Restart agent process
3. Review heartbeat configuration
4. Monitor for recurrence

**Prevention**: None reliable yet (OpenClaw working on this)

**Expectation**: Plan to reset agents occasionally

---

### Pattern: Agent Mission Flexibility
**Status**: ✅ PROVEN (NLW's experience)

**Finding** (NLW, lines 61-62):
> "A couple of times, I basically requisitioned one of those agents to do a different type of unrelated research, and it did a good job without losing its mission focus."

**Pattern**:
- Agents can handle off-mission tasks
- Return to core mission afterward
- Don't need rigid specialization

**Use case**: Ad-hoc research requests to research agents

---

## Security Patterns

### Pattern: Conservative Initial Access
**Status**: ✅ PROVEN | 🎯 RECOMMENDED

**NLW's approach**:
```
✅ Allowed:
- File system (limited directories)
- Chat interface
- Research (read-only web)
- Internal task management

❌ Not allowed (yet):
- Email monitoring
- Email sending
- Extensive third-party integrations
- Many skills (malware concerns)
```

**Philosophy**: "Incrementally give it access to the systems"

**Evolution**: Expand access as trust builds

---

### Pattern: Skill Vetting
**Status**: ✅ PROVEN | ⚠️ CAUTION

**Issue** (NLW, line 79):
> "They found that initially a ton of them [skills] had malware"

**Current approach**:
- Not using many skills
- Watching security situation improve
- Considering specific skills (e.g., Supermemory)

**Recommendation**:
1. Start without skills
2. Wait for ClawHub security improvements
3. Vet each skill manually before enabling
4. Monitor OpenClaw security updates

---

### Pattern: Isolated Environment
**Status**: ✅ PROVEN (Mac Mini approach)

**Benefits**:
- No bleeding into personal systems
- Can wipe/reset without consequences
- Controlled expansion of access

**Alternative**: User-level sandboxing on existing machine

---

## Development Workflow Patterns

### Pattern: Claude as Build Partner
**Status**: ✅ PROVEN | 🎯 RECOMMENDED (NLW's #1 lesson)

**Setup**:
```
1. Create Claude Project (or ChatGPT/Gemini equivalent)
2. Load OpenClaw documentation
3. Treat as coach/mentor/build partner
4. Use for ALL technical questions
```

**NLW's instruction to Claude**:
> "I am a neophyte and an income poop and I need you to walk through everything step by step in the tiniest little incremental ways"

**Result**:
- Zero YouTube videos watched
- Zero tutorials followed
- Dozens of Claude conversations
- All problems resolved

---

### Pattern: Shameless Question Asking
**Status**: ✅ PROVEN | 🎯 RECOMMENDED

**Example** (NLW, lines 89-91):
```
Claude: "Run these commands one at a time"
NLW: "If those things are four separate commands,
      copy them one at a time, please"
Claude: [Dutifully copies them one by one]
```

**Lesson**: "Infinite patience" - no question too basic

**Pattern**:
- Ask even "infantile" questions
- Request copy-paste ready commands
- Get step-by-step breakdowns
- Never assume you should know something

---

### Pattern: Expect Negative ROI Period
**Status**: ✅ PROVEN (NLW's guarantee)

**Timeline**:
- Weeks 1-3: Heavy negative ROI
- Hours of Claude back-and-forth
- Learning curve, mistakes, restarts

**NLW's disaster** (lines 95-96):
- Tried to force Opus 4.6 upgrade
- Wiped out all agents
- Tens of hours of work seemed lost
- Worked through it with Claude

**Promise**:
> "There will be no point at which you get fully stuck"

**Mindset**: Investment period, not waste

---

### Pattern: Iterative Agent Refinement
**Status**: ✅ PROVEN

**Process**:
1. Build agent with initial SOUL.md
2. Use for 1-2 weeks
3. Observe behavior
4. Refine personality/instructions
5. Test changes
6. Repeat

**Example**: PM agents started as simple task lists, evolving toward coordination

**USER.md evolution**: Agent learns your style over time

---

## Monitoring & Observability Patterns

### Pattern: Simple Cost Tracking
**Status**: ✅ PROVEN (mentioned but not detailed)

**NLW's dashboard shows**:
- Costs (line 7: "costs, and things that are waiting on decisions for me")

**Implementation**: Not detailed in video

**Guide suggests** (not verified):
- Per-agent cost tracking
- Model usage tracking
- Budget alerts

---

### Pattern: Decision Queue
**Status**: ✅ PROVEN (NLW's dashboard)

**Function**: Surface items waiting for human input

**Examples**:
- Research proposals requiring approval
- Decisions PM agents are waiting on
- Tasks that need clarification

**Interface**: Mission Control dashboard shows these

---

### Pattern: Status Dots (NOT verified)
**Status**: 🔬 EXPERIMENTAL (from guide, not in NLW's video)

**Guide suggests**:
- 🟢 Green = Active
- ⚫ Gray = Idle (within 2x threshold)
- 🟡 Amber = Overdue
- 🔴 Red = Error

**Screenshot 1**: Shows simpler interface without color-coded dots

**Reality**: Simpler status indicators likely used

---

## Advanced Patterns (From Guide, Not NLW)

### Pattern: AI Maturity Mapping
**Status**: 🔬 EXPERIMENTAL (OUTPUT, not feature)

**Clarification**:
- This is what NLW's research agents PRODUCE
- Not an OpenClaw feature
- Product of AIDB Intelligence platform

**Dimensions** (NLW):
1. Use cases
2. Systems integration
3. Data access
4. Outcomes
5. People
6. Governance

**Use case**: Research agents propose updates to these frameworks

---

### Pattern: Opportunity Radars
**Status**: 🔬 EXPERIMENTAL (OUTPUT, not feature)

**What it is**:
- Way to organize use cases by business function
- Categories based on business type applicability
- Research output, not agent capability

---

### Pattern: Continuous Research Sweeps
**Status**: ✅ PROVEN (24/7 research agents)

**Implementation**:
```
Heartbeat (every 30 min):
1. Check research sources (studies, surveys, papers)
2. Catalog new findings
3. Integrate into knowledge base
4. Generate proposals for updates

Cron (daily/weekly):
- Comprehensive research sweeps
- Cross-source synthesis
- Trend analysis
```

**Result**: "Literally around the clock surfacing, cataloging, and integrating"

---

## Integration Patterns (Future/Experimental)

### Pattern: Email Monitoring (NOT implemented)
**Status**: 📋 FUTURE (NLW considering)

**Potential**:
- Scan inbox for priority items
- Flag decisions needed
- Summarize threads
- Never mentioned if/when implementing

---

### Pattern: Supermemory Integration
**Status**: 📋 FUTURE (NLW considering)

**Mentioned** (line 79):
> "I've got my eye on a few things I might want to integrate, like super memory"

**Purpose**: Enhanced memory/knowledge management

**Status**: Under consideration, not implemented

---

### Pattern: Slack Integration (Phase 2)
**Status**: 📋 FUTURE (via skills)

**NLW's vision** (line 67-68):
- PM agents interact with Slack
- Coordinate with team members
- Surface project status

**Timing**: Phase 2, after basic agents proven

---

## Anti-Patterns (What NOT to Do)

### Anti-Pattern: Building Mission Control First
**Status**: ⚠️ CAUTION

**NLW's lesson**:
- Most technically demanding part
- Uncertain if worth it
- Off-the-shelf options coming

**Right approach**: Telegram first, dashboard later (or never)

---

### Anti-Pattern: Complex Multi-Agent Orchestration Too Soon
**Status**: ⚠️ CAUTION

**NLW's explicit choice**:
- No sequential agent handoffs
- No complex coordination
- Simple shared context only

**Right approach**: Master simple agents first, Phase 2 for coordination

---

### Anti-Pattern: Builder Agent for Iterative Projects
**Status**: ⚠️ CAUTION (NLW's experience)

**Issue**: Most projects are iterative and need constant feedback

**Right tool**: Replit, Lovable, Claude Code for interactive coding

**Builder agent works for**: Scripts, utilities, discrete tasks

---

### Anti-Pattern: Extensive Skill Usage Before Security Mature
**Status**: ⚠️ CAUTION

**Issue**: Malware found in many skills

**Right approach**:
- Wait for security improvements
- Vet manually before enabling
- Start with zero skills

---

### Anti-Pattern: Following YouTube Tutorials
**Status**: ⚠️ CAUTION (NLW's lesson)

**NLW watched**: Zero YouTube videos

**Right approach**: Claude as build partner with full context

**Why**:
- Tutorials lack your specific context
- Can't adapt to your environment
- No back-and-forth for clarification

---

## Decision Trees

### When to Build an Agent?

```
Does this work benefit from:
├─ Mobile management? (Y) → Consider agent
├─ 24/7 persistence? (Y) → Consider agent
├─ Scheduled execution? (Y) → Consider agent
└─ All No? → Probably not a good agent use case

If considering agent:
├─ Can you clearly define the task? (N) → Wait
├─ Is quality verifiable? (N) → Difficult
├─ Does it require real-time decisions? (Y) → Maybe not agent
└─ All clear? → Build agent
```

### Which Agent Type?

```
Task nature:
├─ To-do management → Task agent (HIGH VALUE)
├─ 24/7 research in narrow domain → Research agent (HIGH VALUE)
├─ Project tracking (basic) → PM agent (MEDIUM VALUE)
├─ Discrete coding tasks → Builder agent (LOW VALUE for most)
├─ Cross-project triage → Chief of Staff (WAIT until Phase 2)
└─ Cost tracking → Finance agent (EXPERIMENTAL)
```

### Infrastructure Choices?

```
Budget:
├─ <$100 → Use old laptop + free Tailscale
├─ $100-$700 → Mac Mini + Tailscale
└─ Enterprise → VPS + Incus containers

Technical comfort:
├─ Non-technical → Mac Mini (simplest)
├─ Comfortable → Any laptop + Docker
└─ Advanced → VPS + custom setup
```

---

## Phased Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
**Goal**: One working agent, understand system

**Steps**:
1. ✅ Set up Claude Project with OpenClaw context
2. ✅ Install OpenClaw on always-on machine
3. ✅ Configure Tailscale for remote access
4. ✅ Build Task Agent (highest ROI)
5. ✅ Learn markdown file structure
6. ✅ Test heartbeat system
7. ✅ Iterate on SOUL.md based on usage

**Success criteria**:
- Task agent working reliably
- Comfortable with Claude build partnership
- Understand file structure
- Can reset heartbeat when needed

---

### Phase 2: Specialized Value (Weeks 5-8)
**Goal**: 3-5 agents providing clear value

**Steps**:
1. ✅ Add specialized research agent
2. ✅ Quality calibration (3-4 weeks)
3. ✅ Add 2-3 PM agents for major projects
4. ✅ Set up cron schedules (8 AM, 5 PM)
5. ✅ Refine agent personalities
6. ⚠️ Skip mission control (use Telegram)
7. ⚠️ Skip builder agent unless clear need

**Success criteria**:
- Research agent producing quality proposals
- PM agents providing daily value
- Comfortable with multi-agent management
- Clear ROI emerging

---

### Phase 3: Integration Preparation (Weeks 9-12)
**Goal**: Stable foundation for system integration

**Steps**:
1. ✅ Build Chief of Staff (will be idle)
2. 🔬 Experiment with safe skills
3. 🔬 Consider email monitoring
4. 📋 Plan Phase 2 PM coordination
5. 📋 Identify systems for integration
6. 📋 Security review before expansion

**Success criteria**:
- All agents stable and reliable
- Clear Phase 2 integration plan
- Security posture understood
- Ready for broader access

---

### Phase 4: Coordination & Integration (Month 4+)
**Goal**: Phase 2 - agents coordinate and integrate

**Steps**:
1. 📋 Connect PM agents to Slack/systems
2. 📋 Enable inter-agent communication
3. 📋 Activate Chief of Staff
4. 📋 Implement agent handoffs
5. 📋 Add email monitoring
6. 📋 Expand skill usage carefully

**Success criteria**:
- Agents coordinate without manual intervention
- Chief of Staff provides daily triage
- System integrations working
- True "digital employee" behavior

**Note**: NLW is still in Phase 2-3, not Phase 4

---

## Quick Reference: What to Copy from NLW

### ✅ Definitely Copy

1. **Claude as Build Partner** - Don't use YouTube tutorials
2. **Task Agent First** - Highest value, lowest effort
3. **Telegram Primary Interface** - Skip mission control initially
4. **Conservative Access** - Limited systems at start
5. **30-Minute Heartbeat Default** - Standard interval
6. **PM Morning/Evening Check-ins** - 8 AM, 5 PM pattern
7. **Quality Calibration Process** - For research agents
8. **Expect Negative ROI** - 3-4 week learning curve
9. **Five Core Files** - IDENTITY, SOUL, AGENTS, USER, TOOLS

### ⚠️ Copy with Caution

1. **Builder Agent** - Only if you have discrete coding tasks
2. **Mission Control** - Very optional, off-the-shelf coming
3. **Multiple Research Agents** - Start with one, expand if valuable
4. **Chief of Staff** - Will be idle until Phase 2

### ❌ Don't Copy (Yet)

1. **Complex Agent Orchestration** - NLW doesn't do this
2. **Extensive Skills** - Security concerns remain
3. **Email Automation** - Not implemented by NLW
4. **Multi-Agent Handoffs** - Phase 2+ only

---

## Checklist: Before Building Your First Agent

**Prerequisites**:
- [ ] Claude Project set up with OpenClaw docs
- [ ] Always-on machine configured (Mac Mini or laptop)
- [ ] Tailscale installed for remote access
- [ ] OpenClaw installed and running
- [ ] Telegram/WhatsApp connected
- [ ] Clear use case identified (task management, research, etc.)
- [ ] Time allocated for learning curve (negative ROI period)
- [ ] Expectation set: simple start, expand later

**First agent recommendation**: Task Agent
**Timeline**: 1-2 weeks to working agent
**Success**: Using it daily for task management

---

## Cost Expectations

### NLW's System (not detailed in video)

**Known costs**:
- Mac Mini: ~$600 one-time (optional)
- Tailscale: Free (personal use)
- OpenClaw: Free (open source)
- LLM API: Not specified by NLW

### Guide's Estimate (not verified)

**Monthly API costs**:
- Kimi K2.5: $30-80/month
- GPT-5 Nano (heartbeats): $1-5/month
- Opus 4.5 (complex tasks): $20-50/month
- **Total**: $60-150/month

**vs. Typical setups**: $150-5000/month (Opus-only)

---

## Success Metrics

### Week 1-2: Foundation
- [ ] Task agent working
- [ ] Can add/update tasks via Telegram
- [ ] Heartbeat firing reliably
- [ ] Comfortable asking Claude questions

### Week 3-4: Value Emergence
- [ ] Using task agent daily
- [ ] Research agent (if built) producing output
- [ ] PM agents providing structure
- [ ] Clear workflow established

### Week 5-8: Proven Value
- [ ] Agents providing net positive value
- [ ] Quality calibration complete (research)
- [ ] Rare heartbeat resets needed
- [ ] Comfortable managing 3-5 agents

### Week 9-12: Stable Foundation
- [ ] All agents reliable
- [ ] Clear Phase 2 roadmap
- [ ] Ready for integration expansion
- [ ] Positive ROI achieved

---

## Troubleshooting Common Issues

### Issue: Heartbeat Stops Working

**Symptoms**:
- Agent stops checking in
- No HEARTBEAT_OK messages

**Solutions**:
1. Restart OpenClaw process
2. Check HEARTBEAT.md format
3. Verify 30-minute interval setting
4. Review agent logs
5. Last resort: Rebuild agent config

**Prevention**: None reliable yet

---

### Issue: Research Quality Poor

**Symptoms**:
- Mediocre sources
- Weak justifications
- Off-topic findings

**Solutions**:
1. Review outputs with agent
2. Provide good vs. bad examples
3. Refine SOUL.md quality standards
4. Iterate over 2-3 weeks
5. Set explicit quality criteria

**Timeline**: 3-4 weeks to stable quality

---

### Issue: Builder Agent Not Useful

**Symptoms**:
- Rarely used
- Output needs heavy revision
- Doesn't save time

**Solutions**:
1. Evaluate if projects are too iterative
2. Consider using Replit/Claude Code instead
3. Limit to discrete scripts/utilities
4. May not be good fit for your workflow

**NLW's result**: Least used agent

---

### Issue: Overwhelmed by Agent Messages

**Symptoms**:
- Too many notifications
- Can't keep up
- Telegram constantly buzzing

**Solutions**:
1. Adjust heartbeat intervals (30 min → 60 min)
2. Set HEARTBEAT_OK to suppress non-urgent
3. Use cron instead of heartbeat for non-urgent
4. Consolidate agents if redundant
5. Set active hours (8 AM - 10 PM)

---

## Key Quotes for Reference

**On learning approach**:
> "The best way to learn some new thing in AI or to build some new thing in AI is to just let the AI help." - NLW

**On accessibility**:
> "If you have the will and are willing to put in the time, it doesn't matter how non-technical you are." - NLW

**On simplicity**:
> "I'm doing a really simple version of this" - NLW

**On ROI**:
> "It is almost certainly the case that there will be a meaningful period of time where you are negative ROI" - NLW

**On mission control**:
> "This is the part that I'm not sure that I think is actually worth it" - NLW

---

## Conclusion: The Synthesis

**What to do** (from NLW's proven approach):
1. Use Claude as build partner, not YouTube
2. Start with Task Agent (highest ROI)
3. Add specialized research agents for persistent work
4. PM agents for project segmentation
5. Telegram as primary interface
6. Conservative system access initially
7. Expect 4-8 week learning curve
8. Skip mission control, skip builder (unless clear fit)

**What to aspire to** (from guide, Phase 2+):
1. Multi-agent coordination with handoffs
2. System integrations (Slack, email, etc.)
3. Mission control dashboard
4. Advanced monitoring with status indicators
5. Extensive skill library (once security mature)

**Critical lesson**:
NLW's simple Phase 1 system provides real value TODAY. The guide's complex Phase 2 system is aspirational for LATER.

Start simple. Prove value. Expand carefully.
