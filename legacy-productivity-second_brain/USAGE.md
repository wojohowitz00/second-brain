---
category:
- '[[App Development]]'
- '[[Coding with AI]]'
tags:
- personal
- projects
created: '2026-01-28'
updated: '2026-01-28'
---
# Second Brain App - User Guide

Complete guide to using the Second Brain macOS app for capturing and organizing your thoughts.

## Table of Contents

1. [First-Time Setup](#first-time-setup)
2. [Daily Usage](#daily-usage)
3. [Features Overview](#features-overview)
4. [Settings Configuration](#settings-configuration)
5. [Tips & Best Practices](#tips--best-practices)
6. [Troubleshooting](#troubleshooting)

---

## First-Time Setup

### Step 1: Install Python Dependencies

```bash
cd ~/SecondBrain/_scripts
pip3 install -r requirements.txt
```

Or if you're using the project directory:

```bash
cd /Users/richardyu/PARA/1_projects/coding/second_brain/_scripts
pip3 install -r requirements.txt
```

### Step 2: Launch the App

1. Open the app in Xcode
2. Press **⌘R** to build and run
3. The app window will appear

### Step 3: Configure Settings

#### Slack Configuration

1. Go to **Settings → Slack**
2. Enter your credentials:
   - **Bot Token**: Your Slack bot token (starts with `xoxb-`)
   - **Channel ID**: The ID of your `#wry_sb` channel
   - **User ID**: Your Slack user ID
3. Click **Test Connection** to verify
4. Click **Save**

**How to get these values:**
- **Bot Token**: Create a Slack app at https://api.slack.com/apps, install it to your workspace, copy the "Bot User OAuth Token"
- **Channel ID**: Right-click your channel in Slack → View channel details → Copy the Channel ID (starts with `C`)
- **User ID**: Right-click your profile in Slack → Copy member ID (starts with `U`)

#### LLM Configuration

1. Go to **Settings → LLM**
2. Select your provider:
   - **Anthropic Claude**: Cloud API (requires API key)
   - **OpenAI**: Cloud API (requires API key)
   - **Ollama**: Local model (no API key needed)
   - **LM Studio**: Local model (no API key needed)
3. Configure based on your choice:

   **For Cloud APIs (Anthropic/OpenAI):**
   - Enter your **API Key**
   - Select a **Model** from the dropdown
   - Click **Test Connection**
   - Click **Save**

   **For Local Models (Ollama/LM Studio):**
   - Enter **API Endpoint** (defaults shown)
   - Click **Refresh Models** to load available models
   - Select a **Model** from the dropdown
   - Click **Test Connection**
   - Click **Save**

**Ollama Setup:**
```bash
# Install Ollama from https://ollama.ai
# Pull a model:
ollama pull llama2
# Or:
ollama pull mistral
```

**LM Studio Setup:**
1. Download from https://lmstudio.ai
2. Download a model in LM Studio
3. Start the local server (usually runs on port 1234)

#### Obsidian Configuration

1. Go to **Settings → Obsidian**
2. Click **Browse...**
3. Select your Obsidian vault folder (usually `~/SecondBrain`)
4. Verify the folder structure is detected
5. Click **Save**

**Expected folder structure:**
```
SecondBrain/
├── people/
├── projects/
├── ideas/
├── admin/
├── daily/
└── _inbox_log/
```

---

## Daily Usage

### Starting the Background Service

1. Open the **Dashboard** tab
2. Click **Start** in the "Background Service" section
3. The app will now automatically:
   - Check for new Slack messages every 2 minutes
   - Classify and file them into your Obsidian vault
   - Run health checks periodically

### Capturing Thoughts

1. Post a message to your `#wry_sb` Slack channel
2. The app will automatically:
   - Detect the new message (within 2 minutes)
   - Classify it (person/project/idea/admin)
   - Create a Markdown file in the appropriate folder
   - Reply in Slack with confirmation and confidence score

**Example Slack message:**
```
Had a great conversation with Sarah about the new product launch timeline
```

**Result:**
- File created: `people/sarah.md` or `projects/product-launch.md`
- Slack reply: "✅ Filed to projects/product-launch.md (confidence: 0.92)"

### Manual Actions

From the **Dashboard**, you can trigger manual actions:

- **Process Inbox**: Immediately process all unprocessed messages
- **Health Check**: Verify system health and connectivity
- **Daily Digest**: Generate a summary of today's captured thoughts
- **Weekly Review**: Generate a weekly summary (run on Sundays)

### Viewing Your Vault

1. Go to **Vault** tab
2. Select a folder from the sidebar (people/projects/ideas/admin/daily)
3. Click a file to view its contents
4. Files are organized by classification

### Monitoring Logs

1. Go to **Logs** tab
2. View real-time processing logs
3. Filter by type:
   - **All**: All logs
   - **Processing**: Message processing logs
   - **Health**: Health check logs
   - **Fixes**: Error recovery logs
4. Use **Search** to find specific entries
5. Click **Export** to save logs to a file

### Viewing Messages

1. Go to **Messages** tab
2. See all messages from your inbox channel
3. Click a message to view:
   - Full message text
   - Classification result (if processed)
   - Confidence score
   - Destination filename
4. Click **Refresh** to reload messages

---

## Features Overview

### Dashboard

- **System Status**: Shows if the system is healthy
- **Quick Stats**: Last success time, failure count, service status
- **Quick Actions**: One-click access to common tasks
- **Background Service Control**: Start/stop automated processing

### Messages View

- Browse all Slack messages from your inbox
- See processing status for each message
- View classification details
- Manually trigger classification if needed

### Vault Browser

- Navigate your Obsidian vault structure
- View file contents
- Organized by folder (people/projects/ideas/admin/daily)

### Logs View

- Real-time log streaming
- Filter by log type
- Search functionality
- Export logs for debugging

### Settings

- **Slack**: Configure bot token, channel ID, user ID
- **LLM**: Choose provider, configure API keys/endpoints, select models
- **Obsidian**: Set vault path

---

## Settings Configuration

### Slack Settings

**Required:**
- Bot Token: OAuth token from your Slack app
- Channel ID: Your inbox channel ID
- User ID: Your Slack user ID

**Testing:**
- Click "Test Connection" to verify credentials
- Green checkmark = success
- Red X = check your credentials

### LLM Settings

**Cloud Providers (Anthropic/OpenAI):**
- Requires API key from provider
- Select model from dropdown
- Test connection before saving

**Local Providers (Ollama/LM Studio):**
- No API key needed
- Set endpoint (defaults work for localhost)
- Click "Refresh Models" to load available models
- Select model from dropdown

**Model Recommendations:**
- **Anthropic**: `claude-3-opus-20240229` (best), `claude-3-sonnet-20240229` (faster)
- **OpenAI**: `gpt-4-turbo-preview` (best), `gpt-3.5-turbo` (faster)
- **Ollama**: `llama2`, `mistral`, `codellama`
- **LM Studio**: Any compatible model you've downloaded

### Obsidian Settings

**Vault Path:**
- Default: `~/SecondBrain`
- Click "Browse..." to select a different vault
- App validates folder structure on save

**Required Folders:**
- `people/` - For person-related thoughts
- `projects/` - For project-related thoughts
- `ideas/` - For idea-related thoughts
- `admin/` - For administrative thoughts
- `daily/` - For daily digests
- `_inbox_log/` - For processing logs

---

## Tips & Best Practices

### Writing Effective Messages

**Good messages:**
- Clear and specific: "Met with John about Q2 roadmap"
- Include context: "Sarah mentioned the API is ready for testing"
- Action items: "Need to follow up with Mike about budget approval"

**Less effective:**
- Too vague: "Had a meeting"
- Missing context: "Talked about the thing"
- Too long: Multi-paragraph messages (split into multiple messages)

### Organizing Your Vault

- **People**: Use full names or consistent nicknames
- **Projects**: Use descriptive project names
- **Ideas**: Be specific about the idea
- **Admin**: Tasks, reminders, system notes

### Background Service

- **Keep it running**: The app works best when the background service is active
- **Check logs regularly**: Monitor for errors or issues
- **Health checks**: Run manual health checks if something seems off

### Performance Tips

- **Local models**: Faster for privacy, but require powerful hardware
- **Cloud models**: More reliable, but require internet and API costs
- **Batch processing**: The app processes messages in batches for efficiency

### Privacy & Security

- **API keys**: Stored securely in macOS Keychain
- **Local models**: Keep your data completely private
- **Cloud models**: Data sent to provider (check their privacy policy)

---

## Troubleshooting

### App Won't Start

**Symptoms:** App crashes on launch or won't open

**Solutions:**
1. Check Console.app for error messages
2. Verify Python dependencies are installed: `pip3 list | grep anthropic`
3. Ensure vault path exists: `ls ~/SecondBrain`
4. Rebuild in Xcode: **Product → Clean Build Folder** (⇧⌘K), then **⌘R**

### Messages Not Processing

**Symptoms:** Messages appear in Slack but aren't being filed

**Solutions:**
1. Check if background service is running (Dashboard)
2. Verify Slack credentials (Settings → Slack → Test Connection)
3. Check logs (Logs tab) for error messages
4. Verify channel ID is correct
5. Ensure bot has permission to read the channel

### LLM Connection Fails

**Symptoms:** "Test Connection" fails or classification errors

**Solutions:**
- **Cloud APIs:**
  1. Verify API key is correct
  2. Check API key hasn't expired
  3. Verify you have credits/quota
  4. Check internet connection

- **Local Models:**
  1. Verify Ollama/LM Studio is running
  2. Check endpoint URL (default: `http://localhost:11434` for Ollama)
  3. Ensure a model is downloaded
  4. Try "Refresh Models" button

### Can't Find Vault

**Symptoms:** "Vault path does not exist" or files not showing

**Solutions:**
1. Verify vault path in Settings → Obsidian
2. Check folder structure exists
3. Ensure you have read/write permissions
4. Try selecting the vault path again

### Python Script Errors

**Symptoms:** "Python script not found" or execution errors

**Solutions:**
1. Verify scripts exist: `ls ~/SecondBrain/_scripts/`
2. Check Python version: `python3 --version` (needs 3.9+)
3. Verify dependencies: `pip3 install -r ~/SecondBrain/_scripts/requirements.txt`
4. Check script permissions: `chmod +x ~/SecondBrain/_scripts/*.py`

### Background Service Stops

**Symptoms:** Service stops running unexpectedly

**Solutions:**
1. Check logs for error messages
2. Verify all settings are saved correctly
3. Restart the app
4. Check system resources (memory/CPU)
5. Verify Python scripts are accessible

### Classification Errors

**Symptoms:** Messages classified incorrectly or with low confidence

**Solutions:**
1. Try a different LLM model
2. Improve message clarity (see Tips section)
3. Check LLM provider status
4. Review classification examples in logs
5. Consider fine-tuning your prompts (advanced)

### Export/Import Issues

**Symptoms:** Can't export logs or import settings

**Solutions:**
1. Check file permissions
2. Verify disk space available
3. Try a different save location
4. Check macOS security settings

---

## Advanced Usage

### Custom Classification

The app uses LLM classification by default. To customize:

1. Edit `_scripts/process_inbox.py`
2. Modify the classification prompt
3. Restart the background service

### Scheduled Tasks

The app runs these automatically:
- **Every 2 minutes**: Process inbox
- **Every hour**: Health check
- **Daily**: Generate digest (if enabled)
- **Weekly**: Generate review (if enabled)

### Integration with Obsidian

The app creates files with:
- **Frontmatter**: YAML metadata (tags, dates, links)
- **Wikilinks**: Auto-generated `[[links]]` to related entities
- **Templates**: Uses templates from `_templates/` folder

### Backup & Restore

**Backup:**
- Vault: Copy your `~/SecondBrain` folder
- Settings: Export from Keychain Access app
- Logs: Export from Logs tab

**Restore:**
- Vault: Copy folder back
- Settings: Re-enter in app (stored in Keychain)
- Logs: Import if needed

---

## Getting Help

- **Check logs**: Most issues are visible in the Logs tab
- **Console.app**: System-level errors appear here
- **Health check**: Run from Dashboard to diagnose issues
- **GitHub Issues**: Report bugs or request features

---

## Keyboard Shortcuts

- **⌘R**: Build and run (Xcode)
- **⌘Q**: Quit app
- **⌘W**: Close window
- **⌘,**: Open Settings (if implemented)
- **⌘F**: Search (in Logs/Messages views)

---

## Version Information

Check app version in:
- Xcode: Project settings → General → Version
- About menu: SecondBrain → About SecondBrain

---

**Happy capturing! 🧠✨**
