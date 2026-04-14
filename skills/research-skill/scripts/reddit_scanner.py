#!/usr/bin/env python3
"""
Reddit Scanner for YouTube Research
Finds high-engagement questions from science/tech subreddits
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
OUTPUT_DIR = RESEARCH_HOME / "output" / "reddit"

# Question signals in comments
QUESTION_PATTERNS = [
    r"how does.*work",
    r"why does.*happen",
    r"can you explain",
    r"what is.*actually",
    r"i don't get",
    r"but wait",
    r"so if that's true",
    r"what about",
    r"but how do we know",
]

# Subreddits to scan
SUBREDDITS = [
    {"name": "science", "weight": 1.0},
    {"name": "explainlikeimfive", "weight": 1.2},
    {"name": "askscience", "weight": 1.1},
    {"name": "technology", "weight": 0.8},
    {"name": "dataisbeautiful", "weight": 0.9},
]


def load_config():
    """Load research configuration."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    return {}


def fetch_reddit_posts(subreddit, limit=25):
    """Fetch recent posts from a subreddit using Reddit API."""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}&t=all"
    
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (YouTube Research Bot)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data.get("data", {}).get("children", [])
    except Exception as e:
        print(f"Error fetching {subreddit}: {e}")
        return []


def get_post_comments(post, max_comments=20):
    """Fetch top comments for a post."""
    post_id = post["data"]["id"]
    url = f"https://www.reddit.com/r/{post['data']['subreddit']}/comments/{post_id}.json?limit=100"
    
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (YouTube Research Bot)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            # Comments are in data[1].children
            if len(data.get("data", {}).get("children", [])) > 1:
                comments = data[1]["data"]["children"]
                return [c["data"] for c in comments if c["data"]["stickied"] == False][:max_comments]
    except Exception as e:
        pass
    return []


def is_question(text):
    """Check if text contains question signals."""
    text_lower = text.lower()
    for pattern in QUESTION_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    # Also check for actual question marks
    if "?" in text:
        return True
    return False


def extract_questions_from_comments(comments):
    """Extract questions from comments."""
    questions = []
    for comment in comments:
        if is_question(comment.get("body", "")):
            questions.append({
                "text": comment["body"],
                "author": comment["author"],
                "score": comment["score"],
                "created_utc": comment["created_utc"]
            })
    return questions


def score_post(post):
    """Score a post for YouTube explainer potential."""
    data = post["data"]
    
    score = 0
    
    # Engagement score (upvotes / 100)
    score += min(data.get("ups", 0) / 100, 10)
    
    # Comment ratio (comments / upvotes) - higher means more discussion
    if data.get("ups", 0) > 0:
        comment_ratio = data.get("num_comments", 0) / data["ups"]
        if comment_ratio > 0.1:  # More than 10% comment ratio
            score += 5
    
    # Title length (medium length = more detail)
    title_len = len(data.get("title", ""))
    if 50 < title_len < 150:
        score += 3
    
    # Self-post (usually more detailed than link posts)
    if data.get("is_self", False):
        score += 4
    
    # Flair presence (indicates categorization)
    if data.get("link_flair_text"):
        score += 2
    
    return min(score, 20)


def scan_subreddit(subreddit_config):
    """Scan a single subreddit for content."""
    subreddit = subreddit_config["name"]
    weight = subreddit_config.get("weight", 1.0)
    
    posts = fetch_reddit_posts(subreddit)
    results = []
    
    for post in posts:
        score = score_post(post) * weight
        data = post["data"]
        
        # Only process posts with decent engagement
        if score < 3:
            continue
        
        # Get comments and extract questions
        comments = get_post_comments(post)
        questions = extract_questions_from_comments(comments)
        
        results.append({
            "subreddit": subreddit,
            "title": data.get("title", ""),
            "url": f"https://reddit.com{data.get('permalink', '/')}",
            "upvotes": data.get("ups", 0),
            "comments": data.get("num_comments", 0),
            "self_text": data.get("selftext", "")[:200] if data.get("is_self") else None,
            "flair": data.get("link_flair_text"),
            "score": score,
            "questions": questions[:5],  # Top 5 questions
            "timestamp": datetime.fromtimestamp(data.get("created_utc", 0)).isoformat()
        })
    
    return results


def generate_research_brief(scan_results):
    """Generate a formatted research brief."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sort by score
    scan_results.sort(key=lambda x: x["score"], reverse=True)
    
    # Filter to high-scoring topics
    high_score = [r for r in scan_results if r["score"] >= 8]
    
    brief = f"""# Reddit Research Brief
Generated: {datetime.now().isoformat()}

## Top Topics

"""
    
    for i, result in enumerate(high_score[:10], 1):
        brief += f"""### {i}. {result['title']}
**Source**: {result['subreddit']} | **Score**: {result['score']:.1f} | **Engagement**: {result['upvotes']} upvotes, {result['comments']} comments
**Link**: {result['url']}
"""
        if result.get("flair"):
            brief += f"**Flair**: {result['flair']}\n"
        
        if result.get("questions"):
            brief += "**Audience Questions**:\n"
            for q in result["questions"][:3]:
                brief += f"- {q['text'][:100]}... (score: {q['score']})\n"
        
        brief += "\n"
    
    # Save to file
    output_file = OUTPUT_DIR / f"reddit-brief-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(output_file, "w") as f:
        f.write(brief)
    
    return brief, output_file


def main():
    """Main research scan function."""
    print("🔍 Scanning Reddit for YouTube research...")
    
    all_results = []
    for subreddit in SUBREDDITS:
        print(f"  Scanning {subreddit['name']}...")
        results = scan_subreddit(subreddit)
        all_results.extend(results)
    
    print(f"  Found {len(all_results)} posts with engagement")
    
    brief, output_file = generate_research_brief(all_results)
    
    print(f"\n✅ Research brief saved to: {output_file}")
    print("\n" + brief[:500] + "..." if len(brief) > 500 else brief)
    
    return brief


if __name__ == "__main__":
    main()
