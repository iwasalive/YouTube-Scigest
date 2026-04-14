#!/usr/bin/env python3
"""
Topic Scorecard System for YouTube Research
Validates topics before recommending them (40+ score threshold)
"""

import urllib.request
import json
import re
from pathlib import Path
from datetime import datetime
import yaml

# Configuration
RESEARCH_HOME = Path.home() / ".hermes" / "research"
CONFIG_PATH = RESEARCH_HOME / "config.yaml"
OUTPUT_DIR = RESEARCH_HOME / "output" / "scoring"


def load_config():
    """Load research configuration."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    return {}


def score_reddit_engagement(topic):
    """
    Score Reddit engagement for a topic.
    Returns 0-10 based on comment/upvote ratios.
    """
    try:
        encoded_topic = topic.replace(" ", "+")
        url = f"https://www.reddit.com/search.json?q={encoded_topic}&sort=hot&limit=10"
        
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Research Bot)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            
            posts = data.get("data", {}).get("children", [])
            if not posts:
                return 0
            
            # Calculate average engagement
            scores = []
            for post in posts[:10]:
                data = post.get("data", {})
                upvotes = data.get("ups", 0)
                comments = data.get("num_comments", 0)
                
                if upvotes > 100:  # Only count meaningful posts
                    # Higher comment/upvote ratio = more discussion
                    ratio = comments / max(upvotes, 1)
                    score = min(ratio * 100, 10)  # Scale to 0-10
                    scores.append(score)
            
            if scores:
                return sum(scores) / len(scores)
            return 0
            
    except Exception as e:
        return 0


def score_youtube_search_volume(topic):
    """
    Score YouTube search volume for a topic.
    Returns 0-10 based on related video view counts.
    """
    try:
        encoded_topic = topic.replace(" ", "+")
        url = f"https://www.youtube.com/results?search_query={encoded_topic}"
        
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Research Bot)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode()
            
            # Extract view counts from HTML (simplified)
            views = re.findall(r'"viewCountText":"([^"]+)"', html)
            
            if not views:
                return 5  # Default score if we can't parse
            
            # Parse view counts (e.g., "1.2M views" -> 1200000)
            total_views = 0
            count = 0
            
            for v in views[:10]:
                v = v.lower().replace(" views", "").replace("view", "")
                if "k" in v:
                    total_views += float(v.replace("k", "")) * 1000
                elif "m" in v:
                    total_views += float(v.replace("m", "")) * 1000000
                elif v.isdigit():
                    total_views += int(v)
                count += 1
            
            if count > 0:
                avg_views = total_views / count
                
                # Scale: 100K+ avg views = 10, 10K+ = 7, 1K+ = 4
                if avg_views >= 100000:
                    return 10
                elif avg_views >= 10000:
                    return 7
                elif avg_views >= 1000:
                    return 4
                else:
                    return 2
            
            return 5
            
    except Exception as e:
        return 5  # Default on error


def score_news_freshness(topic):
    """
    Score if topic is in current news cycle.
    Returns 0-10 based on recency.
    """
    try:
        encoded_topic = topic.replace(" ", "+")
        url = f"https://news.google.com/search?q={encoded_topic}&hl=en-US&gl=US&ceid=US:en"
        
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Research Bot)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode()
            
            # Check for recent articles (within 7 days)
            recent_count = 0
            total_count = 0
            
            # Look for time indicators in HTML
            time_patterns = [
                r'<time[^>]*datetime="(\d{4}-\d{2}-\d{2})"',
                r"(\d+)\s+(hours?|days?|weeks?)\s+ago",
            ]
            
            for pattern in time_patterns:
                matches = re.findall(pattern, html)
                total_count += len(matches)
                
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    
                    if isinstance(match, str):
                        # Check if within 7 days
                        try:
                            from datetime import datetime as dt
                            article_date = dt.strptime(match, "%Y-%m-%d")
                            if (dt.now() - article_date).days <= 7:
                                recent_count += 1
                        except:
                            pass
            
            if total_count > 0:
                return min((recent_count / total_count) * 10, 10)
            
            return 5  # Default if we can't determine
            
    except Exception as e:
        return 5  # Default on error


def score_explainer_potential(topic):
    """
    Score if topic is good for explainer video.
    Returns 0-10 based on "what" and "how" question potential.
    """
    score = 0
    
    # Does the topic naturally lead to questions?
    if any(word in topic.lower() for word in ["how", "what", "why", "explain", "mechanism"]):
        score += 3
    
    # Is it complex enough for a deep dive?
    if len(topic.split()) > 2:  # Multi-word topics
        score += 2
    
    # Does it have visual potential?
    visual_words = ["machine", "system", "process", "technology", "science", "physics", "biology"]
    if any(word in topic.lower() for word in visual_words):
        score += 2
    
    # Is it current/relevant?
    current_words = ["2024", "2025", "new", "latest", "breakthrough", "discovery"]
    if any(word in topic.lower() for word in current_words):
        score += 2
    
    return min(score, 10)


def score_visual_potential(topic):
    """
    Score if topic has visual potential for video.
    Returns 0-10.
    """
    score = 0
    
    visual_indicators = [
        "machine", "detector", "telescope", "satellite", "experiment",
        "lab", "facility", "particle", "accelerator", "array",
        "network", "map", "data", "graph", "chart", "diagram",
        "structure", "process", "flow", "system"
    ]
    
    for indicator in visual_indicators:
        if indicator in topic.lower():
            score += 1
    
    return min(score, 10)


def calculate_topic_score(topic):
    """
    Calculate comprehensive topic score.
    
    Components:
    - Reddit engagement: 0-10 (weight: 20%)
    - YouTube search volume: 0-10 (weight: 25%)
    - News freshness: 0-10 (weight: 15%)
    - Explainer potential: 0-10 (weight: 20%)
    - Visual potential: 0-10 (weight: 20%)
    
    Returns:
    - Total score (0-100)
    - Component breakdown
    """
    scores = {
        "reddit_engagement": score_reddit_engagement(topic),
        "youtube_search_volume": score_youtube_search_volume(topic),
        "news_freshness": score_news_freshness(topic),
        "explainer_potential": score_explainer_potential(topic),
        "visual_potential": score_visual_potential(topic),
    }
    
    # Weighted average
    weights = {
        "reddit_engagement": 0.20,
        "youtube_search_volume": 0.25,
        "news_freshness": 0.15,
        "explainer_potential": 0.20,
        "visual_potential": 0.20,
    }
    
    total = sum(scores[k] * weights[k] for k in scores)
    
    return {
        "topic": topic,
        "total_score": round(total, 1),
        "components": {k: round(v, 1) for k, v in scores.items()},
        "meets_threshold": total >= 40,
        "timestamp": datetime.now().isoformat()
    }


def generate_score_report(topics):
    """Generate a formatted score report."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sort by total score
    topics.sort(key=lambda x: x["total_score"], reverse=True)
    
    report = f"""# Topic Scorecard Report
Generated: {datetime.now().isoformat()}

## Recommended Topics (40+ Score)

"""
    
    for topic in topics:
        if not topic["meets_threshold"]:
            continue
        
        report += f"""### {topic["topic"]}
**Total Score**: {topic["total_score"]}/100
**Breakdown**:
- Reddit Engagement: {topic["components"]["reddit_engagement"]}/10
- YouTube Search Volume: {topic["components"]["youtube_search_volume"]}/10
- News Freshness: {topic["components"]["news_freshness"]}/10
- Explainer Potential: {topic["components"]["explainer_potential"]}/10
- Visual Potential: {topic["components"]["visual_potential"]}/10

"""
    
    # Save to file
    output_file = OUTPUT_DIR / f"score-report-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(output_file, "w") as f:
        f.write(report)
    
    return report, output_file


def main():
    """Test topic scoring with sample topics."""
    sample_topics = [
        "quantum computing explained",
        "how AI actually works",
        "why climate models are wrong",
        "the science behind black holes",
        "new particle discovery 2024",
    ]
    
    print("Scoring topics...")
    
    scores = []
    for topic in sample_topics:
        print(f"  Scoring: {topic}")
        score = calculate_topic_score(topic)
        scores.append(score)
    
    report, output_file = generate_score_report(scores)
    
    print(f"\n✅ Report saved to: {output_file}")
    print("\n" + report[:500] + "..." if len(report) > 500 else report)


if __name__ == "__main__":
    main()
