#!/usr/bin/env python3
"""
FORCE PUSH to GitHub - Direct execution
Uses subprocess to handle git authentication
"""

import subprocess
import os
import sys

def run_cmd(cmd, description=""):
    """Run command and return output"""
    print(f"\n📤 {description}")
    print(f"   Running: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="/tmp/flag")
        if result.returncode == 0:
            print(f"   ✅ Success")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

def main():
    print("=" * 70)
    print("🚀 FORCE PUSH AI CONTENT DETECTOR TO GITHUB")
    print("=" * 70)
    
    # Check for token
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("\n❌ ERROR: GITHUB_TOKEN not found!")
        print("\nYou MUST provide a GitHub Personal Access Token:")
        print("1. Go to: https://github.com/settings/tokens/new")
        print("2. Select 'repo' scope")
        print("3. Generate token")
        print("4. Run:")
        print("   export GITHUB_TOKEN=your_token_here")
        print("   python3 /tmp/flag/force_push.py")
        sys.exit(1)
    
    print(f"\n✓ Token found ({len(token)} chars)")
    
    # Step 1: Configure git
    print("\n📋 Step 1: Configure Git")
    run_cmd('git config --global user.email "kixu@zenetive.dev"', "Setting email")
    run_cmd('git config --global user.name "Kixu"', "Setting name")
    
    # Step 2: Update remote
    print("\n🔗 Step 2: Update Remote")
    remote_url = f'https://x-access-token:{token}@github.com/Kishoreramu25/flag.git'
    run_cmd(f'git remote set-url origin "{remote_url}"', "Updating remote URL")
    
    # Step 3: Show what will be pushed
    print("\n📊 Step 3: Check Status")
    run_cmd('git log --oneline -3', "Recent commits")
    run_cmd('git status', "Git status")
    
    # Step 4: FORCE PUSH
    print("\n💥 Step 4: FORCE PUSH to main")
    if run_cmd('git push origin main -f', "FORCE PUSH to main branch"):
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Code pushed to GitHub!")
        print("=" * 70)
        print("\n🎉 Your repo is now updated:")
        print("   https://github.com/Kishoreramu25/flag")
        print("\n📂 Files pushed:")
        print("   ✓ frontend/src/ (React components)")
        print("   ✓ backend/ (FastAPI + AI detector)")
        print("   ✓ README.md (documentation)")
        print("\n🚀 Next steps:")
        print("   1. Deploy frontend to Vercel")
        print("   2. Deploy backend to Heroku/Railway/Fly.io")
        print("   3. Connect APIs")
        print("\n" + "=" * 70)
        return 0
    else:
        print("\n❌ Push failed!")
        print("Try running manually:")
        print(f'   git remote set-url origin "{remote_url}"')
        print("   git push origin main -f")
        return 1

if __name__ == "__main__":
    sys.exit(main())
