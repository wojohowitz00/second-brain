I have analyzed the tutorial content and the provided resources. Below is the practitioner-quality guide designed for implementation by **Claude Code**.

# **Tutorial Guide: AI-Powered Knowledge Management with Obsidian & Claude Code**

## **1\. Summary**

This guide details how to implement a "Second Brain" knowledge management system by integrating **Obsidian** (a local Markdown-based note-taking app) with **Claude Code** (Anthropic’s agentic CLI). This setup allows an AI to index, reason across, and edit thousands of personal notes (journals, research, manuscripts) directly on your local file system. It solves the "fragmented knowledge" problem by providing a 200k+ (up to 1M) token context window that can maintain world-building consistency, automate line-editing, and find novel connections across decades of data.

## ---

**2\. Source**

| Field | Details |
| :---- | :---- |
| Title | What Happens When AI Can Read 20 Years of Your Notes |
| Author / Publisher | Ser / Aligned Intelligence |
| URL | [https://www.youtube.com/watch?v=2ykBMhIsdL4](https://www.youtube.com/watch?v=2ykBMhIsdL4) |
| Retrieved | March 19, 2026 |
| Format | Video Transcript & Supplemental Articles |

## ---

**3\. Tools & Technologies**

| Tool | Version | Purpose | Documentation |
| :---- | :---- | :---- | :---- |
| **Obsidian** | latest | Local-first markdown knowledge base | [Docs](https://help.obsidian.md/) |
| **Node.js** | 18.x+ | Runtime required to run Claude Code | [Docs](https://nodejs.org/) |
| **Claude Code** | latest | CLI agent for file manipulation & reasoning | [Docs](https://code.claude.com/) |
| **git** | latest | Version control for your notes (highly recommended) | [Docs](https://git-scm.com/) |

⚠️ **Pin this version in production:** Ensure Node.js is at least v18 for Claude Code compatibility.

## ---

**4\. Project Structure**

This structure assumes a standard Obsidian Vault layout where Claude Code operates from the root.

my-second-brain/ (Vault Root)  
├── .claude.json         \# Claude Code configuration  
├── .gitignore           \# Exclude system files from AI indexing  
├── Inbox/               \# New, unsorted notes/scraps  
├── Journal/             \# Daily notes and logs  
├── Projects/            \# Active writing or creative work  
│   └── Book-Draft/  
├── Resources/           \# Reference material and highlights  
└── \_templates/          \# Obsidian note templates

## ---

**5\. Prerequisites & Environment Setup**

### **5a. Required Knowledge**

* Basic terminal navigation (cd, ls, mkdir).  
* Fundamental Markdown syntax (headers, links, code blocks).  
* Understanding of "Context Windows" (how much data the AI can "see" at once).

### **5b. Environment Setup**

Run these commands to prepare your local machine for the integration.

Bash

\# 1\. Install Node.js (using nvm is recommended if not installed)  
\# Download at https://nodejs.org/

\# 2\. Install Claude Code globally  
npm install \-g @anthropic-ai/claude-code

\# 3\. Navigate to your Obsidian Vault directory  
cd \~/Documents/My-Obsidian-Vault

\# 4\. Initialize Claude Code in this directory  
claude init

### **5c. Verification**

Confirm the environment is ready:

Bash

claude \--version  
node \--version  
\# Ensure you are inside your vault directory  
ls \-a | grep ".obsidian"

## ---

**6\. Implementation Checklist**

* \[ \] Step 1: Initialize the Obsidian Vault  
* \[ \] Step 2: Install the Terminal Plugin in Obsidian  
* \[ \] Step 3: Authenticate and Configure Claude Code  
* \[ \] Step 4: Batch Convert Legacy Files (Word/PDF to MD)  
* \[ \] Step 5: Establish the "Worldview" Consistency Check  
* \[ \] Final: Execute an End-to-End Creative Task

## ---

**7\. Step-by-Step Implementation**

### **Step 1: Initialize the Obsidian Vault**

**Goal:** Create the local environment where the notes reside.

**Action:** Download and install Obsidian. Create a new "Vault" pointing to a dedicated folder on your hard drive.

### **Step 2: Install Terminal Plugin**

**Goal:** Allow Claude Code to be accessible within the Obsidian UI.

**Action:** 1\. In Obsidian: Settings \> Community Plugins \> Browse.

2\. Search for "Terminal" or "Obsidian Shell".

3\. Install and Enable.

4\. Open the terminal pane within Obsidian.

### **Step 3: Configure Claude Code**

**Goal:** Link your Anthropic account and set permissions.

**Action:**

Run the login command and follow the browser prompts.

Bash

claude login

⚠️ **Gap:** The tutorial does not mention CLAUDE\_CONFIG\_DIR. For portability, ensure your config is accessible to the terminal plugin.

### **Step 4: Batch Convert Legacy Files**

**Goal:** Convert old .docx or .txt files into Obsidian-readable .md files.

**Action:** Ask Claude Code to perform the migration.

Bash

\# Inside the vault terminal  
claude "Find all .txt and .docx files in /Resources, convert their content to .md format, and delete the originals."

**Pros:** Rapidly ingests 20 years of legacy data.

**Cons:** Formatting in complex Word docs may require manual cleanup.

### **Step 5: Establish Worldview Consistency**

**Goal:** Use the 1M token context window to ensure new writing matches existing lore.

**Action:** Create a "Cosmology" or "Reference" file and point Claude to it.

Bash

\# Example command  
claude "Read Projects/Book-Draft/Cosmology.md. Now check Chapter-5.md for any logic or consistency errors based on that cosmology."

**Validation:**

Bash

\# Claude should return a list of specific inconsistencies with page/line references.

## ---

**8\. End-to-End Example: "The Memoir Editor"**

Use this prompt to replicate the author's success with compiling scattered memoirs:

Bash

claude "1. Search my entire vault for notes tagged \#memoir or mentioning 'Dad'.   
2\. Summarize the chronological order of these events.   
3\. Create a new file 'Projects/Memoir-Manuscript.md'.   
4\. Compile the text from those notes into this file.   
5\. Perform a line-edit on the entire manuscript in the style of Steven Pinker's 'Sense of Style', focusing on clarity and removing 'zombie nouns'."

## ---

**9\. Troubleshooting**

| Error / Symptom | Likely Cause | Fix |
| :---- | :---- | :---- |
| Command not found: claude | Path not updated after npm install | Restart terminal or run source \~/.zshrc |
| Context window exceeded | Vault too large for standard model | Use claude \--model claude-3-7-sonnet (or latest) |
| Files not appearing in Obsidian | File extension is not .md | Rename files to include .md suffix |

## ---

**10\. Key Takeaways**

* **Local-First AI:** Claude Code works on your *files*, not just a chat window. Changes are reflected in Obsidian immediately.  
* **The "Second Brain" Context:** The value scales with the volume of data; 20,000 notes provide a unique "aligned worldview" for the AI.  
* **Agentic Workflow:** Don't just ask questions; give Claude Code *permission* to create, move, and edit files to organize your knowledge.

## ---

**11\. Further Reading**

* [Official Claude Code Documentation](https://code.claude.com/docs)  
* [Obsidian Beginners Guide](https://www.google.com/search?q=https://obsidian.md/help)  
* [Steven Pinker's 'A Sense of Style' Summary](https://stevenpinker.com/publications/sense-style-thinking-persons-guide-writing-21st-century)

---

**Filename:** guide\_obsidian-claude-code-setup\_2026-03-19.md