---
name: scigest-production
description: End-to-end production pipeline for Scigest technical explainer videos - from discovery to humanized script and archiving.
version: 1.1.0
author: Hermes Agent
tags: [scigest, youtube, scriptwriting, technical-research, humanization]
---

# Scigest Production Pipeline

This skill orchestrates the transformation of a technical discovery into a production-ready YouTube script package following the Scigest brand voice: Intelligent, fact-based, and cynical but fair.

## Workflow

### 1. Enhanced Discovery & Selection
The goal is to find high-impact, scientifically accurate breakthroughs through a multi-stage filter.

**Stage A: Broad Discovery**
- Scan a wide array of sources: arXiv (priority: cs.AI, cs.LG), Hacker News (for buzz detection), Nature, Science, Cell, NASA, ESA, SpaceX, and specialized subreddits (r/science, r/space, r/biology, r/physics).
- Gather a wide list of potential candidates.

**Stage B: Initial Filtering**
- Filter candidates based on:
    - **Popularity**: Is there existing buzz or a growing trend?
    - **Channel Alignment**: Does this fit the Scigest technical/cynical brand?
- Narrow the list down to a shortlist of high-potential topics.

**Stage C: Dual-Perspective Analysis & Validation**
For the shortlist, perform a high-level analysis from two angles:
- **Scientific Direction**: Is the methodology sound? Is the source reputable (peer-reviewed, established institution)?
- **Layman's Perspective**: Is the "hook" understandable? Why does the average person care?
- Verify scientific accuracy and source credibility before proceeding.

**Stage D: Deep Dive**
- Select the **top 3 ideas** from the validated shortlist.
- Perform exhaustive research on these three to determine the absolute strongest narrative.

**Stage E: Final Selection & Expansion**
- Choose the final topic. 
- **Expansion**: If multiple topics from the top 3 are exceptionally strong, proceed with creating scripts for all of them. Each topic must be handled as a separate, clean workstream.

### 2. Research Brief (`01_research_brief.json`)
Generate a structured JSON brief containing:
- `topic` and `angle` (the specific "hook").
- `confidence_score` (1-100).
- `core_mechanism`: Detailed explanation of the "How" and "Why".
- `technical_details`: Specs, versions, and hardware.
- `surprising_facts`: Counter-intuitive findings or community myths.
- `sources`: List of URLs.

### 3. Scripting (`03_raw_script.txt`)
Generate a 1200-2000 word script following the VidRush format:
- **STRICT TTS Rules**: 
    - Every single number must be written as a word (e.g., "2026" $\rightarrow$ "twenty twenty-six").
    - Absolutely no meta-language: No `[Visuals]`, `(Pause)`, or `[Audio]`. Pure spoken text only.
- **Structure**:
    - Cold Open $\rightarrow$ Setup $\rightarrow$ Background $\rightarrow$ Core Narrative $\rightarrow$ Implications $\rightarrow$ Conclusion.
- **Mechanism Depth**: The technical "How it works" section must be 200+ words.

### 4. Humanization (`03_humanized_script.txt`)
Process the raw script to strip AI patterns:
- Replace "Additionally", "Furthermore", "In conclusion" with colloquial transitions.
- Vary sentence length and structure.
- Inject a "cynical but fair" tone.
- If `humanizer.py` is unavailable or unreliable, perform a manual LLM pass focusing on "digital archaeology" and "subversion of intent" themes.

### 5. Production ZIP Package
Create a ZIP archive as the primary deliverable:
- **Contents**:
    - `01_research_brief.json`
    - `03_humanized_script.txt`
    - `04_script_package.json`
- **Naming format**: `Scigest - YYYYMMDD - <video_title_slug>.zip`
    - Example: `Scigest - 20260409 - Quantum-Internet-Entanglement-Swapping.zip`
    - Title slug: lowercase, spaces to hyphens, remove special characters
- **Location**: Save to `~/.hermes/scigest/temp/`
- This ZIP is the attachment sent to Discord

### 6. Archiving & Sync
- **Folder Structure**: `~/.hermes/scigest/projects/YYYYMMDD - <title>/`
- **Files**:
    - `01_research_brief.json`
    - `03_humanized_script.txt`
    - `04_script_package.json`
    - Copy the production ZIP file
- **Sync**: Push the project folder to the `iwasalive/scigest-hermes` GitHub repo using `gh repo`.

## Pitfalls
- **Reddit 404s**: The `research_scan.py` may fail due to Reddit API changes. Always be ready to pivot to `browser` tools.
- **Number Formatting**: LLMs often forget to write numbers as words in long scripts. Always run a final regex check for digits.
- **Meta-Language Leakage**: Ensure no bracketed instructions remain in the final humanized script.
- **Content Access Fallbacks**: Many technical sites (CACM, academic journals) block automated access with Cloudflare or cookie walls. Use `https://r.jina.ai/http://<URL>` to fetch article content as markdown. This works for most paywalled or bot-blocked pages.
- **Browser Bot Detection**: Direct browser automation may fail on sites with aggressive bot detection. Prefer terminal-based research (curl + jina.ai reader) over browser tools for article extraction.
