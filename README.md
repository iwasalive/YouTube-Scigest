# YouTube Scigest

Content research, analysis, and production pipeline for YouTube Scigest videos.

## 📁 Folder Structure

```
YouTube-Scigest/
├── README.md                    # This file - navigation guide
├── docs/                        # Documentation
│   ├── pipeline.md             # Production pipeline overview
│   ├── research-methodology.md # How we research topics
│   └── output-examples/        # Sample outputs
├── skills/                      # Hermes Agent skills
│   ├── scigest-production/           # Core production skill
│   ├── scigest-production-pipeline/  # Full pipeline automation
│   ├── youtube-analytics-automation/ # YouTube analytics collection
│   ├── research-skill/               # Topic research system
│   └── youtube-content/              # YouTube content utilities
├── scripts/                     # Standalone Python scripts
│   └── youtube_analytics.py  # Analytics data collection
├── config/                      # Configuration files
│   └── config.yaml         # Hermes agent configuration
└── output/                      # Sample outputs and reports
    └── *.md              # Example analysis reports
```

## 🚀 Quick Start

### Run the Production Pipeline

The Scigest production pipeline is a fully automated system that:
1. **Discovers** high-potential video topics from Reddit, YouTube, and news sources
2. **Researches** topics deeply using multiple data sources
3. **Scripts** complete video scripts with proper structure
4. **Analyzes** YouTube performance metrics

```bash
# Daily automated discovery (runs via cron)
# Check the scigest-production-pipeline skill for details

# Manual run
hermes skill scigest-production-pipeline
```

### Key Skills

| Skill | Purpose | Location |
|-------|---------|----------|
| `scigest-production` | Core production workflow | `skills/scigest-production/` |
| `scigest-production-pipeline` | Full automation pipeline | `skills/scigest-production-pipeline/` |
| `research-skill` | Topic research system | `skills/research-skill/` |
| `youtube-analytics-automation` | Performance tracking | `skills/youtube-analytics-automation/` |

## 📊 Cron Jobs

### Scigest Production Pipeline
- **Schedule:** Daily at 9:00 AM PST
- **Job ID:** `85617a4f68f9`
- **Deliver:** Discord channel `1485454680896307401`
- **Output:** Topic discovery and script generation

Check status:
```bash
hermes cron list
```

## 🔧 Configuration

### Environment Variables

Required in `~/.hermes/.env`:
```bash
# YouTube API
YOUTUBE_API_KEY=your_key_here

# Discord
DISCORD_BOT_TOKEN=your_token_here
DISCORD_HOME_CHANNEL=channel_id

# GitHub (for this repo sync)
GITHUB_TOKEN=your_token_here
```

### Hermes Config

See `config/config.yaml` for:
- Model configuration
- Tool settings
- Display preferences
- Cron job settings

## 📈 Output Examples

Sample reports are in the `output/` directory:
- `youtube_analytics_*.md` - Daily analytics reports
- Show channel performance, video metrics, and insights

## 🔍 Research Methodology

The research system uses multiple sources:

1. **Reddit** - r/Scigest and related communities
2. **YouTube** - Competitor analysis, trending topics
3. **Newsletters** - Curated industry newsletters
4. **Social Media** - Twitter/X trending topics
5. **Manual Feed** - User-suggested topics

See `skills/research-skill/SKILL.md` for detailed methodology.

## 🤖 Automated Workflow

```
┌─────────────────┐
│  Daily Cron Job │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Topic Discovery│ - Scan 7 sources
│  (999 topics)   │ - Deduplicate
│                 │ - Filter cooldown
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Deep Research  │ - Each topic analyzed
│  per topic      │ - Multiple perspectives
│                 │ - Source verification
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Script Writing │ - Full video script
│                 │ - Proper structure
│                 │ - Engaging format
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Discord Output │ - Delivered to channel
│  + File Attach  │ - MEDIA: protocol
└─────────────────┘
```

## 📝 Files Reference

### Skills (Hermes Agent)

Each skill directory contains:
- `SKILL.md` - Main skill documentation and instructions
- `scripts/` - Supporting Python scripts (if any)
- `templates/` - Output templates (if any)
- `references/` - Reference materials (if any)

### Key Scripts

- `scripts/youtube_analytics.py` - Standalone analytics collection
  - Can be run independently of Hermes
  - Outputs JSON and Markdown reports

### Configuration

- `config/config.yaml` - Hermes agent configuration
  - Model settings
  - Tool enablement
  - Display preferences
  - Cron wrap settings

## 🔗 External Resources

- **Hermes Agent Docs:** See `AGENTS.md` in hermes-agent repo
- **Discord Channel:** #youtube-scigest (ID: 1485454680896307401)
- **GitHub Repo:** https://github.com/iwasalive/YouTube-Scigest

## 🛠 Maintenance

### Update This Repo

To sync changes from the live system:

```bash
cd ~/YouTube-Scigest
# Manually copy updated skills/scripts
# Commit and push
git add .
git commit -m "Update: description"
git push origin main
```

### Check Cron Job Status

```bash
# List all jobs
hermes cron list

# View specific job output
ls -la ~/.hermes/cron/output/85617a4f68f9/

# Check recent runs
tail -50 ~/.hermes/cron/jobs.json
```

## 📞 Support

For issues or questions:
1. Check the relevant skill's `SKILL.md` file
2. Review cron job outputs in `~/.hermes/cron/output/`
3. Check Discord #youtube-scigest channel

---

*Last updated: April 14, 2026*
*Synced from: ~/.hermes/*
