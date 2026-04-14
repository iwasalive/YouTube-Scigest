# Scigest Production Pipeline

## Overview

The Scigest Production Pipeline is an automated system that discovers, researches, and scripts YouTube video content. It runs daily via cron and delivers outputs to Discord with file attachments.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Daily Cron Job (9 AM PST)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Topic Discovery Phase                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Reddit  │  │ YouTube  │  │ News     │  │ Manual   │   │
│  │          │  │          │  │ Letters  │  │ Feed     │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│         │              │              │              │      │
│         └──────────────┴──────────────┴──────────────┘      │
│                              │                              │
│                      Deduplicate & Filter                   │
│                      (6-month cooldown)                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Deep Research Phase                            │
│  For each discovered topic:                                 │
│  - Multiple source analysis                                 │
│  - Perspective gathering                                    │
│  - Fact verification                                        │
│  - Trend assessment                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Script Writing Phase                           │
│  - Hook & introduction                                      │
│  - Main content sections                                    │
│  - Examples & case studies                                  │
│  - Conclusion & CTA                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Output & Delivery                              │
│  - Summary report (text)                                    │
│  - Full script (MEDIA: attachment)                          │
│  - Delivered to Discord channel                             │
└─────────────────────────────────────────────────────────────┘
```

## Job Configuration

**Job ID:** `85617a4f68f9`
**Schedule:** `0 9 * * *` (9:00 AM PST daily)
**Deliver:** `discord:1485454680896307401`
**Skills:** `research-skill`, `scigest-production`

## Skills Used

### 1. research-skill
Located: `skills/research-skill/SKILL.md`

Purpose: Topic discovery and initial research
- Scans Reddit, YouTube, newsletters, and manual feed
- Deduplicates and filters by cooldown period
- Performs initial topic assessment

### 2. scigest-production
Located: `skills/scigest-production/SKILL.md`

Purpose: Full video production
- Takes discovered topics
- Performs deep research
- Writes complete video scripts
- Formats for YouTube delivery

### 3. scigest-production-pipeline
Located: `skills/scigest-production-pipeline/SKILL.md`

Purpose: End-to-end automation
- Orchestrates discovery → research → production
- Handles error recovery
- Manages output formatting

## Output Format

### Daily Summary (Text Message)
```markdown
## Scigest Production Report

**Date:** 2026-04-14
**Topics Discovered:** X
**Scripts Generated:** Y

### Top Picks
1. Topic A - Brief description
2. Topic B - Brief description
3. Topic C - Brief description

**Full Scripts:** MEDIA:/path/to/scripts.md
```

### Full Scripts (Attached File)
- Complete video scripts for each topic
- Structured with timestamps
- Includes research citations
- Ready for voiceover/production

## Media Attachment Protocol

The pipeline uses the `MEDIA:` protocol for file attachments:

```markdown
**Full Report:** MEDIA:/home/mxyclaw/.hermes/cron/output/scigest-2026-04-14.md
```

This ensures:
1. File is extracted by the scheduler
2. Sent as native Discord attachment
3. Removed from message body (clean text)

## Cron Job Management

### View Status
```bash
hermes cron list
```

### View Recent Output
```bash
ls -la ~/.hermes/cron/output/85617a4f68f9/
```

### Check Last Run
```bash
cat ~/.hermes/cron/jobs.json | python3 -c "
import sys, json
jobs = json.load(sys.stdin).get('jobs', [])
for j in jobs:
    if j['id'] == '85617a4f68f9':
        print(f\"Last run: {j.get('last_run_at')}\")
        print(f\"Status: {j.get('last_status')}\")
        print(f\"Error: {j.get('last_delivery_error')}\")
"
```

### Modify Schedule
Edit `~/.hermes/cron/jobs.json` or use:
```bash
hermes cron update --job-id 85617a4f68f9 --schedule "0 10 * * *"
```

## Troubleshooting

### No Output Received
1. Check job status: `hermes cron list`
2. Verify Discord channel ID is correct
3. Check `~/.hermes/cron/output/85617a4f68f9/` for generated files
4. Review error logs in jobs.json

### Script Quality Issues
1. Check research sources are accessible
2. Verify API keys are configured
3. Review skill documentation for adjustments
4. Add topics to manual feed for testing

### Attachment Not Working
1. Verify file exists at MEDIA: path
2. Check file permissions
3. Test extraction:
   ```python
   from gateway.platforms.base import BasePlatformAdapter
   content = "**Report:** MEDIA:/path/to/file.md"
   media, _ = BasePlatformAdapter.extract_media(content)
   print(media)
   ```

## Performance Metrics

Track pipeline effectiveness:
- Topics discovered per day
- Scripts generated per day
- Topics in cooldown (indicates good discovery)
- Delivery success rate

See `skills/youtube-analytics-automation/` for channel performance tracking.

## Related Documentation

- [Research Methodology](docs/research-methodology.md)
- [YouTube Analytics](skills/youtube-analytics-automation/SKILL.md)
- [Hermes Agent Guide](../AGENTS.md)

---
*Last updated: April 14, 2026*
