#!/usr/bin/env python3
"""
GitHub Push Script - AI Content Detector
Pushes code to GitHub using REST API instead of Git protocol
"""

import os
import sys
import json
import base64
import subprocess
from pathlib import Path
from typing import Optional

def get_token() -> Optional[str]:
    """Get GitHub token from environment or user input"""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ Error: GITHUB_TOKEN not found")
        print("\nTo use this script:")
        print("1. Create a token: https://github.com/settings/tokens/new")
        print("   - Give it 'repo' scope")
        print("2. Set environment variable:")
        print("   export GITHUB_TOKEN=your_token_here")
        print("3. Run this script again")
        sys.exit(1)
    return token

def push_with_git(token: str, repo: str, branch: str) -> bool:
    """Push using git with token"""
    try:
        repo_url = f"https://x-access-token:{token}@github.com/{repo}.git"
        
        # Configure git
        os.system(f"git config --local user.email 'ci@flagdetector.dev'")
        os.system(f"git config --local user.name 'Flag Detector CI'")
        
        # Update remote
        os.system(f"git remote set-url origin '{repo_url}'")
        
        # Push
        result = os.system(f"git push origin {branch} 2>&1")
        
        if result == 0:
            return True
        return False
    except Exception as e:
        print(f"❌ Git push error: {e}")
        return False

def main():
    print("🚀 AI Content Detector - GitHub Push")
    print("=" * 50)
    print()
    
    REPO = "Kishoreramu25/flag"
    BRANCH = "main"
    REPO_PATH = "/tmp/flag"
    
    print(f"📦 Repository: {REPO}")
    print(f"🌿 Branch: {BRANCH}")
    print(f"📂 Path: {REPO_PATH}")
    print()
    
    # Get token
    token = get_token()
    print("✓ Token found")
    
    # Change to repo directory
    os.chdir(REPO_PATH)
    
    # Show status
    print("\n📊 Git Status:")
    os.system("git status --short")
    
    print("\n📍 Latest commits:")
    os.system("git log --oneline -3")
    
    # Push
    print("\n📤 Pushing to GitHub...")
    print("-" * 50)
    
    if push_with_git(token, REPO, BRANCH):
        print("-" * 50)
        print("\n✅ SUCCESS!")
        print()
        print("🎉 Your code is now on GitHub!")
        print(f"   https://github.com/{REPO}")
        print()
        print("Next steps:")
        print("1. ✅ Code pushed to main branch")
        print("2. 📂 Frontend: Deploy to Vercel")
        print("   - Run: npm run build && vercel deploy")
        print("3. 🔧 Backend: Deploy to Heroku/Railway/Fly.io")
        print("   - Python 3.10+, Port 8000")
        print("4. 🔗 Connect: Update VITE_BACKEND_URL env var")
        print()
        print("Your AI Content Detector is ready for production! 🚀")
        return 0
    else:
        print("-" * 50)
        print("\n❌ Push failed!")
        print("\nTroubleshooting:")
        print("1. Check token validity")
        print("2. Verify 'repo' scope is enabled")
        print("3. Check network connection")
        print("4. Try manually: git push origin main")
        return 1

if __name__ == "__main__":
    sys.exit(main())
