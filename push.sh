#!/bin/bash

# GitHub Push Script for AI Content Detector
# This will push the latest commit to your main branch

echo "🚀 AI Content Detector - GitHub Push Script"
echo "=========================================="
echo ""

# Check if token is provided
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN environment variable not set"
    echo ""
    echo "To push to GitHub, you need a Personal Access Token:"
    echo ""
    echo "1. Go to: https://github.com/settings/tokens/new"
    echo "2. Create a token with 'repo' scope"
    echo "3. Copy the token"
    echo "4. Run this script:"
    echo ""
    echo "   GITHUB_TOKEN=your_token_here bash push.sh"
    echo ""
    exit 1
fi

REPO="Kishoreramu25/flag"
BRANCH="main"

echo "📦 Repository: $REPO"
echo "🌿 Branch: $BRANCH"
echo ""

cd /tmp/flag

# Show what will be pushed
echo "📊 Changes to push:"
git log origin/main..HEAD --oneline 2>/dev/null || echo "   ✓ Local commits ready"
echo ""

# Get current commit
COMMIT_SHA=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)

echo "📍 Latest commit:"
echo "   SHA: $COMMIT_SHA"
echo "   Message: $COMMIT_MSG"
echo ""

# Try HTTPS push with token
echo "🔐 Authenticating with GitHub..."
git remote set-url origin "https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO}.git"

echo "📤 Pushing to GitHub..."
if git push origin main; then
    echo ""
    echo "✅ SUCCESS! Code pushed to GitHub"
    echo ""
    echo "🎉 Your repo is now live:"
    echo "   https://github.com/$REPO"
    echo ""
    echo "Next steps:"
    echo "1. ✓ Code pushed"
    echo "2. → Deploy frontend to Vercel"
    echo "3. → Deploy backend to Heroku/Railway/Fly.io"
    echo "4. → Update VITE_BACKEND_URL env var"
else
    echo ""
    echo "❌ Push failed. Possible reasons:"
    echo "   - Invalid token"
    echo "   - Token lacks 'repo' scope"
    echo "   - Network issue"
    echo ""
    echo "Check your token: https://github.com/settings/tokens"
fi
