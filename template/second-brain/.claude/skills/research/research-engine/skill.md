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

Topics and keywords defined in `research/topics.md`:

```markdown
# Research Topics

## Topic: [Topic Name 1]
Keywords: keyword1, keyword2, keyword3
Categories: cs.AI, cs.LG (for arXiv)
Priority: high

## Topic: [Topic Name 2]
Keywords: keyword1, keyword2
Categories: cs.HC
Priority: medium
```

## Workflow

### Manual Search Mode

**Trigger:** "search for papers on [topic]"

1. Parse topic from request
2. Construct search queries for:
   - arXiv (if academic/technical)
   - Google Scholar
   - General web (for recent developments)
3. Return top 5-10 relevant results
4. Format with title, one-line summary, link

**Output:**
```markdown
## Papers on [Topic]

### arXiv Results
1. **[Title]** (2024)
   [One-line summary]
   [Link]

2. **[Title]** (2024)
   [One-line summary]
   [Link]

### Scholar Results
1. **[Title]** — [Journal/Conference]
   [One-line summary]
   [Link]

---
*Want me to summarize any of these in detail?*
```

### Daily Digest Mode

**Trigger:** Scheduled or part of /today

1. Read `research/topics.md` for keywords
2. For each topic:
   - Search arXiv for papers from past 24-48 hours
   - Filter by relevance and category
3. Deduplicate against seen papers (check existing digests)
4. Generate digest file

**Output location:** `research/digests/[YYYY-MM-DD].md`

**Digest format:**
```markdown
# Research Digest: [YYYY-MM-DD]

## [Topic 1]
- **[Paper Title]** — [One-line summary]
  [arXiv/link]
  
- **[Paper Title]** — [One-line summary]
  [link]

## [Topic 2]
- **[Paper Title]** — [One-line summary]
  [link]

## No New Papers
- [Topic 3]: No new papers today

---
*Download interesting papers to `research/[topic]/sources/` for detailed summary tomorrow.*
```

### Paper Summarization Mode

**Trigger:** "summarize this paper" or "summarize [paper name]" or new PDF in sources folder

For papers user has downloaded:

1. Locate PDF in `research/[topic]/sources/`
2. Read and analyze the paper
3. Generate detailed summary focusing on:
   - Research question
   - Methods and rigor
   - Key findings
   - Effect sizes (critical for evaluating quality)
   - Limitations
   - Relevance to user's work
4. Save to `research/[topic]/notes/[paper-name].md`

**Summary format:**
```markdown
# [Paper Title]

## Citation
[Authors], [Year], [Source/Journal]
[DOI/Link]

## TL;DR
[2-3 sentence executive summary]

## Research Question
What problem does this paper address?
[Answer]

## Methods

### Study Design
[Type of study: RCT, observational, meta-analysis, etc.]

### Sample
- Size: [N]
- Population: [Who was studied]
- Selection: [How they were chosen]

### Measures
[Key variables and how they were measured]

### Analysis
[Statistical methods used]

## Key Findings

1. **[Finding 1]**
   - Effect size: [If reported]
   - Significance: [p-value or CI]

2. **[Finding 2]**
   - Effect size: [If reported]
   - Significance: [p-value or CI]

## Quality Assessment

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Sample size | Adequate/Small/Large | [Context] |
| Methods rigor | High/Medium/Low | [Why] |
| Pre-registration | Yes/No/Unclear | |
| Conflicts of interest | None/Some/Unclear | |

## Limitations
[Noted by authors]
- [Limitation 1]
- [Limitation 2]

[Observed/potential issues]
- [Issue 1]

## Relevance to My Work
[How this connects to user's interests/projects]

## Bottom Line
**Worth reading in full?** [Yes/No/Skim]
**Why:** [Brief reasoning]

---
*Summarized [date]*
```

### Add Topic Mode

**Trigger:** "add research topic [topic]"

1. Ask for:
   - Topic name
   - Keywords to search
   - arXiv categories (if applicable)
   - Priority level
2. Add to `research/topics.md`
3. Create folder `research/[topic]/` with `sources/` and `notes/` subfolders
4. Confirm setup

## Folder Structure

```
research/
├── topics.md                    # Topic configuration
├── digests/
│   ├── 2024-01-15.md
│   └── 2024-01-16.md
├── [topic-1]/
│   ├── sources/                 # Downloaded PDFs
│   │   └── paper-name.pdf
│   └── notes/                   # Generated summaries
│       └── paper-name.md
└── [topic-2]/
    ├── sources/
    └── notes/
```

## Error Handling

- If topics.md doesn't exist: Create it with template
- If search returns no results: Note in digest, suggest broadening keywords
- If PDF can't be read: Note limitation, offer to summarize from abstract
- If arXiv is down: Fall back to web search

## Notes

- The goal is to reduce friction in staying current, not automate everything
- User still downloads papers manually (acts as filter for quality)
- Summaries focus on methodology quality to help user evaluate papers
- This is augmentation, not replacement for reading important papers
