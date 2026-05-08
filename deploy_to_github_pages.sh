#!/bin/bash
# Deploy portfolio to GitHub Pages
# Usage: ./deploy_to_github_pages.sh

set -e

echo "🚀 GitHub Pages Deployment Helper"
echo "=================================="
echo ""
echo "This script will help you deploy your portfolio to GitHub Pages."
echo ""
echo "Prerequisites:"
echo "  ✓ Git installed"
echo "  ✓ GitHub account"
echo "  ✓ portfolio.html file"
echo ""

# Step 1: Check if git is configured
if ! git config user.name &> /dev/null; then
    echo "⚠️  Git not configured. Setting up..."
    read -p "Enter your name for git commits: " git_name
    read -p "Enter your email for git commits: " git_email
    git config --global user.name "$git_name"
    git config --global user.email "$git_email"
    echo "✅ Git configured"
fi

echo ""
echo "📋 MANUAL STEPS REQUIRED:"
echo "========================"
echo ""
echo "1. Go to https://github.com/new and create a NEW repository:"
echo "   - Repository name: ritika-cv"
echo "   - Description: Interactive CV Portfolio"
echo "   - Make it PUBLIC"
echo "   - Click 'Create repository'"
echo ""
echo "2. Copy the repository URL (should look like):"
echo "   https://github.com/YOUR_USERNAME/ritika-cv.git"
echo ""
read -p "3. Paste your repository URL here: " repo_url

if [ -z "$repo_url" ]; then
    echo "❌ No repository URL provided"
    exit 1
fi

echo ""
echo "⏳ Deploying to GitHub..."
echo ""

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
fi

# Add all files
echo "📝 Adding portfolio files..."
git add portfolio.html
git add -A 2>/dev/null || true

# Check for changes
if git diff --cached --quiet; then
    echo "⚠️  No changes to commit"
    exit 0
fi

# Commit
echo "💾 Committing changes..."
git commit -m "Deploy CV portfolio - $(date +'%Y-%m-%d %H:%M:%S')" || echo "✓ Already up to date"

# Add remote
echo "🔗 Adding remote repository..."
git remote remove origin 2>/dev/null || true
git remote add origin "$repo_url"

# Push
echo "🚀 Pushing to GitHub..."
git push -u origin main --force

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "📋 Next steps:"
echo "  1. Go to: https://github.com/YOUR_USERNAME/ritika-cv/settings"
echo "  2. Scroll down to 'Pages' section"
echo "  3. Select 'Deploy from a branch'"
echo "  4. Select 'main' branch and '/root' folder"
echo "  5. Click 'Save'"
echo ""
echo "🌐 Your portfolio will be available at:"
echo "   https://YOUR_USERNAME.github.io/ritika-cv/"
echo ""
echo "💡 Update config.py with your new URL once GitHub Pages is active"
