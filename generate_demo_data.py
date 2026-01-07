"""
Demo Data Generator for ContentCompass

Fetches REAL data from Virlo API and saves as demo data.
Uses VIRLO_API_KEY from .env file.

Usage: python generate_demo_data.py
"""
import json
import os
import requests
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Output directory
DEMO_DIR = Path(__file__).parent / "data" / "demo"
API_BASE = "https://api.virlo.ai"

def get_api_key():
    """Get Virlo API key from environment"""
    api_key = os.getenv("VIRLO_API_KEY")
    if not api_key:
        print("❌ Error: VIRLO_API_KEY not found in .env file")
        print("   Please add: VIRLO_API_KEY=your_key_here")
        exit(1)
    
    # Clean up the key (remove quotes, whitespace)
    api_key = api_key.strip().strip('"').strip("'")
    
    # Debug output
    print(f"   Key length: {len(api_key)}")
    print(f"   Key prefix: {api_key[:15]}...")
    
    return api_key

def api_get(endpoint: str, api_key: str, params: dict = None) -> dict:
    """Make API request to Virlo"""
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        r = requests.get(f"{API_BASE}{endpoint}", headers=headers, params=params, timeout=30)
        if r.status_code == 401:
            print(f"❌ 401 Unauthorized for {endpoint}")
            print(f"   Response: {r.text}")
            print(f"   Check your VIRLO_API_KEY in .env file")
            return {"results": 0, "data": []}
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        print(f"❌ API Error for {endpoint}: {e}")
        return {"results": 0, "data": []}

def fetch_trends(api_key: str) -> dict:
    """Fetch trends from Virlo API"""
    print("📊 Fetching trends...")
    return api_get("/trends/digest", api_key)

def fetch_hashtags(api_key: str) -> dict:
    """Fetch hashtags from Virlo API"""
    print("🏷️ Fetching hashtags...")
    end = datetime.now()
    start = end - timedelta(days=7)
    return api_get("/hashtags", api_key, {
        "startDate": start.strftime("%Y-%m-%d"),
        "endDate": end.strftime("%Y-%m-%d"),
        "limit": 50,
        "orderBy": "views",
        "sort": "desc"
    })

def fetch_videos(api_key: str) -> dict:
    """Fetch videos from Virlo API"""
    print("🎬 Fetching videos...")
    return api_get("/videos/digest", api_key, {"limit": 20})

def fetch_niches(api_key: str) -> dict:
    """Fetch niches from Virlo API"""
    print("🎯 Fetching niches...")
    return api_get("/niches", api_key)

def generate_weekly_plan(trends_data: dict) -> dict:
    """Generate weekly plan from trends data"""
    print("📋 Generating weekly plan from trends...")
    
    trend_groups = trends_data.get("data", [])
    trends = trend_groups[0].get("trends", []) if trend_groups else []
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    ideas = []
    
    for i, day in enumerate(days):
        if i < len(trends):
            t = trends[i]
            trend_info = t.get("trend", {})
            ideas.append({
                "day": day,
                "trend": trend_info.get("name", f"Trend {i+1}"),
                "description": trend_info.get("description", ""),
                "video_idea": f"Create a video about {trend_info.get('name', 'this trend')}",
                "hook": f"POV: You just discovered {trend_info.get('name', 'this')}...",
                "hashtags": ["#fyp", "#viral", f"#{trend_info.get('name', 'trend').replace(' ', '').lower()[:15]}"],
                "difficulty": ["Easy", "Medium", "Hard"][i % 3],
                "best_time": f"{14 + i % 4}:00 UTC"
            })
    
    return {
        "ideas": ideas,
        "niche": "General",
        "platform": "TikTok",
        "generated_at": datetime.now().isoformat()
    }

def generate_brief_template(trends_data: dict) -> dict:
    """Generate brief template from first trend"""
    print("📄 Generating brief template...")
    
    trend_groups = trends_data.get("data", [])
    trends = trend_groups[0].get("trends", []) if trend_groups else []
    
    if trends:
        trend_info = trends[0].get("trend", {})
        trend_name = trend_info.get("name", "Trending Topic")
        trend_desc = trend_info.get("description", "")
    else:
        trend_name = "Trending Topic"
        trend_desc = "This trend is gaining momentum."
    
    return {
        "trend_name": trend_name,
        "niche": "General",
        "prepared_date": datetime.now().strftime("%Y-%m-%d"),
        "sections": {
            "why_this_trend": trend_desc or f"The {trend_name} trend is gaining momentum and presents a timely opportunity for creators.",
            "what_to_create": {
                "format": "Vertical video, 30-60 seconds",
                "hook_copy": f"Wait until you see this... 🤯",
                "best_posting_time": "2-4 PM UTC"
            },
            "hashtag_strategy": {
                "safe_set": {"tags": ["#fyp", "#viral", "#trending"]},
                "aggressive_set": {"tags": ["#fyp", "#foryou", "#explore", "#viral"]},
                "hidden_gems": {"tags": ["#newtrend", "#underrated", "#mustwatch"]}
            }
        }
    }

def main():
    """Fetch real data from Virlo and save as demo files"""
    print("🔥 ContentCompass Demo Data Generator")
    print("=" * 50)
    print("Fetching REAL data from Virlo API...")
    print()
    
    # Get API key
    api_key = get_api_key()
    print(f"✅ API key loaded from .env")
    print()
    
    # Create directory
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {DEMO_DIR}")
    print()
    
    # Fetch data from API
    trends_data = fetch_trends(api_key)
    hashtags_data = fetch_hashtags(api_key)
    videos_data = fetch_videos(api_key)
    niches_data = fetch_niches(api_key)
    
    # Generate derived data
    weekly_plan = generate_weekly_plan(trends_data)
    brief_template = generate_brief_template(trends_data)
    
    # Save files
    files = {
        "trends.json": trends_data,
        "hashtags.json": hashtags_data,
        "videos.json": videos_data,
        "niches.json": niches_data,
        "weekly_plan.json": weekly_plan,
        "brief_template.json": brief_template,
    }
    
    print()
    print("💾 Saving files...")
    for filename, data in files.items():
        filepath = DEMO_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Show result count
        count = data.get("results", len(data.get("data", data.get("ideas", []))))
        print(f"   ✅ {filename} ({count} items)")
    
    print()
    print("=" * 50)
    print("✨ Demo data generation complete!")
    print()
    print("📊 Summary:")
    print(f"   • Trends: {trends_data.get('results', 0)} groups")
    print(f"   • Hashtags: {hashtags_data.get('results', 0)}")
    print(f"   • Videos: {videos_data.get('results', 0)}")
    print(f"   • Niches: {niches_data.get('results', 0)}")
    print(f"   • Weekly Plan: {len(weekly_plan.get('ideas', []))} ideas")
    print()
    print("🎉 You can now run the app in Demo mode with real data!")

if __name__ == "__main__":
    main()
