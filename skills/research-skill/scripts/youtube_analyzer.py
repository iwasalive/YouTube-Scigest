#!/usr/bin/env python3
"""
YouTube Comment Analyzer for YouTube Research
Extracts "more detail please" requests from trending videos
"""

import json
import urllib.request
import urllib.parse
import re
from datetime import datetime, timedelta
from pathlib import Path
import yaml

# Configuration
RESEARCH_HOME = Path.home() / ".hermes" / "research"
CONFIG_PATH = RESEARCH_HOME / "config.yaml"
OUTPUT_DIR = RESEARCH_HOME / "output" / "youtube"

# Keywords that indicate "more detail" requests
MORE_DETAIL_PATTERNS = [
    r"more detail",
    r"part 2",
    r"can you explain",
    r"how does.*work",
    r"why does.*happen",
    r"but what about",
    r"what about.*actually",
    r"i wish you covered",
    r"would love to see",
    r"deep dive",
    r"more on this",
    r"explain this better",
    r"can you do",
    r"make a video",
    r"please make",
]

# Science/tech categories for trending search
TRENDING_CATEGORIES = [
    "27",  # Science & Technology
    "28",  # Science & Tech (alternative)
]


def load_config():
    """Load research configuration."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    return {}


def search_youtube_videos(query, max_results=10):
    """Search YouTube for videos (uses public API)."""
    # Note: This is a simplified version using public endpoints
    # For production, you'd use the YouTube Data API with an API key
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}&sp=EgIQAQ%253D%253D"
    
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (YouTube Research Bot)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode()
            
            # Extract video IDs from HTML (simplified parsing)
            video_ids = re.findall(r'"videoId":"([^"]+)"', html)
            titles = re.findall(r'"title":"([^"]+)"', html)
            
            results = []
            for i, vid in enumerate(video_ids[:max_results]):
                if i < len(titles):
                    results.append({
                        "video_id": vid,
                        "title": titles[i].replace("\\", "").replace('"', ''),
                        "url": f"https://www.youtube.com/watch?v={vid}"
                    })
            return results
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return []


def extract_comments(video_id, max_comments=50):
    """Extract comments from a YouTube video."""
    # This is a simplified version - in production, use YouTube API
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (YouTube Research Bot)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode()
            
            # Extract comment text (simplified parsing)
            comments = re.findall(r'"commentText":"([^"]+)"', html)
            
            # Clean up the comments
            cleaned = []
            for c in comments[:max_comments]:
                c = c.replace("\\n", "\n").replace("\\", "")
                if len(c) > 20 and len(c) < 500:  # Reasonable comment length
                    cleaned.append(c)
            
            return cleaned
    except Exception as e:
        print(f"Error extracting comments: {e}")
        return []


def find_more_detail_requests(comments):
    """Find comments requesting more detail."""
    requests = []
    
    for comment in comments:
        comment_lower = comment.lower()
        
        for pattern in MORE_DETAIL_PATTERNS:
            if re.search(pattern, comment_lower):
                requests.append({
                    "text": comment,
                    "pattern": pattern
                })
                break  # Only match first pattern
    
    return requests


def analyze_video(video):
    """Analyze a single video for "more detail" requests."""
    print(f"  Analyzing: {video['title'][:50]}...")
    
    comments = extract_comments(video["video_id"])
    requests = find_more_detail_requests(comments)
    
    return {
        "video": video,
        "total_comments": len(comments),
        "detail_requests": requests,
        "request_count": len(requests)
    }


def generate_research_brief(analyses):
    """Generate a formatted research brief."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sort by detail request count
    analyses.sort(key=lambda x: x["request_count"], reverse=True)
    
    brief = f"""# YouTube Research Brief
Generated: {datetime.now().isoformat()}

## Videos with High "More Detail" Requests

"""
    
    for i, analysis in enumerate(analyses[:10], 1):
        if analysis["request_count"] == 0:
            continue
            
        brief += f"""### {i}. {analysis['video']['title']}
**Link**: {analysis['video']['url']}
**Detail Requests**: {analysis['request_count']} comments asking for more info
**Total Comments Analyzed**: {analysis['total_comments']}

**Sample Requests**:
"""
        for req in analysis["detail_requests"][:5]:
            brief += f"- {req['text'][:100]}...\n"
        
        brief += "\n"
    
    # Save to file
    output_file = OUTPUT_DIR / f"youtube-brief-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(output_file, "w") as f:
        f.write(brief)
    
    return brief, output_file


def main():
    """Main research scan function."""
    print("🔍 Analyzing YouTube for content ideas...")
    
    # Search for trending science/tech topics
    search_terms = [
        "quantum computing explained",
        "AI breakthrough 2024",
        "new space discovery",
        "climate change explained",
        "biology explained",
        "physics explained",
        "technology explained",
        "science explained",
    ]
    
    all_videos = []
    for term in search_terms:
        print(f"Searching: {term}")
        videos = search_youtube_videos(term)
        all_videos.extend(videos)
    
    # Remove duplicates by video_id
    seen = set()
    unique_videos = []
    for v in all_videos:
        if v["video_id"] not in seen:
            seen.add(v["video_id"])
            unique_videos.append(v)
    
    print(f"Found {len(unique_videos)} unique videos")
    
    # Analyze videos for detail requests
    analyses = []
    for video in unique_videos[:20]:  # Limit to first 20 for performance
        analysis = analyze_video(video)
        analyses.append(analysis)
    
    brief, output_file = generate_research_brief(analyses)
    
    print(f"\n✅ Research brief saved to: {output_file}")
    print("\n" + brief[:500] + "..." if len(brief) > 500 else brief)
    
    return brief


if __name__ == "__main__":
    main()
