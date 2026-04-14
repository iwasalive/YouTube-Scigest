#!/usr/bin/env python3
"""
Humanizer Module for YouTube Scripts
Rewrites AI content with human patterns: sentence variance, colloquialisms, first-person
"""

import re
import random
from pathlib import Path
from datetime import datetime

# Configuration
RESEARCH_HOME = Path.home() / ".hermes" / "research"
OUTPUT_DIR = RESEARCH_HOME / "output" / "humanizer"

# Colloquial transitions and fillers
TRANSITIONS = [
    "Look,",
    "Here's the thing,",
    "So,",
    "Now,",
    "Okay,",
    "Here's where it gets weird,",
    "And this is wild,",
    "But here's the kicker,",
    "So what do you do with that?",
    "Now you might be thinking,",
    "Let me break this down,",
    "Here's the deal,",
]

# Parenthetical asides
ASIDES = [
    "(and this is wild)",
    "(get this)",
    "(spoiler: it's not what you think)",
    "(long story short)",
    "(and don't get me started)",
    "(this is important)",
    "(trust me on this)",
    "(and I'm not even joking)",
    "(yes, really)",
    "(no, I'm serious)",
]

# First-person phrases
FIRST_PERSON = [
    "I found",
    "I discovered",
    "I was looking into this",
    "I came across",
    "What I found was",
    "Here's what I learned",
    "I had to dig into",
    "I spent some time on",
]

# Concrete quantifiers (AI loves "a lot" - humans use numbers)
# Format: (vague_pattern, concrete_template) - template is evaluated with random
CONCRETE_QUANTIFIERS = [
    ("a lot of", lambda: f"about {random.randint(60, 80)}% of"),
    ("many", lambda: f"{random.randint(3, 7)} out of 10"),
    ("several", lambda: str(random.randint(3, 9))),
    ("most", lambda: f"{random.randint(70, 90)}%"),
    ("some", lambda: f"{random.randint(20, 40)}%"),
    ("few", lambda: f"{random.randint(5, 15)}%"),
    ("a bunch", lambda: str(random.randint(10, 30))),
    ("tons of", lambda: f"{random.randint(50, 100)}+"),
]

# AI patterns to detect and avoid
AI_PATTERNS = [
    r"additionally",
    r"moreover",
    r"furthermore",
    r"it's important to note",
    r"it's worth mentioning",
    r"in conclusion",
    r"in summary",
    r"this demonstrates",
    r"this highlights",
    r"this underscores",
    r"it is worth noting",
    r"nevertheless",
    r"nonetheless",
    r"hence",
    r"thus",
    r"therefore",
]


def split_into_sentences(text):
    """Split text into sentences."""
    # Simple sentence splitter (not perfect but works for most cases)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def calculate_sentence_std_dev(sentences):
    """Calculate standard deviation of sentence lengths."""
    if not sentences:
        return 0
    
    lengths = [len(s.split()) for s in sentences]
    mean = sum(lengths) / len(lengths)
    variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
    return variance ** 0.5


def inject_colloquialisms(text):
    """Add colloquialisms and transitions."""
    sentences = split_into_sentences(text)
    result = []
    
    for i, sentence in enumerate(sentences):
        # Add transition to some sentences
        if random.random() < 0.3 and i > 0:  # 30% chance
            transition = random.choice(TRANSITIONS)
            sentence = f"{transition} {sentence[0].lower()}{sentence[1:]}"
        
        # Add parenthetical asides occasionally
        if random.random() < 0.15 and len(sentence) > 30:  # 15% chance
            aside = random.choice(ASIDES)
            sentence = f"{sentence} {aside}"
        
        result.append(sentence)
    
    return " ".join(result)


def add_first_person(text):
    """Convert passive/impersonal to first-person."""
    result = text
    
    # Replace some passive constructions
    replacements = [
        (r"it was found", random.choice(FIRST_PERSON) + " that"),
        (r"research shows", random.choice(FIRST_PERSON) + " that"),
        (r"studies indicate", random.choice(FIRST_PERSON) + " that"),
        (r"scientists discovered", random.choice(FIRST_PERSON) + " that"),
    ]
    
    for pattern, replacement in replacements:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result


def make_quantifiers_concrete(text):
    """Replace vague quantifiers with specific numbers."""
    result = text
    
    for vague, concrete_fn in CONCRETE_QUANTIFIERS:
        pattern = rf"\b{vague}\b"
        # Call the lambda to get the concrete value
        replacement = concrete_fn() if callable(concrete_fn) else concrete_fn
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    return result


def vary_sentence_lengths(text):
    """Ensure sentence length variance (AI writes uniform sentences)."""
    sentences = split_into_sentences(text)
    
    if len(sentences) < 3:
        return text
    
    lengths = [len(s.split()) for s in sentences]
    std_dev = calculate_sentence_std_dev(sentences)
    
    # Target: std dev > 5 for human-like variance
    if std_dev < 4:
        # Inject some short and long sentences
        for i in range(min(3, len(sentences) // 3)):
            if random.random() < 0.5:
                # Make this sentence shorter
                sentences[i] = sentences[i].split(".")[0] + "."
            else:
                # Make this sentence longer
                sentences[i] = sentences[i] + " (and this is the part that matters)"
    
    return " ".join(sentences)


def remove_ai_patterns(text):
    """Remove or replace AI-sounding patterns."""
    result = text.lower()
    
    for pattern in AI_PATTERNS:
        result = re.sub(pattern, "", result, flags=re.IGNORECASE)
    
    # Clean up double spaces
    result = re.sub(r'\s+', ' ', result)
    
    return result.strip()


def humanize_text(text, iterations=2):
    """
    Apply multiple rounds of humanization.
    
    Args:
        text: The AI-generated text to humanize
        iterations: How many passes to make (more = more human but slower)
    
    Returns:
        Humanized text
    """
    result = text
    
    for i in range(iterations):
        # 1. Remove AI patterns
        result = remove_ai_patterns(result)
        
        # 2. Make quantifiers concrete
        result = make_quantifiers_concrete(result)
        
        # 3. Add first-person
        result = add_first_person(result)
        
        # 4. Inject colloquialisms
        result = inject_colloquialisms(result)
        
        # 5. Vary sentence lengths
        result = vary_sentence_lengths(result)
    
    # Final cleanup
    result = re.sub(r'\s+', ' ', result)  # Remove extra spaces
    result = re.sub(r'\s*\.\s*\.', '.', result)  # Fix double periods
    result = re.sub(r'\s*\(\s*\)', '', result)  # Remove empty parentheses
    
    return result.strip()


def analyze_ai_score(text):
    """
    Analyze how "AI-sounding" text is.
    
    Returns a score (0-100, higher = more AI-like).
    """
    score = 0
    
    # Check for AI patterns
    for pattern in AI_PATTERNS:
        if re.search(pattern, text.lower()):
            score += 5
    
    # Check sentence length variance
    sentences = split_into_sentences(text)
    if len(sentences) > 2:
        std_dev = calculate_sentence_std_dev(sentences)
        if std_dev < 3:
            score += 20  # Very uniform = AI-like
        elif std_dev < 5:
            score += 10  # Somewhat uniform
    
    # Check for vague quantifiers
    vague_count = len(re.findall(r"\b(a lot|many|several|most|some|few|a bunch|tons)\b", text.lower()))
    score += vague_count * 3
    
    return min(score, 100)


def main():
    """Test the humanizer with sample text."""
    sample_text = """
    Additionally, it is important to note that research shows a lot of people are confused about this topic. 
    Furthermore, studies indicate that many scientists were wrong about this for decades. 
    In conclusion, this demonstrates how complex the issue really is.
    """
    
    print("Original text:")
    print(sample_text)
    print(f"\nAI Score: {analyze_ai_score(sample_text)}/100")
    
    humanized = humanize_text(sample_text)
    
    print("\nHumanized text:")
    print(humanized)
    print(f"\nAI Score: {analyze_ai_score(humanized)}/100")


if __name__ == "__main__":
    main()
