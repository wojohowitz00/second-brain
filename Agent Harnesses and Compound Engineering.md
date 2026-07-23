# Agent Harnesses & Compound Engineering
## Using AI Infrastructure to Make Quality Software the Default

> Source: Research discussion synthesized from Anthropic, OpenAI, Every.to, OWASP, Braintrust, and others — March 2026

---

## The Core Thesis

From *AI Made Every Company 10x More Productive* (2026):

> **Unlock #3: Quality software is the default today. It's not at a premium.**
>
> So much of our software has been mediocre — not because engineers are bad, but because we lack the execution capacity to do great testing, great documentation, great security review, great performance optimization, great accessibility, and great visual polish. All on time, all under budget.
>
> These problems are all agent verifiable. When agent harnesses run testing, security review, and documentation — not as expensive add-ons, but as standard procedure — the baseline quality of all software goes up dramatically.
>
> For so long, the gap between the top 5% of engineering teams and everyone else has been polish. Not anymore. The quality floor rises. Differentiation shifts to product.

---

## What Is an Agent Harness?

An agent harness is the **infrastructure around the AI model**, not the model itself. It operates at a higher level than agent frameworks. The harness is the OS:

- Curates context before each agent turn
- Handles the boot sequence (prompts, hooks, memory injection)
- Routes tool calls and manages lifecycle
- Enforces quality gates
- Writes learnings back for future sessions

> *"The agent isn't the hard part — the harness is."* — Industry consensus, Q1 2026

**Key distinction**: Capabilities that required complex hand-coded pipelines in 2024 are handled by a single context-window prompt in 2026. Developers must build harnesses that allow them to rip out the "smart" logic they wrote yesterday as models improve.

---

## Compound Engineering (Every.to)

Compound engineering is the framework that connects harnesses to institutional memory. The principle: **each unit of engineering work should make the next unit easier, not harder.**

### The Four-Step Loop

```
Plan → Work → Review → Compound
```

- **Plan**: Subagents read issues, search `docs/knowledge/` for past learnings, research approaches, and synthesize implementation plans before any code is written
- **Work**: Claude asks clarifying questions, builds the feature, writes tests from the plan
- **Review**: Engineer reviews output and lessons learned; specialized review agents run in parallel
- **Compound**: Learnings are written back to `docs/knowledge/` as searchable YAML-frontmatter markdown — bugs, failures, a-ha moments, solved problems

The `/compound` command spawns six parallel subagents: context analyzer, solution extractor, related-docs finder, prevention strategist, category classifier, and documentation writer.

### Documentation as Harness Layer

Documentation in this model is not an artifact *of* engineering — it's an *input* to the next cycle. Three levels:

| Level | Model | Mechanism |
|-------|-------|-----------|
| Static injection | OpenAI/Cursor | `docs/` directory injected into context at session start — maps, not manuals |
| Quality tracking | Schmid model | Living health dashboard grading each domain and architectural layer; routes agent attention |
| Active generation | Every's `/compound` | Docs generated *during* the loop, not post-hoc; future planning agents read them before writing code |

**OpenAI's key finding**: Give the agent a map, not a 1,000-page instruction manual. Short structured files as pointers — not encyclopedias.

### Reference Architecture

```
docs/
  knowledge/        ← /compound output; YAML-frontmatter markdown
  specs/            ← design intent injected at plan phase
  quality.md        ← domain health grades, gap tracking
  architecture.md   ← map-not-manual, pointer structure
CLAUDE.md           ← boot sequence, agent instructions
.evals/             ← eval suite, registered before features ship
```

---

## Eval/Testing on the Completed Harness

### Why Agent Evals Are Fundamentally Different

Traditional software testing has a fixed target. Agent harness testing has a moving target across three dimensions:
- **Non-determinism** — same input, different output each run
- **Multi-step trajectories** — the path matters, not just the endpoint
- **Environment side effects** — did the database actually update, not just did the agent claim it did

> Anthropic's framing: saying "your flight is booked" is not a passing eval. The reservation must exist in the database.

### The Three Eval Layers

**Layer 1 — Unit evals (component-level)**
Test individual agent capabilities in isolation. Fast, cheap, catch regressions in specific behaviors without running the full pipeline. Does the planning subagent produce a coherent spec? Does the documentation writer produce valid YAML frontmatter?

**Layer 2 — Trajectory evals (path-level)**
Evaluate the full transcript — all tool calls, reasoning steps, and intermediate states. Catches efficiency regressions (correct answer, 40 unnecessary tool calls), reasoning failures (right output, wrong logic), safety violations mid-run.

Three grader types:
- **Code-based**: string matching, regex, binary checks, API response verification — fast, cheap, reproducible
- **Model-based**: LLM-as-judge for open-ended outputs — rubric scoring, pairwise comparison, multi-judge consensus
- **Human**: reference standard used to calibrate model-based graders, not primary gate

**Layer 3 — Final state evals (outcome-level)**
Did the environment end in the correct state? Does the PR exist with the right contents? Does the test suite pass? Is the doc written to the correct path? Most expensive, slowest, but the only true correctness signal.

### The Infrastructure Noise Problem

Anthropic's March 2026 finding: **infrastructure configuration alone can swing eval scores by 6+ percentage points** — often more than the leaderboard gap between top models.

The mechanism: when container memory limits equal guaranteed allocation (zero headroom), transient memory spikes terminate the container. The agent "fails" a task it would have passed with a 3x buffer. This means benchmark rankings partially reflect which models default to strategies compatible with the evaluator's hardware, not just underlying capability.

**Implication**: Resource configuration (memory limits, CPU, parallelism headroom) must be treated as a first-class experimental variable, controlled with the same rigor as prompt format or sampling temperature.

### Golden Datasets and Regression Suites

Maintain a curated golden set of 20–50 test cases as the regression suite. Two components:
1. **Representative cases** — tasks sampling the full distribution of what the harness handles
2. **Adversarial cases** — previously-failed production tasks, permanently added to prevent recurrence

Every production failure → golden set entry → reduced recurrence. This is compounding on the testing side.

### OpenAI's Codex Approach: Agent-to-Agent Review

When agent throughput exceeds human attention, waiting for human review becomes more expensive than the cost of occasional corrections. Codex's architecture:
- Agent reviews its own changes locally first
- Requests additional agent reviews (local and cloud)
- Iterates until all agent reviewers are satisfied
- PRs are short-lived, merged fast
- Test flakes get follow-up runs, not indefinite blocks

Traditional quality gates were designed around human review bandwidth as the constraint. When the constraint shifts to agent throughput, the gate design must shift too.

---

## Security Harnesses

### The New Attack Surface: The Agent Itself

OWASP published the **Top 10 for Agentic Applications 2026** — a separate framework from the traditional OWASP Top 10 — because autonomous agents introduce risks that didn't exist in static software.

**Top risks specific to agents:**

| Risk | Description |
|------|-------------|
| ASI01 — Agent Goal Hijack | Attackers redirect agent objectives via manipulated inputs, tool outputs, or external content |
| ASI02 — Tool Misuse | Agents invoke legitimate tools incorrectly due to injection or misalignment — the tool isn't compromised, the reasoning about it is |
| ASI03 — Identity & Privilege Abuse | Agents inherit credentials, cache permissions, delegate to sub-agents; a compromised orchestrator abuses downstream permissions |
| ASI06 — Memory & Context Poisoning | Persistent corruption of RAG stores or knowledge base — a poisoned `/compound` doc infects all future sessions |

**Two governing design principles:**
- **Least Agency**: autonomy is a feature earned, not a default
- **Strong Observability**: log what the agent does, why, which tools, which identities — every turn

### Three-Layer Security Harness

**Layer 1 — SAST on generated code**
Run immediately on AI-generated code before review. *Reachability-based prioritization* is the key advance: rank by whether vulnerabilities are actually reachable from application code, not just present in it. AI codegen produces a lot of defensive-but-unreachable code paths; classic SAST drowns in false positives from this.

**Layer 2 — DAST in pre-production**
AI-driven DAST now auto-discovers attack surface from source code and auto-generates test configurations. Business-logic testing verifies the agent can't be manipulated into acting outside its mandate — testable in pre-production before any human touches it. What previously required weeks of setup takes hours.

**Layer 3 — Runtime adversarial probing**
Context-aware penetration testing on demand throughout the development lifecycle, not just at ship time. The **Intent Capsule** pattern is emerging as a mandatory architectural requirement: a signed, immutable envelope binding the agent's original mandate to each execution cycle, so sub-agents can't be redirected by injected content mid-run.

**Additional threat (2026)**: Multimodal agents accepting images are vulnerable to adversarial instructions embedded visually — bypassing all text-layer input sanitization. Not theoretical; documented by Cloud Security Alliance.

---

## Accessibility Harnesses

### The Honest State of Automation

Even the best AI-augmented accessibility scanners catch **20–50% of WCAG violations**. Accessible.org is targeting 75% coverage with <0.5% false positives as a 2027 milestone — not there yet. The harness shifts where human attention is required, not whether it's required.

### Three-Layer Accessibility Harness

**Layer 1 — axe-core static scan**
Industry standard (used by Google, Microsoft, browser DevTools). Runs on every PR against WCAG 2.2 success criteria. Catches: missing alt text, color contrast failures, incorrect ARIA attributes, missing labels, landmark structure errors. These are the *structural* violations — definitively checkable by machine.

**Layer 2 — Dynamic agent (keyboard nav + interactive patterns)**
Run after the static scan, using a headless browser (Playwright) to actually drive the UI. An input labeled correctly in the DOM can still be unreachable via keyboard if focus management is broken. This layer catches: keyboard navigation flow, tab order logic, focus trap behavior, interactive component state changes.

**Layer 3 — Remediation loop**
AI-powered tools now generate remediation guidance inline — not just "this element has no label" but specific fix code, opening a PR with the suggested change. The engineer reviews the PR, not the raw finding.

**Integration pattern (current standard)**: Trigger automated accessibility scans on every PR. Structural WCAG failures are detected before manual testing begins. The harness gates on what it can reliably detect; surfaces everything else as findings for human review; never blocks on what it can't reliably grade.

### What Doesn't Automate
Cognitive load, reading level, plain language quality, interaction consistency across a flow, context-appropriate error messaging. These require human judgment. The harness handles the verifiable; humans handle the experiential.

---

## Final Polish Harnesses

### Four Verifiable Dimensions of "Polish"

**1. Visual regression**
Percy (BrowserStack) and Chromatic capture screenshots of every component and page state on every PR, diff against baseline, flag changes for human review. AI-powered perceptual diffing understands human vision — suppresses insignificant pixel drift (anti-aliasing, sub-pixel rendering) while surfacing real regressions (button moved 8px, color changed, text truncated).

- **Percy**: 1,000+ screenshot comparisons across 50,000+ real devices; Playwright/Cypress/Selenium/Storybook integrations
- **Chromatic**: purpose-built for Storybook; tighter fit for component-first workflows

**2. Performance budgets**
Lighthouse CI enforces budgets on Core Web Vitals (LCP, CLS, INP) in the pipeline. If a feature degrades performance past the budget threshold, the build fails before merge. AI-generated code frequently produces performance anti-patterns (over-fetching, unoptimized images, unnecessary re-renders) that humans writing code wouldn't reach for.

**3. Linting and code style gates**
The Agent Legibility Scorecard (emerging 2026 pattern) evaluates agent-generated code against seven metrics including Lint + Format Gates and Validation Harness. If generated code violates framework conventions or anti-patterns, the pipeline blocks. The harness enforces the codebase's own standards against AI output, which otherwise trends toward "works but not idiomatic."

**4. Every's `/workflows:review` — 14 parallel specialized reviewers**
Runs 14 specialized agents simultaneously across security, performance, architecture, and style. Polish-specific reviewers check naming consistency, API surface coherence, UX copy accuracy, component hierarchy logic. Findings are triaged by priority before surfacing — the engineer sees a ranked list, not 14 simultaneous opinions. The full compound engineering pipeline spawns 50+ agents across all stages.

---

## The Standard Merge Gate Sequence

```
1. Lint + format          → fastest, cheapest — fail early
2. Unit + integration tests
3. SAST + SCA security scan
4. Accessibility static scan (axe-core)
5. Visual regression diff (Percy/Chromatic)
6. Performance budget (Lighthouse CI)
7. Agent-to-agent review (security, arch, style reviewers in parallel)
8. Human approval on flagged items only
```

The ordering is deliberate: cheap deterministic checks run first to fail fast; expensive probabilistic checks (model-based reviewers, visual diffing) run only if earlier gates pass.

---

## How It All Compounds

The thread across every harness type — eval/testing, security, accessibility, polish — is the same mechanism:

```
Build
  → Harness gates run
  → Failures surface
  → Agent-to-agent review
  → Fixes applied
  → Trajectory logged
  → Learnings written to docs/knowledge/ via /compound
  → Next build reads knowledge/ at plan phase
  → Fewer failures
  → Evals cost less
  → Quality floor rises
```

Each production failure → golden set entry → reduced recurrence.
Each novel fix → compound doc → reduced re-discovery time.

**The distinction from traditional CI/CD**: CI/CD prevents *known* regressions. A compound eval harness reduces the *surface area of unknown failures* over time — because the knowledge written back to `docs/knowledge/` teaches future planning agents about failure modes *before code is written*, not after.

The quality floor rises not because individual agents are better, but because the harness accumulates institutional memory that every future session inherits.

---

## Sources

- [Demystifying evals for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Quantifying infrastructure noise in agentic coding evals — Anthropic Engineering](https://www.anthropic.com/engineering/infrastructure-noise)
- [The importance of Agent Harness in 2026 — Philipp Schmid](https://www.philschmid.de/agent-harness-2026)
- [Harness engineering: leveraging Codex in an agent-first world — OpenAI](https://openai.com/index/harness-engineering/)
- [Unrolling the Codex agent loop — OpenAI](https://openai.com/index/unrolling-the-codex-agent-loop/)
- [2026 Agentic Coding Trends Report — Anthropic](https://resources.anthropic.com/2026-agentic-coding-trends-report)
- [Compound Engineering: How Every Codes With Agents — every.to](https://every.to/chain-of-thought/compound-engineering-how-every-codes-with-agents)
- [Compound Engineering: The Definitive Guide — every.to](https://every.to/source-code/compound-engineering-the-definitive-guide)
- [Learning from Every's Compound Engineering — Will Larson](https://lethain.com/everyinc-compound-engineering/)
- [EveryInc/compound-engineering-plugin — GitHub](https://github.com/EveryInc/compound-engineering-plugin)
- [What is eval-driven development — Braintrust](https://www.braintrust.dev/articles/eval-driven-development)
- [AI agent evaluation: A practical framework — Braintrust](https://www.braintrust.dev/articles/ai-agent-evaluation-framework)
- [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [AI Agent Security Cheat Sheet — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html)
- [Harness AI Feb 2026: Secure SDLC — Harness.io](https://www.harness.io/blog/harness-ai-february-2026-updates)
- [AWS Security Agent Preview — AWS Blog](https://aws.amazon.com/blogs/aws/new-aws-security-agent-secures-applications-proactively-from-design-to-deployment-preview/)
- [AI-driven DAST in 2026 — Help Net Security](https://www.helpnetsecurity.com/2026/02/26/joni-klippert-ceo-stackhawk-ai-driven-dast-testing/)
- [Image-Based Prompt Injection — Cloud Security Alliance](https://labs.cloudsecurityalliance.org/research/csa-research-note-image-prompt-injection-multimodal-llm-2026/)
- [Automated Accessibility Testing with AI and axe-core — Test-Lab.ai](https://www.test-lab.ai/blog/accessibility-testing-agent)
- [Automating Accessibility Testing in 2026 — BrowserStack](https://www.browserstack.com/guide/automate-accessibility-testing)
- [AI Hybrid WCAG Audits Expected in Q1 2027 — Accessible.org](https://accessible.org/ai-hybrid-wcag-audits/)
- [Percy Visual Regression Testing Tools 2026](https://percy.io/blog/visual-regression-testing-tools/)
- [Harness Engineering — Martin Fowler](https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html)
