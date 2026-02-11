# OpenClaw + Incus + Kimi K2.5: Architecture Synthesis

## 1. How OpenClaw Actually Works

### Core Architecture

OpenClaw is a **Node.js CLI process and Gateway server** (requires Node ≥22) that functions as a message router and AI agent runtime. It's not a model — it's infrastructure that connects messaging platforms to LLM APIs with tool execution capabilities.

**Three core functions:**
1. **Message Interception** — receives inputs from communication channels (WhatsApp, Telegram, Slack, Discord, Signal, iMessage, Google Chat, Microsoft Teams, Matrix, WebChat)
2. **LLM Orchestration** — calls model APIs (Anthropic, OpenAI, OpenRouter, local models) with dynamically constructed system prompts
3. **Controlled Tool Execution** — runs shell commands, file operations, browser tasks in local or sandboxed (Docker) environments

### The Gateway

The Gateway is the control plane — a long-running service that manages:
- **Sessions** — persistent conversation state per channel/user/agent
- **Channels** — adapters that normalize input from each messaging platform
- **Tools** — browser, exec, file system, canvas, nodes, cron
- **Cron/Heartbeat** — scheduled and periodic agent turns
- **WebSocket control plane** — sessions, presence, config, webhooks, Control UI

Install and run:
```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon    # wizard-driven setup
openclaw gateway --port 18789 --verbose
```

### Lane Queue (Serial Execution)

OpenClaw processes messages through a **strictly serial pipeline** to prevent race conditions:
1. Channel Adapter standardizes input
2. System Prompt Builder merges instructions + tools + skills + memory
3. Session History Loader pulls previous interactions from JSONL transcript
4. Context Window Guard monitors tokens, triggers summarization before overflow
5. Tool execution runs sequentially by default

### Memory System

Simple, file-based, no vector DB required:
- **JSONL Transcripts** — line-by-line audit log of messages, tool calls, results
- **MEMORY.md** — markdown file of distilled knowledge, summaries, experiences
- The project explicitly notes that vector search often leads to "semantic noise"

### Heartbeat System

Periodic agent turns in the main session to surface things needing attention:
```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "target": "last",
        "activeHours": { "start": "08:00", "end": "24:00" }
      }
    }
  }
}
```

- Agent checks a HEARTBEAT.md checklist (optional but recommended)
- If nothing needs attention, responds `HEARTBEAT_OK` (suppressed, no notification sent)
- Alert content gets delivered to the last active channel
- Can be restricted to active hours to avoid night-time spam
- Model can be overridden — use a cheap model (e.g., GPT-5 Nano) for heartbeats, strong model for real work

### Cron System

More structured scheduled tasks, two modes:
- **Main session** — enqueues a system event, runs on next heartbeat
- **Isolated session** — dedicated agent turn in `cron:<jobId>`, fresh context each time, can deliver output to specific channels

```bash
# Morning briefing delivered to WhatsApp
openclaw cron add \
  --name "Morning status" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize inbox + calendar for today." \
  --announce \
  --channel whatsapp \
  --to "+15551234567"
```

Cron jobs persist under `~/.openclaw/cron/` — restarts don't lose schedules. Exponential retry backoff on failures (30s → 1m → 5m → 15m → 60m).

### Multi-Agent Routing

Route inbound channels/accounts to isolated agents, each with:
- Own workspace directory
- Per-agent sessions
- Per-agent skills (workspace-level)
- Per-agent model configuration
- Separate sandboxing scope

---

## 2. Skills System (The Extensibility Layer)

### How Skills Work

Skills are **directories containing a SKILL.md** file with YAML frontmatter and natural language instructions. No rigid schemas — the AI reads the instructions and adapts behavior. Each skill teaches the agent how to use a tool or execute a workflow.

```
skills/
  my-skill/
    SKILL.md      # Required: frontmatter + instructions
    helper.js     # Optional: supporting code
```

**SKILL.md format:**
```yaml
---
name: nano-banana-pro
description: Generate or edit images via Gemini 3 Pro Image
metadata: { "openclaw": { "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"] }, "primaryEnv": "GEMINI_API_KEY" } }
---

Instructions in plain English describing behavior, edge cases, and preferences.
The AI reads these instructions and adapts its behavior accordingly.
```

### Skill Precedence (highest to lowest)
1. **Workspace skills** — `<workspace>/skills` (per-agent)
2. **Managed/local skills** — `~/.openclaw/skills` (shared across agents)
3. **Bundled skills** — shipped with install
4. **Extra dirs** — configured via `skills.load.extraDirs`

### Gating (Load-Time Filters)

Skills are filtered at load time based on:
- `requires.bins` — binary must exist on PATH
- `requires.env` — env var must exist or be configured
- `requires.config` — openclaw.json path must be truthy
- `os` — platform filter (darwin, linux, win32)

### Configuration in `openclaw.json`

```json
{
  "skills": {
    "entries": {
      "nano-banana-pro": {
        "enabled": true,
        "apiKey": "GEMINI_KEY_HERE",
        "env": { "GEMINI_API_KEY": "GEMINI_KEY_HERE" }
      },
      "risky-skill": { "enabled": false }
    }
  }
}
```

Environment injection is scoped to the agent run, not the global shell.

### ClawHub (Public Registry)

Browse at https://clawhub.com. Install/sync/update skills:
```bash
clawhub install <skill-slug>
clawhub update --all
clawhub sync --all
```

**Critical warning from OpenClaw docs:** "Treat third-party skills as untrusted code. Read them before enabling."

### Token Impact

Per skill in system prompt: ~97 chars + name + description + location (~24+ tokens each). With many skills loaded, this can consume meaningful context window space.

---

## 3. Security Model — What We're Dealing With

### Documented Threats

| Threat | Description |
|--------|-------------|
| **Prompt Injection** | Malicious content in emails/web pages/docs hijacks agent behavior |
| **Indirect Injection** | Fetched URLs, attachments, pasted content contain hidden instructions |
| **Tool Abuse** | Misconfigured agents cause damage through overly permissive settings |
| **Identity Risks** | Agent sends messages as you, damaging relationships/reputation |
| **Supply Chain** | Malicious skills on ClawHub (already documented: crypto-targeting backdoor skill) |
| **Exposed Instances** | 42K+ instances exposed to public internet with default localhost trust |

### OpenClaw's Built-In Defenses

**Sandboxing (Docker-based):**
```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "enabled": true,
        "scope": "session",
        "workspaceAccess": "none",
        "docker": {
          "setupCommand": "apt-get update && apt-get install -y curl"
        }
      }
    }
  }
}
```

- `scope: "agent"` (default) or `"session"` (stricter, per-session container)
- `workspaceAccess: "none"` (default), `"ro"`, or `"rw"`
- Non-main sessions (groups/channels) can be sandboxed independently

**DM Pairing:**
```json
{
  "channels": {
    "whatsapp": { "dmPolicy": "pairing" }
  }
}
```

**Tool Allow/Deny Lists:**
- Block write, edit, exec, process tools for non-owner agents
- `tools.elevated` is the global escape hatch — keep `allowFrom` tight

**Group Chat Security:**
- Require @mentions (default)
- Group allowlists
- Per-group sandboxing

**Recommended "safe default" config:**
```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "port": 18789,
    "auth": { "mode": "token", "token": "your-long-random-token" }
  },
  "channels": {
    "whatsapp": {
      "dmPolicy": "pairing",
      "groups": { "*": { "requireMention": true } }
    }
  }
}
```

### What OpenClaw Cannot Defend Against

- **Prompt injection from processed content** — emails, web pages, documents. The model cannot reliably distinguish user instructions from injected content. This is an unsolved problem across all AI systems.
- **Model choice matters** — older/legacy models are less robust. OpenClaw recommends Opus 4.5/4.6 for best prompt-injection resistance.
- **Even single-user setups are vulnerable** — if the agent reads untrusted content (web, email, docs), injection can happen regardless of who can message the bot.

---

## 4. Architecture: Secure OpenClaw on Incus with Kimi K2.5

### Why Incus Instead of Docker

| Feature | Docker (OpenClaw default) | Incus |
|---------|--------------------------|-------|
| Isolation level | Process-level containers | Full system containers (own init, systemd) |
| Kernel | Shared (can be escaped) | Shared but with stronger isolation via LXC |
| UID mapping | Manual configuration | Built-in, transparent UID mapping |
| Persistent state | Volume mounts | Native — stop/start preserves everything |
| VM support | Separate tooling | Same CLI, pass `--vm` flag |
| Multi-tenant | Docker Compose | Projects with CPU/memory quotas |
| Nested containers | Limited | Full support on bare metal |
| Cost | Free | Free (open-source) |

Incus gives you **system containers that behave like full Linux machines** — unlike Docker's privileged mode. UID mapping means files created by the agent inside the container are natively owned by your user on the host.

### Why Kimi K2.5 for the Agent Model

| Property | Value | Why It Matters |
|----------|-------|----------------|
| Parameters | 1T MoE, 32B active | Efficient for always-on agent loops |
| Agent Swarm | Up to 100 sub-agents, 1500 parallel tool calls | Built for agentic workloads |
| BrowseComp | 74.9% (vs GPT-5.2's 59.2%) | Web interaction accuracy |
| Multimodal | Native (15T tokens, vision+text co-trained) | Handles screenshots, docs, images natively |
| License | MIT | Full self-hosting, commercial use |
| Input pricing | $0.60/M tokens | ~10-20x cheaper than Opus for always-on use |
| Output pricing | $2.50/M tokens | Cost-effective for chatty agent loops |

**Authentication options:**
1. **Kimi Code plan** — fixed monthly, token cap, predictable cost
2. **Kimi API (kimi.ai)** — pay-as-you-go, international, USD billing
3. **Kimi API (kimi.cn)** — mainland China platform

OpenClaw natively supports Kimi K2.5 via the model configuration:
```json
{
  "models": {
    "default": "moonshot/kimi-k2.5"
  }
}
```

### Proposed Architecture

```
┌──────────────────────────────────────────────────────┐
│  Host Machine (Linux bare metal or VPS)              │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │  Incus Project: "openclaw-prod"                │  │
│  │  (CPU: 4 cores, Memory: 8GB quota)             │  │
│  │                                                │  │
│  │  ┌──────────────────────────────────────────┐  │  │
│  │  │  System Container: "agent-main"          │  │  │
│  │  │  Ubuntu 24.04                            │  │  │
│  │  │                                          │  │  │
│  │  │  ┌──────────────────────────────────┐    │  │  │
│  │  │  │  OpenClaw Gateway (Node.js)      │    │  │  │
│  │  │  │  ├─ Kimi K2.5 API (primary)     │    │  │  │
│  │  │  │  ├─ Opus 4.5 (fallback/complex) │    │  │  │
│  │  │  │  ├─ GPT-5 Nano (heartbeats)     │    │  │  │
│  │  │  │  ├─ Channel adapters             │    │  │  │
│  │  │  │  │  (Telegram, WhatsApp, etc.)   │    │  │  │
│  │  │  │  ├─ Skills (workspace-level)     │    │  │  │
│  │  │  │  ├─ Cron scheduler              │    │  │  │
│  │  │  │  ├─ Docker sandbox (nested)     │    │  │  │
│  │  │  │  │  for tool execution          │    │  │  │
│  │  │  │  └─ Memory (JSONL + MEMORY.md)  │    │  │  │
│  │  │  └──────────────────────────────────┘    │  │  │
│  │  │                                          │  │  │
│  │  │  Workspace: /home/openclaw/workspace     │  │  │
│  │  │  (UID-mapped to host user)               │  │  │
│  │  └──────────────────────────────────────────┘  │  │
│  │                                                │  │
│  │  Network: incusbr0 (bridged, firewall rules)   │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  Tailscale (encrypted remote access, no port expose) │
│  Fail2ban (brute-force protection)                   │
│  UFW (host firewall — only Tailscale + SSH)          │
└──────────────────────────────────────────────────────┘
```

### Setup Steps

#### 1. Install Incus on Host

```bash
# Ubuntu — via Zabbly repo
sudo apt update && sudo apt install -y curl gpg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://pkgs.zabbly.com/key.asc | sudo gpg --dearmor -o /etc/apt/keyrings/zabbly.gpg
# Add repo, install incus
sudo apt install incus
sudo incusadmin init   # accept defaults
```

**On macOS (via Colima):**
```bash
# Incus runs inside Colima VM
colima start --mount /path/to/workspace:w
# SSH in, then install Incus inside
```

#### 2. Configure Networking

```bash
incus network create incusbr0
incus profile device add default eth0 nic network=incusbr0
# Firewall: add bridge to trusted zone, enable IPv4 forwarding
sudo firewall-cmd --zone=trusted --add-interface=incusbr0 --permanent
sudo sysctl -w net.ipv4.ip_forward=1
```

#### 3. Create Isolated Project

```bash
incus project create openclaw-prod \
  -c features.profiles=true \
  -c features.networks=true \
  -c features.storage.volumes=true
incus project switch openclaw-prod

# Set resource limits
incus project set openclaw-prod limits.cpu=4
incus project set openclaw-prod limits.memory=8GB
```

#### 4. Launch Container + Install OpenClaw

```bash
incus launch images:ubuntu/24.04 agent-main
incus exec agent-main -- bash

# Inside container:
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs docker.io
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

#### 5. Configure Security-Hardened openclaw.json

```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "port": 18789,
    "auth": { "mode": "token", "token": "<generate-long-random-token>" }
  },
  "models": {
    "default": "moonshot/kimi-k2.5",
    "fallback": ["anthropic/opus-4.5"],
    "heartbeat": "openrouter/openai/gpt-5-nano"
  },
  "agents": {
    "defaults": {
      "sandbox": {
        "enabled": true,
        "scope": "session",
        "workspaceAccess": "ro"
      },
      "heartbeat": {
        "every": "30m",
        "target": "last",
        "activeHours": { "start": "08:00", "end": "22:00" }
      }
    }
  },
  "channels": {
    "telegram": {
      "dmPolicy": "pairing",
      "groups": { "*": { "requireMention": true } }
    }
  },
  "tools": {
    "elevated": {
      "allowFrom": []
    }
  },
  "skills": {
    "entries": {}
  }
}
```

#### 6. Remote Access via Tailscale

```bash
# On host and your devices
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up --ssh=true
# Access OpenClaw gateway via Tailscale IP — never expose port publicly
```

---

## 5. Useful Elements to Extract from OpenClaw

### Worth Adopting Directly

| Component | What It Does | How to Use |
|-----------|-------------|------------|
| **Skills system** | SKILL.md pattern for teaching agents tool usage | Write your own skills, skip ClawHub third-party |
| **Heartbeat pattern** | Periodic check-ins with HEARTBEAT_OK suppression | Prevents notification spam, cheap model for checks |
| **Cron system** | Scheduled isolated agent turns with channel delivery | Morning briefings, periodic email checks |
| **JSONL transcripts** | Auditable, line-by-line conversation logs | Observability without complex infrastructure |
| **MEMORY.md** | Simple markdown memory, no vector DB needed | Portable, readable, debuggable |
| **Lane Queue** | Serial execution preventing race conditions | Critical for tool execution safety |
| **Model failover** | Primary → fallback with cooldown on provider errors | Cost optimization + reliability |
| **Session isolation** | Per-channel, per-agent session management | Multi-tenant, multi-channel safety |
| **`openclaw doctor`** | Diagnoses misconfigurations and security risks | Run regularly |

### Worth Skipping or Replacing

| Component | Risk/Issue | Alternative |
|-----------|-----------|-------------|
| **ClawHub third-party skills** | Supply chain risk (documented malicious skill) | Write your own skills |
| **Docker sandbox** | Weaker isolation than Incus system containers | Incus containers |
| **Default localhost trust** | Root cause of 42K exposed instances | Token auth + Tailscale |
| **Open DM policies** | Anyone can message and inject prompts | Pairing + allowlists |
| **`tools.elevated`** | Escape hatch that runs exec on host | Keep `allowFrom: []` |

### Operational Best Practices (from Community)

1. **Use cheap models for heartbeats** — GPT-5 Nano costs fractions of a cent for tens of thousands of tokens
2. **Rotate checks on heartbeat** — instead of checking everything every 30 min, track "last checked" timestamps and check the most overdue item each tick
3. **Wire up observability** — Todoist/Notion as task state source of truth, not just logs
4. **Set autonomy limits** — 2-hour max before agent must report back
5. **Log what the agent said last** — prevents repetitive notifications
6. **Cross-reference signals** — new email → check active partnerships in Notion → decide if alert-worthy
7. **Run `openclaw security audit-deep` and `openclaw security audit-fix`** regularly

---

## 6. Cost Model

| Component | Monthly Cost | Notes |
|-----------|-------------|-------|
| Kimi K2.5 API (moderate use) | ~$30-80 | $0.60/M in, $2.50/M out |
| GPT-5 Nano (heartbeats) | ~$1-5 | Fractions of a cent per heartbeat |
| Opus 4.5 (complex tasks, fallback) | ~$20-50 | Use sparingly, strong injection resistance |
| Incus | Free | Open source |
| Tailscale | Free (personal) | Encrypted remote access |
| VPS (Hetzner CX23 or similar) | ~$5-15 | If not running on local hardware |
| **Total** | **~$60-150** | vs. $150-5000 for typical OpenClaw Opus-only setups |

---

## 7. Key References

- **OpenClaw Docs:** https://docs.openclaw.ai
- **OpenClaw Security:** https://docs.openclaw.ai/gateway/security
- **OpenClaw Skills:** https://docs.openclaw.ai/tools/skills
- **Trust Program:** https://trust.openclaw.ai
- **Incus (Code on Incus):** https://github.com/code-on-incus
- **Kimi K2.5 API:** https://platform.moonshot.ai
- **Community guide (cost optimization):** https://gist.github.com/digitalknk/ec360aab27ca47cb4106a183b2c25a98
