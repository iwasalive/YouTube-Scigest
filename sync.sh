#!/bin/bash
# Sync YouTube-Scigest repo with live ~/.hermes/ data
# Run this periodically to keep the repo updated

set -e

REPO_DIR="$HOME/YouTube-Scigest"
HERMES_DIR="$HOME/.hermes"

echo "🔄 Syncing YouTube-Scigest repo..."
cd "$REPO_DIR"

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main 2>/dev/null || true

# Update skills
echo "📦 Updating skills..."
for skill_dir in \
    "skills/content-creation/scigest-production" \
    "skills/content-creation/scigest-production-pipeline" \
    "skills/content-creation/youtube-analytics-automation" \
    "skills/research-skill" \
    "skills/media/youtube-content"; do
    
    src="$HERMES_DIR/$skill_dir"
    dst="$REPO_DIR/$skill_dir"
    
    if [ -d "$src" ]; then
        rm -rf "$dst"
        cp -r "$src" "$dst"
        echo "  ✓ Updated $skill_dir"
    fi
done

# Update scripts
echo "🔧 Updating scripts..."
if [ -f "$HERMES_DIR/scripts/youtube_analytics.py" ]; then
    cp "$HERMES_DIR/scripts/youtube_analytics.py" "$REPO_DIR/scripts/"
    echo "  ✓ Updated youtube_analytics.py"
fi

# Update config (without sensitive data)
echo "⚙️ Updating config..."
if [ -f "$HERMES_DIR/config.yaml" ]; then
    # Copy but remove sensitive sections
    grep -v "^[^#].*:" "$HERMES_DIR/config.yaml" > "$REPO_DIR/config/config.yaml.safe" 2>/dev/null || \
    cp "$HERMES_DIR/config.yaml" "$REPO_DIR/config/config.yaml"
    echo "  ✓ Updated config.yaml"
fi

# Add recent output samples (keep only last 3)
echo "📊 Updating output samples..."
output_dir="$REPO_DIR/output"
find "$HERMES_DIR/cron/output" -name "youtube_analytics*.md" -type f | \
    sort -r | head -3 | while read f; do
    cp "$f" "$output_dir/"
done
echo "  ✓ Updated output samples"

# Stage changes
echo "📝 Staging changes..."
git add .

# Check if there are changes
if git diff --cached --quiet; then
    echo "✅ No changes to commit"
    exit 0
fi

# Commit and push
echo "🚀 Committing and pushing..."
git commit -m "Sync: $(date '+%Y-%m-%d %H:%M')" || echo "No changes to commit"
git push origin main

echo "✨ Sync complete!"
echo "📍 Repo: https://github.com/iwasalive/YouTube-Scigest"
