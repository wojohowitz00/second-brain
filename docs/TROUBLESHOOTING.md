# Second Brain Troubleshooting Guide

Solutions for common issues with Second Brain.

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Ollama Issues](#ollama-issues)
4. [Slack Issues](#slack-issues)
5. [Classification Issues](#classification-issues)
6. [File Creation Issues](#file-creation-issues)
7. [Menu Bar Issues](#menu-bar-issues)
8. [Performance Issues](#performance-issues)
9. [Getting Help](#getting-help)

---

## Quick Diagnostics

### Check Health Status

Click the menu bar icon → **Health** to see:
- Ollama status
- Vault connection
- Slack connection

### Run Diagnostic Commands

```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check model
ollama list | grep llama3.2

# Check Slack credentials
cd backend/_scripts && cat .env | head -3

# Check vault exists
ls -la ~/PARA/.obsidian/

# Check recent logs
cat /tmp/secondbrain.err.log | tail -20
```

### Run Test Suite

```bash
cd backend
uv run pytest -v --tb=short
```

All 259 tests should pass.

---

## Installation Issues

### "App can't be opened because it is from an unidentified developer"

**Cause:** App is not code-signed with Apple Developer ID.

**Solution:**
1. Right-click the app → **Open**
2. Click **Open** in the dialog
3. Or: System Preferences → Security & Privacy → Click "Open Anyway"

### "Second Brain.app is damaged and can't be opened"

**Cause:** Gatekeeper quarantine flag.

**Solution:**
```bash
xattr -cr /Applications/Second\ Brain.app
```

### Installer fails with "permission denied"

**Cause:** Need admin privileges.

**Solution:**
```bash
sudo installer -pkg pkg/SecondBrain-1.0.0.pkg -target /
```

### App doesn't appear after installation

**Cause:** App might be running but hidden.

**Solution:**
1. Check menu bar for 🧠 icon
2. Check Activity Monitor for "Second Brain" process
3. Try launching manually:
   ```bash
   open /Applications/Second\ Brain.app
   ```

---

## Ollama Issues

### "Ollama is not running"

**Symptoms:**
- Menu bar shows ⚠️
- Health check shows "Ollama: ✗"

**Solutions:**

1. **Start Ollama:**
   ```bash
   ollama serve
   ```

2. **Check if running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. **Restart Ollama:**
   ```bash
   pkill ollama
   ollama serve
   ```

### "Model not found"

**Symptoms:**
- Classification fails
- Error: "model 'llama3.2:latest' not found"

**Solution:**
```bash
# List available models
ollama list

# Pull the model
ollama pull llama3.2:latest

# Verify
ollama list | grep llama3.2
```

### Classification times out

**Symptoms:**
- Sync takes forever
- No response from classification

**Causes:**
- Ollama under heavy load
- Model still loading (cold start)
- Insufficient RAM

**Solutions:**

1. **Wait for warm-up:** First classification after Ollama starts takes ~30 seconds.

2. **Check RAM usage:**
   ```bash
   top -l 1 | grep ollama
   ```
   llama3.2 needs ~4GB RAM.

3. **Restart Ollama:**
   ```bash
   pkill ollama
   ollama serve
   ```

4. **Use smaller model (if RAM limited):**
   Edit `.env`:
   ```
   OLLAMA_MODEL=llama3.2:1b
   ```

### Ollama crashes frequently

**Cause:** Insufficient system resources.

**Solutions:**
1. Close other applications
2. Increase swap space
3. Use a smaller model variant
4. Check macOS Console.app for crash logs

---

## Slack Issues

### "Invalid authentication"

**Symptoms:**
- Health shows "Slack: ✗"
- Error: "invalid_auth"

**Causes:**
- Token expired or revoked
- Wrong token type

**Solutions:**

1. **Verify token format:**
   ```bash
   cat backend/_scripts/.env | grep SLACK_BOT_TOKEN
   # Should start with xoxb-
   ```

2. **Regenerate token:**
   - Go to https://api.slack.com/apps
   - Select your app
   - OAuth & Permissions → Reinstall to Workspace
   - Copy new token

3. **Check permissions:**
   Bot needs: `channels:history`, `channels:read`, `chat:write`

### "Channel not found"

**Symptoms:**
- No messages fetched
- Error: "channel_not_found"

**Solutions:**

1. **Verify Channel ID:**
   ```bash
   cat backend/_scripts/.env | grep SLACK_CHANNEL_ID
   # Should start with C
   ```

2. **Check bot is in channel:**
   - In Slack: `/invite @Second Brain`

3. **Check channel visibility:**
   - Bot can only access channels it's been invited to

### "Rate limited"

**Symptoms:**
- Intermittent failures
- Error: "ratelimited"

**Cause:** Too many API calls.

**Solution:** This is handled automatically. The app backs off and retries. If persistent:
- Reduce poll frequency (edit `POLL_INTERVAL_SECONDS` in code)
- Check for duplicate app instances

### Messages not being processed

**Symptoms:**
- Posted to Slack but nothing filed
- No errors in Health

**Solutions:**

1. **Check message timestamp:**
   - Only processes messages newer than last processed
   - State stored in `backend/_scripts/.state/.last_processed_ts`

2. **Reset processing state:**
   ```bash
   rm backend/_scripts/.state/.last_processed_ts
   ```
   Then click **Sync Now**.

3. **Check message format:**
   - Bot messages are ignored
   - Empty messages are skipped

---

## Classification Issues

### Wrong domain classification

**Symptoms:**
- Messages filed in wrong domain folder

**Solutions:**

1. **Add context to messages:**
   ```
   ❌ "Meeting notes"
   ✅ "Work meeting notes: discussed Q2 budget with finance team"
   ```

2. **Use explicit domain indicator:**
   ```
   domain:work Meeting notes from standup
   ```

3. **Check vault structure:**
   ```bash
   ls ~/PARA/
   ```
   Domain names come from your folder names.

### Wrong PARA type

**Symptoms:**
- Projects filed as Resources, etc.

**Solution:** Use explicit indicators or be more descriptive:
```
todo: Finish the MVP for project Apollo domain:work
```

The word "project" and action-oriented language helps.

### Low confidence scores

**Symptoms:**
- Confidence < 0.5 frequently
- Random-seeming classifications

**Causes:**
- Vague messages
- Missing vault vocabulary
- Model confusion

**Solutions:**

1. **Be more specific:**
   ```
   ❌ "Stuff"
   ✅ "Research notes on Kubernetes operators for database project"
   ```

2. **Rescan vault:**
   - Click menu bar → **Health** → vault should show domain count
   - If domains missing, restart app to rescan

3. **Create target folders:**
   If you often mention "recipes" but have no `Resources/recipes/` folder, create it.

### Classification returns defaults

**Symptoms:**
- Everything goes to `Personal/Resources/general`

**Cause:** LLM response parsing failed.

**Solutions:**

1. **Check Ollama logs:**
   ```bash
   cat /tmp/secondbrain.err.log | grep -i error
   ```

2. **Test classification manually:**
   ```bash
   cd backend
   uv run python -c "
   import sys; sys.path.insert(0, '_scripts')
   from message_classifier import MessageClassifier
   mc = MessageClassifier()
   result = mc.classify('Test message about work projects')
   print(result)
   "
   ```

3. **Restart Ollama:**
   ```bash
   pkill ollama && ollama serve
   ```

---

## File Creation Issues

### Files not appearing in vault

**Symptoms:**
- Slack shows "Filed to..." but file not found

**Solutions:**

1. **Check exact path:**
   ```bash
   find ~/PARA -name "*.md" -mmin -5
   ```

2. **Check folder exists:**
   ```bash
   ls ~/PARA/Personal/1_Projects/
   ```
   If subject folder doesn't exist, file may be in parent.

3. **Check Obsidian indexing:**
   - Obsidian may take a moment to index new files
   - Press Cmd+Shift+F to search

### Permission denied

**Symptoms:**
- Error: "Permission denied" writing to vault

**Solutions:**

1. **Check folder permissions:**
   ```bash
   ls -la ~/PARA/
   ```
   You need write access.

2. **Check disk space:**
   ```bash
   df -h ~
   ```

3. **Check if vault is on network drive:**
   Network drives may have different permissions.

### Duplicate files

**Symptoms:**
- Same message creates multiple files

**Cause:** Processing state corrupted.

**Solution:**
```bash
# View processed message IDs
cat backend/_scripts/.state/.last_processed_ts

# Reset if needed (will reprocess recent messages)
rm backend/_scripts/.state/.last_processed_ts
```

---

## Menu Bar Issues

### Icon not appearing

**Symptoms:**
- App running but no menu bar icon

**Solutions:**

1. **Check menu bar space:**
   - Too many icons can hide new ones
   - Try Cmd+drag to rearrange

2. **Check Activity Monitor:**
   - Search for "Second Brain"
   - If running, try quitting and restarting

3. **Check for crashes:**
   ```bash
   cat /tmp/secondbrain.err.log | tail -50
   ```

### Menu not responding

**Symptoms:**
- Click icon but menu doesn't open

**Solution:**
1. Quit and restart the app
2. If persists, reboot your Mac

### Wrong status icon

**Symptoms:**
- Shows error (⚠️) but everything works

**Solution:**
- Click **Health** to see actual status
- Icon updates every 30 seconds; may lag

---

## Performance Issues

### High CPU usage

**Symptoms:**
- Second Brain using >10% CPU idle

**Causes:**
- Excessive polling
- Memory pressure

**Solutions:**

1. **Check for runaway process:**
   ```bash
   top -l 1 | grep -i second
   ```

2. **Restart the app:**
   Quit from menu bar and relaunch.

3. **Check for multiple instances:**
   ```bash
   pgrep -f "Second Brain" | wc -l
   ```
   Should be 1.

### High memory usage

**Symptoms:**
- App using >500MB RAM

**Cause:** Memory leak or accumulated state.

**Solution:** Restart the app periodically, or:
```bash
# Clear cache
rm backend/_scripts/.state/vault_cache.json
```

### Slow sync

**Symptoms:**
- Sync takes >1 minute

**Causes:**
- Many unprocessed messages
- Ollama cold start
- Network issues

**Solutions:**

1. **First sync is slow:** Ollama model loads into RAM.

2. **Process in batches:** If hundreds of messages backed up:
   ```bash
   # Reset to only process new messages
   date +%s > backend/_scripts/.state/.last_processed_ts
   ```

3. **Check network:**
   ```bash
   curl -I https://slack.com
   ```

---

## Getting Help

### Collect Diagnostic Info

```bash
# System info
sw_vers
uname -a

# Ollama version
ollama --version

# Python version
cd backend && uv run python --version

# Recent errors
cat /tmp/secondbrain.err.log | tail -100

# Test suite
uv run pytest -v 2>&1 | tail -50
```

### Log Locations

| Log | Location |
|-----|----------|
| Stdout | `/tmp/secondbrain.out.log` |
| Stderr | `/tmp/secondbrain.err.log` |
| State | `backend/_scripts/.state/` |

### Report an Issue

When reporting issues, include:
1. macOS version
2. Error messages
3. Steps to reproduce
4. Diagnostic output above

---

*Last updated: 2026-01-31 | Version: v1.0.0*
