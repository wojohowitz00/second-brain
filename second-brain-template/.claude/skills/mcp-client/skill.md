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

## Why This Skill Exists

MCP servers expose many tools with detailed parameters, which can overwhelm the context window if loaded directly. This skill:
1. Keeps MCP tool descriptions out of main context
2. Loads tools on-demand when needed
3. Provides consistent interface across different MCPs

## Configuration

MCP servers are defined in `mcp-config.json` in this skill folder:

```json
{
  "servers": {
    "zapier": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-zapier"],
      "env": {
        "ZAPIER_API_KEY": "${ZAPIER_API_KEY}"
      }
    },
    "google-calendar": {
      "command": "node",
      "args": ["/path/to/calendar-server/index.js"],
      "env": {
        "GOOGLE_CLIENT_ID": "${GOOGLE_CLIENT_ID}",
        "GOOGLE_CLIENT_SECRET": "${GOOGLE_CLIENT_SECRET}"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}"
      }
    }
  }
}
```

## Usage

### List Available Servers
```bash
python3 mcp_client.py list-servers
```
Shows all configured MCP servers.

### List Tools in a Server
```bash
python3 mcp_client.py list-tools --server zapier
```
Shows available tools and their parameters for a specific server.

### Call a Tool
```bash
python3 mcp_client.py call --server zapier --tool gmail_search --args '{"query": "is:unread"}'
```
Executes a tool with provided arguments.

## Workflow

### 1. Identify Server
Based on user's request, determine which MCP server is relevant:
- Email → gmail/zapier
- Calendar → google-calendar/zapier
- Tasks → asana/zapier
- Chat → slack

### 2. Discover Tools (if needed)
If unsure which tool to use:
```bash
python3 mcp_client.py list-tools --server [server]
```

### 3. Call Tool
Execute with appropriate parameters:
```bash
python3 mcp_client.py call --server [server] --tool [tool] --args '[json]'
```

### 4. Parse and Present
Format results clearly for user.

## Safety Rules

### Default: READ ONLY
Only read operations are enabled by default:
- ✅ Search emails
- ✅ List calendar events
- ✅ View tasks
- ✅ Read slack messages

### Requires Explicit Confirmation
Before any write operation, confirm with user:
- ❌ Send email → "Should I send this email to [recipient]?"
- ❌ Create event → "Should I create this calendar event?"
- ❌ Post message → "Should I post this to [channel]?"
- ❌ Complete task → "Should I mark this as done?"

Never auto-send, auto-create, or auto-modify without explicit "yes".

## Common Patterns

### "What's on my calendar today?"
```bash
python3 mcp_client.py call --server google-calendar --tool list_events --args '{"date": "today"}'
```
Then format as readable list.

### "Check email for anything from [person]"
```bash
python3 mcp_client.py call --server zapier --tool gmail_search --args '{"query": "from:[person]"}'
```
Summarize results, highlight important items.

### "What tasks are due in Asana?"
```bash
python3 mcp_client.py call --server zapier --tool asana_search_tasks --args '{"filter": "due_today"}'
```
Present as checklist.

### "Any new Slack messages?"
```bash
python3 mcp_client.py call --server slack --tool read_messages --args '{"channel": "general", "limit": 10}'
```
Summarize conversation threads.

## Adding New MCPs

### Step 1: Add Configuration
Edit `mcp-config.json` to add server details.

### Step 2: Test Connection
```bash
python3 mcp_client.py list-tools --server [new-server]
```

### Step 3: Document Gotchas
After testing, run:
"Go through all tools in [server] and document any gotchas"

Add discoveries to global `claude.md` under MCP Gotchas section.

### Step 4: Update This Skill (Optional)
Add common patterns for the new server.

## Error Handling

- **Server not found:** List available servers, suggest configuration
- **Tool not found:** List available tools for that server
- **Auth failure:** Prompt user to check credentials in environment
- **Rate limited:** Wait and retry, notify user if persistent
- **Timeout:** Retry once, then report failure

## Integration Notes

This skill works alongside the inbox-processor and daily-digest skills:
- Inbox processor can pull from Slack MCP
- Daily digest can include calendar via this skill
- Research engine can forward interesting papers via email MCP

Keep MCPs for external services, keep core second brain in local Obsidian files.
