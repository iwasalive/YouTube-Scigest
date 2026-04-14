---
name: research-skill
description: YouTube-friendly topic research system - Reddit, YouTube comments, news RSS, humanizer, and topic scoring
version: 1.0.0
author: MJ + Hermes Agent
tags: [research, youtube, reddit, news, humanizer, content-creation]
---

# YouTube Research System

Research topics that actually drive views for long-form explainer content. Focuses on **audience signals** (Reddit, YouTube comments) and **news angles** rather than academic sources.

## What This Does

- **Reddit Scanner**: Finds high-engagement questions from r/science, r/explainlikeimfive, r/askscience
- **YouTube Comment Analyzer**: Extracts "more detail please" requests from trending videos
- **News Angle Detector**: Monitors science/tech RSS feeds for counterintuitive stories
- **Humanizer**: Rewrites AI content with colloquial patterns and sentence variance
- **Topic Scorecard**: Validates topics before recommending them (40+ score threshold)

## When to Use

- Planning a new video topic
- Need fresh ideas for explainer/deep-dive content
- Want to know what audiences are actually asking about
- Need to check if a topic is "AI-sounding" before finalizing script

## Quick Commands

```bash
# Full research scan (all sources)
hermes research scan

# Just Reddit discovery
hermes research reddit

# Just YouTube comment analysis
hermes research youtube

# Just news angles
hermes research news

# Humanize a draft
hermes research humanize "your draft text here"

# Score a topic idea
hermes research score "quantum computing explained"
```

## Cron Job

Runs daily at 8:00 AM PST. Posts research brief to YouTube channel.

## Output Files

- `~/.hermes/research/output/research-brief-YYYY-MM-DD.md` - Daily comprehensive brief
- `~/.hermes/research/output/reddit-brief-YYYY-MM-DD.md` - Reddit findings
- `~/.hermes/research/output/youtube-brief-YYYY-MM-DD.md` - YouTube comments
- `~/.hermes/research/output/news-brief-YYYY-MM-DD.md` - News angles
- `~/.hermes/research/output/scoring/score-report-YYYY-MM-DD.md` - Topic validation scores

## Architecture

```
research-skill/
├── SKILL.md                    # This file
├── scripts/
│   ├── research_scan.py        # Main research orchestrator
│   ├── reddit_scanner.py       # Reddit API integration
│   ├── youtube_analyzer.py     # YouTube comment extraction
│   ├── news_detector.py        # RSS + headline analysis
│   ├── humanizer.py            # AI content humanizer
│   └── topic_scoring.py        # Topic validation system
├── config/
│   └── research.yaml           # Research configuration
└── output/
    └── templates/              # Output templates
```

## Configuration

Edit `~/.hermes/research/config.yaml`:

```yaml
subreddits:
  - name: r/science
    weight: 1.0
  - name: r/explainlikeimfive
    weight: 1.2
  - name: r/askscience
    weight: 1.1
  - name: r/technology
    weight: 0.8
  - name: r/dataisbeautiful
    weight: 0.9

youtubecommentKeywords:
  - "more detail"
  - "part 2"
  - "explain"
  - "how does"
  - "why does"
  - "can you"

newsSources:
  - name: Wired
    url: https://www.wired.com/feed/category/science/latest/rss
    weight: 1.0
  - name: Ars Technica
    url: https://arstechnica.com/feed/
    weight: 0.9
  - name: The Verge
    url: https://www.theverge.com/rss/index.xml
    weight: 0.8

minTopicScore: 40  # Only recommend topics scoring 40+
```

## Implementation Notes & Lessons Learned

### Reddit API Quirks
- **Strip "r/" prefix** - API expects "science" not "r/science"
- **Add `&t=all`** to fetch older posts (default is limited)
- **Rate limits**: ~5 requests then 429 - implement backoff
- **User-Agent required**: Must be Mozilla/5.0 or similar

### RSS Parsing Gotchas
- **Namespace handling is tricky** - XML namespace prefixes often missing
- **Use curly brace format**: `.{http://www.w3.org/2005/Atom}title` instead of `atom:title`
- **Fallback to root tag check**: Check if `root.tag == "feed"` before namespace lookup
- **Handle both Atom and RSS** - Same structure, different namespaces

### Humanizer Pattern
- **Use lambda for random numbers** - Don't evaluate `random.randint()` at import time
  ```python
  # WRONG: ("a lot of", "about {random.randint(60, 80)}% of")
  # RIGHT: ("a lot of", lambda: f"about {random.randint(60, 80)}% of")
  ```
- **Call lambda when replacing**: `replacement = fn() if callable(fn) else fn`
- **Test with AI detector**: Aim for 0-10 AI score after humanization

### Cron Job Setup
- **Job ID**: `244a99e700e0`
- **Schedule**: `0 8 * * *` (8:00 AM PST daily)
- **Output**: `~/.hermes/research/output/research-brief-YYYY-MM-DD.md`

### Real Test Results
```
Reddit scan: ~95 posts per run (with rate limiting)
YouTube analysis: ~17 videos per scan
News articles: ~25 articles per scan
Humanizer: 36/100 → 0/100 AI score improvement
```

## Pitfalls

- **Don't rely on Reddit alone** - Cross-reference with YouTube comments
- **Watch for AI-sounding patterns** - Run humanizer before finalizing scripts
- **Check recency** - News angles expire in 7 days
- **Avoid echo chambers** - If all sources say the same thing, find a counter-narrative
- **Reddit rate limits** - Don't run multiple scans in quick succession
