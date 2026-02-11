# MCP Client

## Description
Interact with MCP (Model Context Protocol) servers without bloating context. Converts any MCP into a skill-compatible interface. Use when user needs external services like Gmail, Calendar, Slack, Asana, etc.

## Triggers
- "check my email"
- "look at my calendar"
- "what's in asana"
- "what meetings do I have"
- "check slack"
- Any request involving configured MCP services

## Safety Rules

### Default: READ ONLY
Only read operations are enabled by default:
- Search emails
- List calendar events
- View tasks
- Read slack messages

### Requires Explicit Confirmation
Before any write operation, confirm with user:
- Send email → "Should I send this email to [recipient]?"
- Create event → "Should I create this calendar event?"
- Post message → "Should I post this to [channel]?"

Never auto-send, auto-create, or auto-modify without explicit "yes".

## Configuration

MCP servers are defined in `mcp-config.example.json` in this skill folder. Copy to `mcp-config.json` and configure.

## Workflow

1. **Identify Server** — Based on user's request, determine which MCP server is relevant
2. **Discover Tools** — List available tools if unsure which to use
3. **Call Tool** — Execute with appropriate parameters
4. **Parse and Present** — Format results clearly for user

## Adding New MCPs

1. Edit `mcp-config.json` to add server details
2. Test connection
3. Document gotchas in `.claude/claude.md` under MCP Gotchas section

## Error Handling

- **Server not found:** List available servers, suggest configuration
- **Auth failure:** Prompt user to check credentials
- **Rate limited:** Wait and retry, notify user if persistent
- **Timeout:** Retry once, then report failure
