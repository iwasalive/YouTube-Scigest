#!/usr/bin/env python3
"""
Research Scan Orchestrator
Integrates Reddit, YouTube, News, Humanizer, and Topic Scoring
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import yaml

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from reddit_scanner import scan_subreddit, SUBREDDITS
from youtube_analyzer import search_youtube_videos, analyze_video
from news_detector import fetch_rss_feed, analyze_article, DEFAULT_SOURCES
from humanizer import humanize_text, analyze_ai_score
from topic_scoring import calculate_topic_score, generate_score_report

# Configuration
RESEARCH_HOME = Path.home() / ".hermes" / "research"
CONFIG_PATH = RESEARCH_HOME / "config.yaml"
OUTPUT_DIR = RESEARCH_HOME / "output"


def load_config():
    """Load research configuration."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    return {}


def run_reddit_scan():
    """Run Reddit scanner and return results."""
    print("\n🔍 Scanning Reddit...")
    all_results = []
    
    config = load_config()
    subreddits = config.get("subreddits", SUBREDDITS)
    
    for subreddit in subreddits:
        results = scan_subreddit(subreddit)
        all_results.extend(results)
    
    print(f"  Found {len(all_results)} posts")
    return all_results


def run_youtube_scan():
    """Run YouTube comment analyzer and return results."""
    print("\n🔍 Scanning YouTube...")
    all_analyses = []
    
    search_terms = [
        "quantum computing explained",
        "AI breakthrough 2024",
        "new space discovery",
        "climate change explained",
        "biology explained",
        "physics explained",
    ]
    
    for term in search_terms:
        videos = search_youtube_videos(term, max_results=5)
        for video in videos[:3]:  # Limit per term
            analysis = analyze_video(video)
            all_analyses.append(analysis)
    
    print(f"  Analyzed {len(all_analyses)} videos")
    return all_analyses


def run_news_scan():
    """Run news detector and return results."""
    print("\n🔍 Scanning news feeds...")
    all_analyses = []
    
    config = load_config()
    sources = config.get("newsSources", DEFAULT_SOURCES)
    
    for source in sources:
        articles = fetch_rss_feed(source["url"], source["name"])
        for article in articles[:5]:  # Limit per source
            analysis = analyze_article(article)
            all_analyses.append(analysis)
    
    print(f"  Analyzed {len(all_analyses)} articles")
    return all_analyses


def extract_topics_from_results(reddit_results, youtube_results, news_results):
    """Extract topic ideas from all sources."""
    topics = []
    
    # From Reddit
    for result in reddit_results:
        if result.get("questions"):
            for question in result["questions"][:2]:
                topics.append({
                    "topic": question["text"][:100],
                    "source": "reddit",
                    "context": result["title"]
                })
    
    # From YouTube
    for analysis in youtube_results:
        if analysis.get("detail_requests"):
            for req in analysis["detail_requests"][:2]:
                topics.append({
                    "topic": req["text"][:100],
                    "source": "youtube",
                    "context": analysis["video"]["title"]
                })
    
    # From News
    for analysis in news_results:
        if analysis.get("counterintuitive_score", 0) >= 2:
            topics.append({
                "topic": analysis["article"]["title"],
                "source": "news",
                "context": analysis["article"]["source"]
            })
    
    return topics


def score_topics(topics):
    """Score all topics and return only those meeting threshold."""
    scored = []
    
    for topic_data in topics:
        score_data = calculate_topic_score(topic_data["topic"])
        score_data["source"] = topic_data["source"]
        score_data["context"] = topic_data["context"]
        scored.append(score_data)
    
    # Filter to 40+ threshold
    return [s for s in scored if s["meets_threshold"]]


def humanize_draft(draft_text):
    """Humanize a draft script."""
    humanized = humanize_text(draft_text)
    original_score = analyze_ai_score(draft_text)
    humanized_score = analyze_ai_score(humanized)
    
    return {
        "original": draft_text,
        "humanized": humanized,
        "original_ai_score": original_score,
        "humanized_ai_score": humanized_score,
        "improvement": original_score - humanized_score
    }


def generate_full_research_brief(reddit_results, youtube_results, news_results):
    """Generate comprehensive research brief."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Extract and score topics
    topics = extract_topics_from_results(reddit_results, youtube_results, news_results)
    scored_topics = score_topics(topics)
    
    # Generate brief
    brief = f"""# YouTube Research Brief
Generated: {datetime.now().isoformat()}

## Top Recommended Topics ({len(scored_topics)} topics scoring 40+)

"""
    
    for i, topic in enumerate(scored_topics[:10], 1):
        brief += f"""### {i}. {topic["topic"][:80]}
**Score**: {topic["total_score"]}/100
**Source**: {topic["source"].upper()}
**Breakdown**:
- Reddit Engagement: {topic["components"]["reddit_engagement"]}/10
- YouTube Search Volume: {topic["components"]["youtube_search_volume"]}/10
- News Freshness: {topic["components"]["news_freshness"]}/10
- Explainer Potential: {topic["components"]["explainer_potential"]}/10
- Visual Potential: {topic["components"]["visual_potential"]}/10

"""
    
    # Save to file
    output_file = OUTPUT_DIR / f"research-brief-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(output_file, "w") as f:
        f.write(brief)
    
    return brief, output_file


def main(command="full"):
    """
    Main research orchestrator.
    
    Commands:
    - full: Run all scans
    - reddit: Just Reddit
    - youtube: Just YouTube
    - news: Just news
    - score <topic>: Score a specific topic
    - humanize <text>: Humanize a draft
    """
    
    if command == "reddit":
        results = run_reddit_scan()
        brief, output_file = generate_research_brief_from_reddit(results)
    
    elif command == "youtube":
        results = run_youtube_scan()
        brief, output_file = generate_research_brief_from_youtube(results)
    
    elif command == "news":
        results = run_news_scan()
        brief, output_file = generate_research_brief_from_news(results)
    
    elif command == "score":
        if len(sys.argv) < 3:
            print("Usage: research_scan.py score <topic>")
            sys.exit(1)
        topic = " ".join(sys.argv[2:])
        score = calculate_topic_score(topic)
        print(f"\nTopic: {topic}")
        print(f"Total Score: {score['total_score']}/100")
        print("Breakdown:")
        for k, v in score["components"].items():
            print(f"  {k.replace('_', ' ').title()}: {v}/10")
        brief, output_file = None, None
    
    elif command == "humanize":
        if len(sys.argv) < 3:
            print("Usage: research_scan.py humanize <text>")
            sys.exit(1)
        text = " ".join(sys.argv[2:])
        result = humanize_draft(text)
        print("\nOriginal AI Score:", result["original_ai_score"])
        print("Humanized AI Score:", result["humanized_ai_score"])
        print("\nHumanized Text:")
        print(result["humanized"])
        brief, output_file = None, None
    
    else:
        # Full scan
        reddit_results = run_reddit_scan()
        youtube_results = run_youtube_scan()
        news_results = run_news_scan()
        
        brief, output_file = generate_full_research_brief(
            reddit_results, youtube_results, news_results
        )
    
    print(f"\n✅ Research brief saved to: {output_file}")
    if brief:
        print("\n" + brief[:800] + "..." if len(brief) > 800 else brief)
    
    return brief, output_file


def generate_research_brief_from_reddit(results):
    """Generate brief from Reddit results."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sort and filter
    results.sort(key=lambda x: x["score"], reverse=True)
    high_score = [r for r in results if r["score"] >= 8]
    
    brief = f"""# Reddit Research Brief
Generated: {datetime.now().isoformat()}

## Top Topics

"""
    
    for i, result in enumerate(high_score[:10], 1):
        brief += f"### {i}. {result['title']}\n"
        brief += f"**Score**: {result['score']:.1f} | **Upvotes**: {result['upvotes']} | **Comments**: {result['comments']}\n\n"
    
    output_file = OUTPUT_DIR / f"reddit-brief-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(output_file, "w") as f:
        f.write(brief)
    
    return brief, output_file


def generate_research_brief_from_youtube(results):
    """Generate brief from YouTube results."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sort by detail requests
    results.sort(key=lambda x: x["request_count"], reverse=True)
    
    brief = f"""# YouTube Research Brief
Generated: {datetime.now().isoformat()}

## Videos with "More Detail" Requests

"""
    
    for i, analysis in enumerate(results[:10], 1):
        if analysis["request_count"] == 0:
            continue
        brief += f"### {i}. {analysis['video']['title']}\n"
        brief += f"**Detail Requests**: {analysis['request_count']} | **Link**: {analysis['video']['url']}\n\n"
    
    output_file = OUTPUT_DIR / f"youtube-brief-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(output_file, "w") as f:
        f.write(brief)
    
    return brief, output_file


def generate_research_brief_from_news(results):
    """Generate brief from news results."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sort by score
    results.sort(key=lambda x: x["total_score"], reverse=True)
    
    brief = f"""# News Research Brief
Generated: {datetime.now().isoformat()}

## Hot Topics

"""
    
    for i, analysis in enumerate(results[:10], 1):
        if analysis["total_score"] < 10:
            continue
        article = analysis["article"]
        brief += f"### {i}. {article['title']}\n"
        brief += f"**Source**: {article['source']} | **Score**: {analysis['total_score']}\n"
        brief += f"**Link**: {article['link']}\n\n"
    
    output_file = OUTPUT_DIR / f"news-brief-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(output_file, "w") as f:
        f.write(brief)
    
    return brief, output_file


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "full"
    main(command)
