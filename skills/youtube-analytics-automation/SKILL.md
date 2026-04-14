---
name: youtube-analytics-automation
description: Automating YouTube channel analytics and reporting via the YouTube Data API v3.
category: content-creation
---

# YouTube Analytics Automation

This skill provides a workflow for automating YouTube channel analytics and reporting via the YouTube Data API v3.

## Trigger Conditions
- User wants to track channel performance (views, engagement, growth).
- Setting up daily automated reports for a YouTube channel.

## Implementation Steps

1. **API Setup**
   - Create a project in Google Cloud Console.
   - Enable "YouTube Data API v3".
   - Create an API Key and restrict it to the YouTube Data API.
   - Save the key in `~/.hermes/.env` as `YOUTUBE_API_KEY`.

2. **Analytics Script (`youtube_analytics.py`)**
   - Use `googleapiclient.discovery` to build the service.
   - Fetch channel statistics (`channels().list(part='statistics')`).
   - Fetch all video IDs from the channel.
   - Fetch statistics for each video (`videos().list(part='statistics')`).
   - Calculate engagement rate: `((likes + comments) / views) * 100`.
   - Generate a Markdown report with:
     - Channel Overview (Total views, avg views, overall engagement).
     - Performance vs Targets (e.g., 3% engagement).
     - Top 3 performing videos.
     - Full video list sorted by views.
     - Insights and Recommendations.

3. **Discord Attachment Protocol**
   - To ensure files are attached to Discord messages, wrap the file path in a specific block:
     ```
     === MEDIA ATTACHMENT ===
     MEDIA:/absolute/path/to/file.md
     === END MEDIA ATTACHMENT ===
     ```

4. **Cron Job Configuration**
   - Schedule the script to run daily (e.g., 10 AM PST).
   - Direct output to a timestamped file in `~/.hermes/cron/output/`.

## Pitfalls
- **API Quotas**: Be mindful of quota limits when fetching statistics for very large channels.
- **Attachment Formatting**: Simple `MEDIA:` paths may fail if not wrapped in the standard attachment markers used by the gateway.
- **Private Videos**: The API key method only works for public data. For private analytics (CTR, Retention), OAuth2 is required.

## Verification
- Run the script manually: `python3 ~/.hermes/scripts/youtube_analytics.py`.
- Verify that the `.md` file is created in the output directory.
- Check that the Discord message contains both the summary and the attached file.
