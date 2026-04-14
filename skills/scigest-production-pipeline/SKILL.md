---
name: scigest-production-pipeline
description: Autonomous discovery, research, and scripting for VidRush formatted video content.
category: content-creation
---

# Scigest Production Pipeline

System for autonomously discovering, researching, and scripting high-quality technical/educational video content in the VidRush format.

## Trigger
When a new video recommendation is needed or during the daily 9:00 AM PST cron job.

## Workflow Steps

1. **Topic Discovery**
   - Scan Reddit, YouTube, and News for trending technical topics.
   - Score topics based on viral potential and depth.
   - Select the top-scoring topic (Score 40+).

2. **Deep Research**
   - Generate a comprehensive research brief.
   - Focus on mechanisms, factual data, and source verification.
   - Save as `01_research_brief.md`.

3. **VidRush Script Generation**
   - **Length**: Strict target of 1,200 to 2,000 words.
   - **Formatting**: All numbers must be written as words (e.g., "twenty twenty-six" instead of "2026").
   - **Constraints**: No meta-language, no visual cues, no `[Pause]` or `(Visuals)`.
   - **Structure**: Cold Open -> Setup -> Background -> Core Narrative -> Implications -> Conclusion.
   - **Requirement**: The "Mechanism Explanation" section must be 200+ words.
   - Save as `02_raw_script.txt`.

4. **Humanization**
   - Process the raw script through `humanizer.py`.
   - **Implementation**: When using `execute_code`, add the script's directory to `sys.path`:
     ```python
     import sys
     from pathlib import Path
     sys.path.append(str(Path.home() / ".hermes" / "skills" / "research-skill" / "scripts"))
     from humanizer import humanize_text
     ```
   - Inject sentence variance, colloquial transitions, and first-person perspective.
   - Save as `03_humanized_script.txt`.

5. **Production Package Creation**
   - Create a ZIP archive containing all deliverables:
     - `01_research_brief.md` (or `.json`)
     - `03_humanized_script.txt`
     - `04_metadata.json` (or `04_script_package.json`)
   - **Naming format**: `Scigest - YYYYMMDD - <video_title_slug>.zip`
     - Example: `Scigest - 20260409 - Quantum-Internet-Entanglement-Swapping.zip`
     - Title slug: lowercase, spaces to hyphens, remove special chars
   - Save to `~/.hermes/scigest/temp/`
   - This ZIP is the primary attachment for Discord delivery

6. **Local Archiving**
   - Create project folder: `~/.hermes/scigest/projects/<YYYY-MM-DD>_<slug>/`.
   - Store all versions of the script, the research brief, and a `04_metadata.json` (titles, tags, thumbnail ideas).
   - Copy the production ZIP to this folder as well.

6. **GitHub Sync**
   - Sync all project artifacts to the private repository: `iwasalive/scigest-hermes`.

7. **Discord Delivery**
   - **Main Post**: Send a high-level summary to `<#1485454680896307401>` (Topic, Score, Viral Title, "Why it works").
   - **Thread**: Create a thread on the main post and attach:
     - The production ZIP file (`Scigest - YYYYMMDD - <title>.zip`) as the primary attachment
     - This single ZIP contains all deliverables (research brief, scripts, metadata)

## Pitfalls
- **Reddit/Google Blocks**: Headless servers often get 404s or blocks from Reddit/Google. If scanners fail, synthesize a topic based on current industry shifts rather than getting stuck in a loop.
- **Word Count**: LLMs often undershoot. Use iterative expansion to hit the 1,200+ word minimum.
- **Numbers**: Ensure dates and percentages are also converted to words for TTS compatibility.
- **Meta-language**: Strictly strip any bracketed text before final delivery.

## Verification
- [ ] Script is between 1,200 and 2,000 words.
- [ ] No digits (0-9) remain in the final script.
- [ ] Production ZIP created with correct naming format: `Scigest - YYYYMMDD - <title_slug>.zip`
- [ ] ZIP contains all deliverables (research brief, humanized script, metadata)
- [ ] Project folder created and synced to GitHub.
- [ ] Discord thread contains the production ZIP as attachment.
