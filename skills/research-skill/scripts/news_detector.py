#!/usr/bin/env python3
"""
News Angle Detector for YouTube Research
Monitors RSS feeds and identifies counterintuitive stories with explainer potential
"""

import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import re

# Configuration
RESEARCH_HOME = Path.home() / ".hermes" / "research"
CONFIG_PATH = RESEARCH_HOME / "config.yaml"
OUTPUT_DIR = RESEARCH_HOME / "output" / "news"

# Counterintuitive patterns in headlines
COUNTERINTUITIVE_PATTERNS = [
    r"scientists thought.*now",
    r"wrong about",
    r"myth",
    r"debunked",
    r"actually",
    r"secret",
    r"hidden",
    r"surprising",
    r"shocking",
    r"never again",
    r"is dead",
    r"is back",
    r"finally",
    r"changes everything",
    r"breakthrough",
    r"game changer",
    r"revolutionary",
]

# Visual potential indicators
VISUAL_PATTERNS = [
    r"machine",
    r"detector",
    r"telescope",
    r"satellite",
    r"experiment",
    r"lab",
    r"facility",
    r"particle",
    r"accelerator",
    r"array",
    r"network",
    r"map",
    r"data",
    r"graph",
    r"chart",
]


def load_config():
    """Load research configuration."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    return {}


# Default news sources (can be overridden in config)
DEFAULT_SOURCES = [
    {"name": "Wired", "url": "https://www.wired.com/feed/category/science/latest/rss"},
    {"name": "Ars Technica", "url": "https://arstechnica.com/feed/"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
    {"name": "Science Daily", "url": "https://www.sciencedaily.com/rss/all.xml"},
    {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
]


def fetch_rss_feed(source_url, source_name):
    """Fetch RSS feed from a URL."""
    try:
        req = urllib.request.Request(
            source_url,
            headers={"User-Agent": "Mozilla/5.0 (RSS Research Bot)"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read().decode()
            return parse_rss(xml_data, source_name)
    except Exception as e:
        print(f"Error fetching {source_name}: {e}")
        return []


def parse_rss(xml_data, source_name):
    """Parse RSS XML data."""
    try:
        root = ET.fromstring(xml_data)
        
        items = []
        
        # Try Atom format first (check for atom:feed or just <feed>)
        if root.tag == "feed" or root.find(".//{http://www.w3.org/2005/Atom}entry") is not None:
            for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
                title = entry.find("{http://www.w3.org/2005/Atom}title")
                link = entry.find("{http://www.w3.org/2005/Atom}link")
                published = entry.find("{http://www.w3.org/2005/Atom}published")
                summary = entry.find("{http://www.w3.org/2005/Atom}summary")
                
                if title is not None:
                    items.append({
                        "title": title.text or "",
                        "link": link.get("href") if link is not None else "",
                        "published": published.text if published is not None else "",
                        "description": summary.text if summary is not None else "",
                        "source": source_name
                    })
            return items
        
        # Try RSS format (check for rss:channel or just <rss>/<channel>)
        channel = root.find("channel")
        if channel is None:
            channel = root.find("{http://www.rssboard.org/rss-specification}channel")
        
        if channel is not None:
            for item in channel.findall("item"):
                title = item.find("title")
                link = item.find("link")
                published = item.find("pubDate")
                description = item.find("description")
                
                if title is not None:
                    items.append({
                        "title": title.text or "",
                        "link": link.text if link is not None else "",
                        "published": published.text if published is not None else "",
                        "description": description.text if description is not None else "",
                        "source": source_name
                    })
            return items
        
        return items
        
    except Exception as e:
        print(f"Error parsing RSS: {e}")
        return []


def score_counterintuitive(headline):
    """Score how counterintuitive a headline is."""
    headline_lower = headline.lower()
    score = 0
    
    for pattern in COUNTERINTUITIVE_PATTERNS:
        if re.search(pattern, headline_lower):
            score += 1
    
    return score


def score_visual_potential(headline, description=""):
    """Score visual potential for video content."""
    text = (headline + " " + description).lower()
    score = 0
    
    for pattern in VISUAL_PATTERNS:
        if re.search(pattern, text):
            score += 1
    
    # Also check for numbers (data visualizations)
    if re.search(r"\d+", text):
        score += 1
    
    return score


def score_explainer_potential(headline, description=""):
    """Score if a story is good for explainer video."""
    score = 0
    
    # Length matters (too short = no depth)
    if 50 < len(headline) < 120:
        score += 2
    
    # Has a "what" or "how" question potential
    if re.search(r"what|how|why", headline.lower()):
        score += 3
    
    # Has complexity indicators
    if re.search(r"complex|mechanism|process|system", headline.lower()):
        score += 2
    
    # Recent (within 7 days)
    return score


def analyze_article(article):
    """Analyze a single article for YouTube potential."""
    headline = article.get("title", "")
    description = article.get("description", "")
    
    counter_score = score_counterintuitive(headline)
    visual_score = score_visual_potential(headline, description)
    explainer_score = score_explainer_potential(headline, description)
    
    total_score = counter_score * 2 + visual_score + explainer_score
    
    return {
        "article": article,
        "counterintuitive_score": counter_score,
        "visual_score": visual_score,
        "explainer_score": explainer_score,
        "total_score": total_score,
        "is_hot": counter_score >= 2 or visual_score >= 3
    }


def generate_research_brief(analyses):
    """Generate a formatted research brief."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Sort by total score
    analyses.sort(key=lambda x: x["total_score"], reverse=True)
    
    brief = f"""# News Angle Research Brief
Generated: {datetime.now().isoformat()}

## Hot Topics (High Explainer Potential)

"""
    
    for i, analysis in enumerate(analyses[:10], 1):
        if analysis["total_score"] < 10:
            continue
        
        article = analysis["article"]
        
        brief += f"""### {i}. {article['title']}
**Source**: {article['source']} | **Score**: {analysis['total_score']}
**Link**: {article['link']}

**Analysis**:
- Counterintuitive: {analysis['counterintuitive_score']}/5
- Visual Potential: {analysis['visual_score']}/5
- Explainer Potential: {analysis['explainer_score']}/5

"""
    
    # Save to file
    output_file = OUTPUT_DIR / f"news-brief-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(output_file, "w") as f:
        f.write(brief)
    
    return brief, output_file


def main():
    """Main research scan function."""
    print("🔍 Scanning news feeds for YouTube angles...")
    
    config = load_config()
    sources = config.get("newsSources", DEFAULT_SOURCES)
    
    all_articles = []
    for source in sources:
        print(f"  Fetching {source['name']}...")
        articles = fetch_rss_feed(source["url"], source["name"])
        all_articles.extend(articles)
    
    print(f"  Found {len(all_articles)} articles")
    
    # Analyze articles
    analyses = []
    for article in all_articles[:50]:  # Limit for performance
        analysis = analyze_article(article)
        analyses.append(analysis)
    
    brief, output_file = generate_research_brief(analyses)
    
    print(f"\n✅ Research brief saved to: {output_file}")
    print("\n" + brief[:500] + "..." if len(brief) > 500 else brief)
    
    return brief


if __name__ == "__main__":
    main()
