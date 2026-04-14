#!/usr/bin/env python3
"""
YouTube Analytics Puller

Fetches channel statistics and video performance data from YouTube Data API v3.
Uses YOUTUBE_API_KEY environment variable.

Usage:
    python3 youtube_analytics.py [--channel-id CHANNEL_ID] [--video-id VIDEO_ID]
    
Output: JSON data with channel stats, recent videos, and performance metrics.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import urllib.parse

# Configuration
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")  # Optional - if not set, will prompt
OUTPUT_DIR = Path(__file__).parent.parent.parent / "cron" / "output"

# Performance targets (from your config)
TARGETS = {
    "ctr": 0.08,           # 8% CTR target
    "retention": 0.50,     # 50% average view duration
    "engagement": 0.03,    # 3% engagement rate
    "sub_conversion": 0.02 # 2% subscriber conversion
}


def log(message, level="INFO"):
    """Print timestamped log message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")


def make_api_request(endpoint, params=None):
    """Make a request to YouTube Data API v3"""
    if not API_KEY:
        raise ValueError("YOUTUBE_API_KEY environment variable not set")
    
    base_url = "https://www.googleapis.com/youtube/v3"
    url = f"{base_url}/{endpoint}"
    
    if params:
        params["key"] = API_KEY
        url += "?" + urllib.parse.urlencode(params)
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.URLError as e:
        log(f"API Error: {e}", "ERROR")
        return None
    except json.JSONDecodeError as e:
        log(f"JSON Parse Error: {e}", "ERROR")
        return None


def get_channel_stats(channel_id=None):
    """Get channel statistics"""
    if channel_id is None:
        channel_id = CHANNEL_ID
    
    if not channel_id:
        log("No channel ID provided. Please set YOUTUBE_CHANNEL_ID env var or pass --channel-id", "ERROR")
        return None
    
    params = {
        "part": "statistics,snippet,contentDetails",
        "id": channel_id
    }
    
    data = make_api_request("channels", params)
    if not data or "items" not in data or len(data["items"]) == 0:
        log("Failed to fetch channel data", "ERROR")
        return None
    
    channel = data["items"][0]
    stats = channel.get("statistics", {})
    snippet = channel.get("snippet", {})
    
    return {
        "channel_id": channel_id,
        "title": snippet.get("title", "Unknown"),
        "description": snippet.get("description", "")[:200],
        "custom_url": snippet.get("customUrl", ""),
        "published_at": snippet.get("publishedAt", ""),
        "thumbnails": snippet.get("thumbnails", {}),
        "statistics": {
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "view_count": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
        }
    }


def get_recent_videos(channel_id, max_results=10):
    """Get recent videos from channel"""
    if not CHANNEL_ID:
        log("No channel ID configured", "ERROR")
        return None
    
    # First get the channel's uploads playlist ID
    playlist_params = {
        "part": "contentDetails",
        "id": channel_id,
        "key": API_KEY
    }
    playlist_data = make_api_request("channels", playlist_params)
    
    if not playlist_data or "items" not in playlist_data:
        log("Failed to get uploads playlist", "ERROR")
        return None
    
    uploads_playlist_id = None
    for item in playlist_data["items"]:
        if "contentDetails" in item and "relatedPlaylists" in item["contentDetails"]:
            uploads_playlist_id = item["contentDetails"]["relatedPlaylists"]["uploads"]
            break
    
    if not uploads_playlist_id:
        log("Could not find uploads playlist ID", "ERROR")
        return None
    
    # Get videos from uploads playlist
    video_params = {
        "part": "snippet,statistics,contentDetails",
        "playlistId": uploads_playlist_id,
        "maxResults": str(max_results),
        "key": API_KEY
    }
    
    data = make_api_request("playlistItems", video_params)
    if not data or "items" not in data:
        log("Failed to fetch videos", "ERROR")
        return None
    
    videos = []
    for item in data["items"]:
        video_id = item["snippet"]["resourceId"]["videoId"]
        
        # Get detailed stats for each video
        video_params = {
            "part": "snippet,statistics,contentDetails",
            "id": video_id,
            "key": API_KEY
        }
        video_data = make_api_request("videos", video_params)
        
        if video_data and "items" in video_data and len(video_data["items"]) > 0:
            video = video_data["items"][0]
            snippet = video.get("snippet", {})
            stats = video.get("statistics", {})
            
            # Calculate derived metrics
            duration = snippet.get("duration", "PT0S")
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))
            
            engagement_rate = (likes + comments) / views if views > 0 else 0
            
            videos.append({
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", "")[:100],
                "published_at": snippet.get("publishedAt", ""),
                "duration": duration,
                "thumbnails": snippet.get("thumbnails", {}),
                "statistics": {
                    "view_count": views,
                    "like_count": likes,
                    "comment_count": comments,
                    "engagement_rate": round(engagement_rate, 4)
                },
                "metrics": {
                    "likes_per_view": round(likes / views, 4) if views > 0 else 0,
                    "comments_per_view": round(comments / views, 4) if views > 0 else 0
                }
            })
    
    return videos


def get_video_analytics(video_id):
    """Get detailed analytics for a specific video"""
    # Note: Detailed analytics (CTR, retention) require YouTube Analytics API
    # which has different permissions. This returns basic stats.
    params = {
        "part": "snippet,statistics,contentDetails",
        "id": video_id,
        "key": API_KEY
    }
    
    data = make_api_request("videos", params)
    if not data or "items" not in data:
        return None
    
    video = data["items"][0]
    snippet = video.get("snippet", {})
    stats = video.get("statistics", {})
    
    return {
        "video_id": video_id,
        "title": snippet.get("title", ""),
        "published_at": snippet.get("publishedAt", ""),
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0)),
        "comments": int(stats.get("commentCount", 0)),
        "duration": snippet.get("contentDetails", {}).get("duration", ""),
        "tags": snippet.get("tags", [])
    }


def generate_report():
    """Generate a comprehensive analytics report"""
    if not CHANNEL_ID:
        log("YOUTUBE_CHANNEL_ID not set. Please configure it first.", "ERROR")
        return None
    
    log(f"Fetching analytics for channel: {CHANNEL_ID}")
    
    # Get channel stats
    channel = get_channel_stats(CHANNEL_ID)
    if not channel:
        return None
    
    # Get recent videos
    videos = get_recent_videos(CHANNEL_ID, max_results=10)
    
    # Calculate averages
    if videos:
        avg_views = sum(v["statistics"]["view_count"] for v in videos) / len(videos)
        avg_engagement = sum(v["statistics"]["engagement_rate"] for v in videos) / len(videos)
        
        # Performance vs targets
        ctr_performance = "N/A (requires YouTube Analytics API)"
        retention_performance = "N/A (requires YouTube Analytics API)"
    else:
        avg_views = 0
        avg_engagement = 0
        ctr_performance = "No data"
        retention_performance = "No data"
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "channel": channel,
        "performance_targets": TARGETS,
        "recent_videos": videos,
        "summary": {
            "total_subscribers": channel["statistics"]["subscriber_count"],
            "total_views": channel["statistics"]["view_count"],
            "total_videos": channel["statistics"]["video_count"],
            "avg_recent_views": round(avg_views, 0),
            "avg_engagement_rate": round(avg_engagement, 4),
            "ctr_status": ctr_performance,
            "retention_status": retention_performance
        }
    }
    
    return report


def save_report(report, filename=None):
    """Save report to file"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"youtube_analytics_{timestamp}.json"
    
    filepath = OUTPUT_DIR / filename
    with open(filepath, "w") as f:
        json.dump(report, f, indent=2)
    
    log(f"Report saved to: {filepath}")
    return filepath


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube Analytics Puller")
    parser.add_argument("--channel-id", help="YouTube channel ID")
    parser.add_argument("--video-id", help="Specific video ID for detailed analytics")
    parser.add_argument("--json", action="store_true", help="Output as raw JSON")
    parser.add_argument("--report", action="store_true", help="Generate full report")
    
    args = parser.parse_args()
    
    if args.channel_id:
        os.environ["YOUTUBE_CHANNEL_ID"] = args.channel_id
    
    if args.video_id:
        # Get specific video analytics
        video = get_video_analytics(args.video_id)
        if video:
            if args.json:
                print(json.dumps(video, indent=2))
            else:
                print(json.dumps(video, indent=2))
        else:
            sys.exit(1)
    elif args.report:
        # Generate full report
        report = generate_report()
        if report:
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                save_report(report)
                print(f"Report generated successfully!")
                print(f"Channel: {report['channel']['title']}")
                print(f"Subscribers: {report['summary']['total_subscribers']:,}")
                print(f"Total Views: {report['summary']['total_views']:,}")
                print(f"Videos: {report['summary']['total_videos']}")
        else:
            sys.exit(1)
    else:
        # Default: generate report
        report = generate_report()
        if report:
            save_report(report)
            print(f"Report generated successfully!")
            print(f"Channel: {report['channel']['title']}")
            print(f"Subscribers: {report['summary']['total_subscribers']:,}")
            print(f"Total Views: {report['summary']['total_views']:,}")
            print(f"Videos: {report['summary']['total_videos']}")
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
