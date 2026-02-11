# Research Engine

## Description
Automated research pipeline for staying current on topics. Includes daily searches of academic sources (arXiv, Google Scholar), digest generation, and paper summarization. Helps user stay informed without manual searching.

## Triggers
- Part of /today command (digest review)
- "search for papers on [topic]"
- "what's new in research"
- "summarize this paper"
- "check research"
- "add research topic [topic]"

## Dependencies

- Research folder structure: `research/topics.md`, `research/digests/`, `research/[topic]/`
- Web search capability for paper queries
- PDF reading capability for summarization (optional)

## Configuration

Topics and keywords defined in `research/topics.md`.

## Modes

### Manual Search
**Trigger:** "search for papers on [topic]"

Search arXiv, Google Scholar, and web. Return top 5-10 results with title, one-line summary, link.

### Daily Digest
**Trigger:** Scheduled or part of /today

Read topics.md, search arXiv for recent papers, deduplicate against seen papers, write digest to `research/digests/[YYYY-MM-DD].md`.

### Paper Summarization
**Trigger:** "summarize this paper"

Read PDF from `research/[topic]/sources/`, generate summary covering: research question, methods, key findings, effect sizes, limitations, relevance. Save to `research/[topic]/notes/[paper-name].md`.

### Add Topic
**Trigger:** "add research topic [topic]"

Ask for topic name, keywords, arXiv categories, priority. Add to topics.md. Create folder structure.

## Folder Structure

```
research/
├── topics.md
├── digests/
│   └── [YYYY-MM-DD].md
└── [topic]/
    ├── sources/     # Downloaded PDFs
    └── notes/       # Generated summaries
```

## Error Handling

- If topics.md doesn't exist: Create it with template
- If search returns no results: Note in digest, suggest broadening keywords
- If PDF can't be read: Note limitation, offer to summarize from abstract
