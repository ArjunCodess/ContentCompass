"""
ContentCompass - Trend Intelligence & Content Planning

Full-featured app with Virlo API integration, Gemini AI, video embeds, and export.
"""
import streamlit as st
import json
import requests
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# ==================== SESSION STATE INIT ====================
if "mode" not in st.session_state:
    st.session_state.mode = None  # None, "demo", "live"
if "virlo_api_key" not in st.session_state:
    st.session_state.virlo_api_key = None
if "credits_used" not in st.session_state:
    st.session_state.credits_used = 0
if "cache" not in st.session_state:
    st.session_state.cache = {}
if "weekly_plan" not in st.session_state:
    st.session_state.weekly_plan = None
if "generated_brief" not in st.session_state:
    st.session_state.generated_brief = None
if "brief_prefill" not in st.session_state:
    st.session_state.brief_prefill = None
if "current_page" not in st.session_state:
    st.session_state.current_page = 0
if "enabled_endpoints" not in st.session_state:
    st.session_state.enabled_endpoints = {
        "trends": True,
        "hashtags": True,
        "videos": True,
    }

# Page config
st.set_page_config(
    page_title="ContentCompass",
    page_icon="🔥",
    layout="wide",
)

# ==================== CONSTANTS ====================
API_BASE = "https://api.virlo.ai"
DEMO_DATA_PATH = Path(__file__).parent / "data" / "demo"
CACHE_FILE = Path(__file__).parent / "data" / ".cache.json"

CREDIT_COSTS = {
    "trends": 1000,
    "hashtags": 10,
    "videos": 100,
}

ENDPOINT_DESCRIPTIONS = {
    "trends": "Today's trending topics",
    "hashtags": "Hashtag analytics & stats", 
    "videos": "Top performing videos",
}

# ==================== GEMINI AI ====================
def get_gemini_key():
    """Get Gemini API key from environment"""
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except:
        pass
    return os.getenv("GEMINI_API_KEY")

def generate_with_ai(prompt: str, fallback: str = "") -> str:
    """Generate content using Gemini AI"""
    api_key = get_gemini_key()
    if not api_key:
        return fallback
    
    try:
        import google.genai as genai
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return response.text
    except Exception as e:
        st.warning(f"AI generation failed: {e}")
        return fallback

# ==================== LOCAL STORAGE ====================
def save_cache_to_file():
    """Save cache to local file for persistence"""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        cache_data = {
            "cache": st.session_state.cache,
            "weekly_plan": st.session_state.weekly_plan,
            "generated_brief": st.session_state.generated_brief,
            "credits_used": st.session_state.credits_used,
            "timestamp": datetime.now().isoformat()
        }
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, default=str)
    except Exception:
        pass

def load_cache_from_file():
    """Load cache from local file on startup"""
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
            st.session_state.cache = cache_data.get("cache", {})
            st.session_state.weekly_plan = cache_data.get("weekly_plan")
            st.session_state.generated_brief = cache_data.get("generated_brief")
            st.session_state.credits_used = cache_data.get("credits_used", 0)
            return True
    except Exception:
        pass
    return False

# Load cache on startup
if "cache_loaded" not in st.session_state:
    load_cache_from_file()
    st.session_state.cache_loaded = True

# ==================== HELPERS ====================
def format_number(num: int) -> str:
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)

def load_demo(filename: str) -> Dict:
    filepath = DEMO_DATA_PATH / filename
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"results": 0, "data": []}

def copy_to_clipboard(text: str):
    st.toast("📋 Copied!")

# ==================== VIRLO API ====================
class VirloAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def _get(self, endpoint: str, params: Dict = None) -> Dict:
        try:
            r = requests.get(f"{API_BASE}{endpoint}", headers=self.headers, params=params, timeout=30)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            st.error(f"API Error: {e}")
            return {"results": 0, "data": []}
    
    def get_trends_digest(self) -> Dict:
        st.session_state.credits_used += CREDIT_COSTS["trends"]
        return self._get("/trends/digest")
    
    def get_hashtags(self, start_date: str, end_date: str, limit: int = 50, order_by: str = "views") -> Dict:
        st.session_state.credits_used += CREDIT_COSTS["hashtags"]
        return self._get("/hashtags", {
            "startDate": start_date,
            "endDate": end_date,
            "limit": limit,
            "orderBy": order_by,
            "sort": "desc"
        })
    
    def get_videos_digest(self, limit: int = 10, niche: str = None) -> Dict:
        st.session_state.credits_used += CREDIT_COSTS["videos"]
        params = {"limit": limit}
        if niche:
            params["niche"] = niche
        return self._get("/videos/digest", params)

def get_data(endpoint: str, force_refresh: bool = False, **kwargs) -> Dict:
    """Get data from API (live) or demo files - with caching"""
    cache_key = f"{endpoint}_{json.dumps(kwargs, sort_keys=True)}"
    
    if not force_refresh and cache_key in st.session_state.cache:
        return st.session_state.cache[cache_key]
    
    if not st.session_state.enabled_endpoints.get(endpoint, True):
        return {"results": 0, "data": []}
    
    if st.session_state.mode == "live" and st.session_state.virlo_api_key:
        api = VirloAPI(st.session_state.virlo_api_key)
        
        if endpoint == "trends":
            data = api.get_trends_digest()
        elif endpoint == "hashtags":
            end = datetime.now()
            start = end - timedelta(days=7)
            data = api.get_hashtags(
                start.strftime("%Y-%m-%d"),
                end.strftime("%Y-%m-%d"),
                kwargs.get("limit", 50),
                kwargs.get("order_by", "views")
            )
        elif endpoint == "videos":
            data = api.get_videos_digest(kwargs.get("limit", 10), kwargs.get("niche"))
        else:
            data = {"results": 0, "data": []}
        
        st.session_state.cache[cache_key] = data
        save_cache_to_file()
    else:
        files = {
            "trends": "trends.json",
            "hashtags": "hashtags.json",
            "videos": "videos.json",
        }
        data = load_demo(files.get(endpoint, "trends.json"))
        st.session_state.cache[cache_key] = data
    
    return data

# ==================== WELCOME SCREEN ====================
def show_welcome():
    st.title("🔥 ContentCompass")
    st.subheader("Trend Intelligence & Content Planning")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Demo Mode")
        st.write("• Explore with sample data")
        st.write("• No API key required")
        st.write("• Perfect for testing")
        if st.button("Try Demo", type="primary", use_container_width=True):
            st.session_state.mode = "demo"
            st.rerun()
    
    with col2:
        st.markdown("### 🔴 Live Mode")
        st.write("• Real-time Virlo API data")
        st.write("• Credit tracking")
        
        api_key = st.text_input("Virlo API Key", type="password", placeholder="vrl_xxx...")
        st.caption("Get your key from [virlo.ai](https://virlo.ai)")
        
        st.markdown("**Select endpoints to fetch:**")
        total_cost = 0
        for endpoint, desc in ENDPOINT_DESCRIPTIONS.items():
            cost = CREDIT_COSTS[endpoint]
            enabled = st.checkbox(f"{desc} (~{cost:,} credits)", value=True, key=f"endpoint_{endpoint}")
            st.session_state.enabled_endpoints[endpoint] = enabled
            if enabled:
                total_cost += cost
        
        st.info(f"💰 **Estimated initial cost:** ~{total_cost:,} credits")
        
        if st.button("Connect & Go Live", use_container_width=True, disabled=not api_key):
            st.session_state.mode = "live"
            st.session_state.virlo_api_key = api_key
            st.session_state.cache = {}
            st.rerun()

# ==================== TREND HUB (with Hashtag Lab merged) ====================
def show_trend_hub():
    st.title("📊 Trend Hub")
    
    # Get data
    trends_data = get_data("trends")
    trend_groups = trends_data.get("data", [])
    trends = trend_groups[0].get("trends", []) if trend_groups else []
    
    hashtag_data = get_data("hashtags", limit=50, order_by="views")
    hashtags = hashtag_data.get("data", [])
    
    # Top stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Trends", len(trends))
    with col2:
        st.metric("Hashtags", len(hashtags))
    with col3:
        st.metric("Credits Used", format_number(st.session_state.credits_used))
    with col4:
        mode = "🔴 Live" if st.session_state.mode == "live" else "📊 Demo"
        st.metric("Mode", mode)
    
    st.divider()
    
    # Hero: Top 3 trends
    if trends:
        st.subheader("🌟 Top Trends")
        cols = st.columns(3)
        labels = ["🔥 Hottest", "📈 Rising", "🌪️ Emerging"]
        
        for i, col in enumerate(cols):
            if i < len(trends):
                t = trends[i]
                trend_info = t.get("trend", {})
                name = trend_info.get("name", "Unknown")
                desc = trend_info.get("description", "")[:80]
                
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{labels[i]}**")
                        st.markdown(f"### {name}")
                        st.caption(desc + "...")
        
        st.divider()
    
    # Hashtag Strategies
    if hashtags:
        st.subheader("🎯 Hashtag Strategies")
        
        safe = hashtags[:4] if len(hashtags) >= 4 else hashtags
        aggressive = hashtags[4:8] if len(hashtags) >= 8 else hashtags[2:6]
        gems = hashtags[-4:] if len(hashtags) >= 4 else hashtags
        
        cols = st.columns(3)
        sets = [
            ("Set A: Safe Play", safe, "Mid competition, stable reach"),
            ("Set B: Aggressive", aggressive, "High reach, competitive"),
            ("Set C: Hidden Gems", gems, "Low competition, rising fast"),
        ]
        
        for i, (title, tags, desc) in enumerate(sets):
            with cols[i]:
                with st.container(border=True):
                    st.markdown(f"**{title}**")
                    tag_str = " ".join([h.get("hashtag", "") for h in tags])
                    st.code(tag_str)
                    st.caption(desc)
                    if st.button("📋 Copy", key=f"copy_set_{i}", use_container_width=True):
                        copy_to_clipboard(tag_str)
        
        st.divider()
    
    # All Hashtags
    if hashtags:
        st.subheader("📋 All Hashtags")
        search = st.text_input("Search hashtags", placeholder="Filter...")
        
        filtered = hashtags
        if search:
            filtered = [h for h in hashtags if search.lower() in h.get("hashtag", "").lower()]
        
        cols = st.columns(4)
        for idx, h in enumerate(filtered[:16]):
            tag = h.get("hashtag", "")
            count = h.get("count", 0)
            views = h.get("total_views", 0)
            
            with cols[idx % 4]:
                with st.container(border=True):
                    st.markdown(f"**{tag}**")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.caption(f"📊 {format_number(count)}")
                    with c2:
                        st.caption(f"👁️ {format_number(views)}")
                    if st.button("📋 Copy", key=f"copy_tag_{idx}", use_container_width=True):
                        copy_to_clipboard(tag)
        
        st.divider()
    
    # All Trends
    if trends:
        st.subheader("📋 All Trends")
        cols = st.columns(4)
        
        for idx, t in enumerate(trends):
            trend_info = t.get("trend", {})
            name = trend_info.get("name", "Unknown")
            desc = trend_info.get("description", "")[:60]
            ranking = t.get("ranking", idx + 1)
            
            with cols[idx % 4]:
                with st.container(border=True):
                    st.markdown(f"**#{ranking} {name}**")
                    st.caption(desc + "...")

# ==================== VIDEO VAULT ====================
def show_video_vault():
    st.title("🎬 Video Vault")
    
    # Get video data first for insights
    data = get_data("videos", limit=20)
    videos = data.get("data", [])
    
    # Insights at top
    if videos:
        st.subheader("📊 Insights")
        lengths = [v.get("duration", 0) for v in videos if v.get("duration")]
        avg_len = sum(lengths) / len(lengths) if lengths else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Length", f"{int(avg_len)}s")
        with col2:
            total_views = sum(v.get("views", 0) for v in videos)
            st.metric("Total Views", format_number(total_views))
        with col3:
            st.metric("Videos Analyzed", len(videos))
        
        st.divider()
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        platform_filter = st.selectbox("Platform", ["All", "YouTube", "TikTok"])
    with col2:
        limit = st.slider("Videos to show", 5, 20, 12)
    
    if not videos:
        st.warning("No videos found")
        return
    
    # Filter by platform
    filtered = videos
    if platform_filter != "All":
        filtered = [v for v in videos if v.get("type", "").lower() == platform_filter.lower()]
    
    st.divider()
    
    # Video grid
    cols = st.columns(4)
    for idx, v in enumerate(filtered[:limit]):
        with cols[idx % 4]:
            with st.container(border=True):
                vid_type = v.get("type", "").upper()
                views = v.get("views", 0)
                desc = v.get("description", "")[:50]
                duration = v.get("duration", 0)
                hashtags = v.get("hashtags", [])
                url = v.get("url", "#")
                external_id = v.get("external_id", "")
                
                st.caption(f"📹 {vid_type} • {duration}s")
                st.markdown(f"**{desc}**...")
                st.caption(f"👁️ {format_number(views)} views")
                
                if hashtags:
                    st.caption(f"🏷️ {' '.join(hashtags[:3])}")
                
                c1, c2 = st.columns(2)
                with c1:
                    with st.expander("▶️ Watch"):
                        if vid_type.lower() == "youtube" and external_id:
                            st.markdown(f'''
                            <iframe width="100%" height="200" 
                                src="https://www.youtube.com/embed/{external_id}" 
                                frameborder="0" allowfullscreen>
                            </iframe>
                            ''', unsafe_allow_html=True)
                        else:
                            st.link_button("Open →", url, use_container_width=True)
                with c2:
                    if st.button("📋 Tags", key=f"vid_copy_{idx}"):
                        copy_to_clipboard(" ".join(hashtags))

# ==================== WEEKLY BLUEPRINT ====================
def show_weekly_blueprint():
    st.title("📋 Weekly Blueprint")
    st.write("Get 5 AI-generated content ideas for the week.")
    
    # Setup
    col1, col2, col3 = st.columns(3)
    with col1:
        niche = st.text_input("Your Niche", placeholder="e.g., Tech, Fitness, Comedy")
    with col2:
        platform = st.selectbox("Platform", ["TikTok", "YouTube Shorts", "Instagram Reels"])
    with col3:
        tone = st.selectbox("Tone", ["Funny", "Educational", "Dramatic", "Inspirational"])
    
    if st.button("✨ Generate My Week", type="primary", use_container_width=True, disabled=not niche):
        with st.spinner("🤖 AI is crafting your content ideas..."):
            # Get trends for context
            trends_data = get_data("trends")
            trend_groups = trends_data.get("data", [])
            trends = trend_groups[0].get("trends", []) if trend_groups else []
            
            trend_names = [t.get("trend", {}).get("name", "") for t in trends[:5]]
            trends_context = ", ".join(trend_names) if trend_names else "general viral content"
            
            # AI prompt
            prompt = f"""Generate 5 content ideas for a {niche} creator on {platform} with a {tone} tone.
            
Current trending topics: {trends_context}

For each day (Monday-Friday), provide:
1. A specific video idea (1 sentence)
2. An engaging hook (first line to capture attention)
3. 3 relevant hashtags
4. Difficulty level (Easy/Medium/Hard)
5. Best posting time in UTC

Format as JSON array with keys: day, trend, video_idea, hook, hashtags (array), difficulty, best_time
Return ONLY valid JSON, no markdown."""

            fallback_ideas = []
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            for i, day in enumerate(days):
                trend = trend_names[i] if i < len(trend_names) else f"{niche} tips"
                fallback_ideas.append({
                    "day": day,
                    "trend": trend,
                    "video_idea": f"Create a {tone.lower()} {platform} video about {trend}",
                    "hook": f"POV: You just discovered {trend}...",
                    "hashtags": ["#fyp", "#viral", f"#{niche.lower().replace(' ', '')}"],
                    "difficulty": ["Easy", "Medium", "Hard"][i % 3],
                    "best_time": f"{14 + i % 4}:00 UTC"
                })
            
            ai_response = generate_with_ai(prompt, "")
            
            ideas = fallback_ideas
            if ai_response:
                try:
                    # Try to parse AI response
                    clean = ai_response.strip()
                    if clean.startswith("```"):
                        clean = clean.split("```")[1]
                        if clean.startswith("json"):
                            clean = clean[4:]
                    parsed = json.loads(clean)
                    if isinstance(parsed, list) and len(parsed) >= 5:
                        ideas = parsed[:5]
                except:
                    pass  # Use fallback
            
            st.session_state.weekly_plan = {"ideas": ideas, "niche": niche, "platform": platform}
            save_cache_to_file()
            st.rerun()
    
    st.divider()
    
    # Show plan
    plan = st.session_state.weekly_plan
    if plan:
        ideas = plan.get("ideas", [])
        
        cols = st.columns(2)
        for idx, idea in enumerate(ideas):
            with cols[idx % 2]:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"### {idea.get('day', f'Day {idx+1}')}")
                        st.caption(idea.get('trend', ''))
                    with c2:
                        st.caption(f"⭐ {idea.get('difficulty', 'Medium')}")
                    
                    st.write(f"📹 {idea.get('video_idea', '')}")
                    st.write(f"🎬 _{idea.get('hook', '')}_")
                    
                    hashtags = idea.get('hashtags', [])
                    if isinstance(hashtags, list):
                        tag_str = " ".join(hashtags)
                    else:
                        tag_str = str(hashtags)
                    st.code(tag_str)
                    
                    st.caption(f"⏰ {idea.get('best_time', '14:00 UTC')}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Use", key=f"use_{idx}", use_container_width=True):
                            st.session_state.brief_prefill = idea
                            st.session_state.current_page = 2  # Brief Creator
                            st.toast("✅ Go to **Brief Creator**")
                    with c2:
                        if st.button("📋 Copy", key=f"copy_idea_{idx}", use_container_width=True):
                            copy_to_clipboard(f"{idea.get('day', '')}: {idea.get('video_idea', '')}\n{tag_str}")
        
        st.divider()
        
        # Export entire plan
        plan_text = f"WEEKLY CONTENT PLAN\nNiche: {plan.get('niche', 'General')} | Platform: {plan.get('platform', 'TikTok')}\n\n"
        for idea in ideas:
            hashtags = idea.get('hashtags', [])
            tag_str = " ".join(hashtags) if isinstance(hashtags, list) else str(hashtags)
            plan_text += f"""=== {idea.get('day', '')} ===
Trend: {idea.get('trend', '')}
Idea: {idea.get('video_idea', '')}
Hook: {idea.get('hook', '')}
Hashtags: {tag_str}
Difficulty: {idea.get('difficulty', '')} | Best Time: {idea.get('best_time', '')}

"""
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                "📄 Download Plan (.txt)",
                plan_text,
                file_name=f"weekly_plan_{plan.get('niche', 'content').replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            if st.button("📋 Copy All", use_container_width=True):
                copy_to_clipboard(plan_text)
        with col3:
            if st.button("🗑️ Clear Plan", use_container_width=True):
                st.session_state.weekly_plan = None
                save_cache_to_file()
                st.rerun()
    else:
        st.info("👆 Enter your niche and click 'Generate My Week'")

# ==================== BRIEF CREATOR ====================
def show_brief_creator():
    st.title("📄 Brief Creator")
    st.write("Create AI-powered professional content briefs.")
    
    prefill = st.session_state.brief_prefill
    
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Topic/Trend", value=prefill.get("trend", "") if prefill else "")
    with col2:
        niche = st.text_input("Your Niche", value="General", placeholder="e.g., Tech, Fitness")
    
    description = st.text_area(
        "Description (optional)",
        value=prefill.get("video_idea", "") if prefill else "",
        placeholder="Describe the trend or your content idea..."
    )
    
    if st.button("✨ Generate Brief", type="primary", use_container_width=True, disabled=not topic):
        with st.spinner("🤖 AI is creating your brief..."):
            # AI prompt
            prompt = f"""Create a professional content brief for a creator making a video about "{topic}" in the {niche} niche.

Include:
1. Why This Trend (2-3 sentences on why it's relevant now)
2. What To Create:
   - Video format recommendation
   - Suggested length
   - Hook copy (attention-grabbing first line)
   - Best posting time
3. Hashtag Strategy:
   - 4 safe hashtags (mid competition)
   - 4 aggressive hashtags (high reach)
   - 3 hidden gem hashtags (low competition)

Additional context: {description}

Format as JSON with keys: why_this_trend, format, length, hook_copy, best_time, safe_hashtags, aggressive_hashtags, gem_hashtags
Return ONLY valid JSON, no markdown."""

            # Fallback brief
            fallback = {
                "why_this_trend": f"The {topic} trend is gaining momentum and presents a timely opportunity for creators in the {niche} space.",
                "format": "Vertical video, fast-paced editing",
                "length": "30-60 seconds",
                "hook_copy": prefill.get("hook", f"Wait... is this really {topic}? 🤯") if prefill else f"Wait... is this really {topic}? 🤯",
                "best_time": prefill.get("best_time", "2-4 PM UTC") if prefill else "2-4 PM UTC",
                "safe_hashtags": ["#fyp", "#viral", "#trending", "#foryou"],
                "aggressive_hashtags": ["#fyp", "#foryou", "#explore", "#viral"],
                "gem_hashtags": ["#newtrend", "#underrated", "#mustwatch"]
            }
            
            ai_response = generate_with_ai(prompt, "")
            
            brief_data = fallback
            if ai_response:
                try:
                    clean = ai_response.strip()
                    if clean.startswith("```"):
                        clean = clean.split("```")[1]
                        if clean.startswith("json"):
                            clean = clean[4:]
                    parsed = json.loads(clean)
                    if isinstance(parsed, dict):
                        brief_data = {**fallback, **parsed}
                except:
                    pass
            
            brief = {
                "trend_name": topic,
                "niche": niche,
                "prepared_date": datetime.now().strftime("%Y-%m-%d"),
                "description": description,
                "sections": brief_data
            }
            
            st.session_state.generated_brief = brief
            st.session_state.brief_prefill = None
            save_cache_to_file()
            st.rerun()
    
    st.divider()
    
    # Display brief
    brief = st.session_state.generated_brief
    if brief:
        st.subheader(f"🔥 {brief['trend_name']}")
        st.caption(f"Niche: {brief['niche']} | Prepared: {brief['prepared_date']}")
        
        s = brief["sections"]
        
        st.markdown("**💡 Why This Trend**")
        st.write(s.get("why_this_trend", ""))
        
        st.markdown("**🎬 What to Create**")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Format: {s.get('format', 'Vertical video')}")
            st.write(f"Length: {s.get('length', '30-60 seconds')}")
        with col2:
            st.write(f"Best time: {s.get('best_time', '2-4 PM UTC')}")
        st.write(f"Hook: _{s.get('hook_copy', '')}_")
        
        st.markdown("**🏷️ Hashtag Strategy**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("Safe")
            tags = s.get("safe_hashtags", [])
            st.code(" ".join(tags) if isinstance(tags, list) else str(tags))
        with col2:
            st.caption("Aggressive")
            tags = s.get("aggressive_hashtags", [])
            st.code(" ".join(tags) if isinstance(tags, list) else str(tags))
        with col3:
            st.caption("Hidden Gems")
            tags = s.get("gem_hashtags", [])
            st.code(" ".join(tags) if isinstance(tags, list) else str(tags))
        
        st.divider()
        
        # Export
        brief_text = f"""CONTENT BRIEF: {brief['trend_name']}
Niche: {brief['niche']} | Date: {brief['prepared_date']}

WHY THIS TREND
{s.get('why_this_trend', '')}

WHAT TO CREATE
Format: {s.get('format', '')}
Length: {s.get('length', '')}
Hook: {s.get('hook_copy', '')}
Best time: {s.get('best_time', '')}

HASHTAGS
Safe: {' '.join(s.get('safe_hashtags', [])) if isinstance(s.get('safe_hashtags'), list) else s.get('safe_hashtags', '')}
Aggressive: {' '.join(s.get('aggressive_hashtags', [])) if isinstance(s.get('aggressive_hashtags'), list) else s.get('aggressive_hashtags', '')}
Gems: {' '.join(s.get('gem_hashtags', [])) if isinstance(s.get('gem_hashtags'), list) else s.get('gem_hashtags', '')}
"""
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                "📄 Download Brief",
                brief_text,
                file_name=f"brief_{topic.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            if st.button("📋 Copy Brief", use_container_width=True):
                copy_to_clipboard(brief_text)
        with col3:
            if st.button("🗑️ Clear Brief", use_container_width=True):
                st.session_state.generated_brief = None
                save_cache_to_file()
                st.rerun()
    else:
        st.info("Enter a topic and generate your brief")

# ==================== SETTINGS ====================
def show_settings():
    st.title("⚙️ Settings")
    
    mode = "🔴 Live" if st.session_state.mode == "live" else "📊 Demo"
    st.write(f"**Current Mode:** {mode}")
    st.write(f"**Credits Used:** {format_number(st.session_state.credits_used)}")
    
    gemini_status = "✅ Connected" if get_gemini_key() else "❌ Not configured"
    st.write(f"**Gemini AI:** {gemini_status}")
    
    st.divider()
    
    st.subheader("Switch Mode")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Switch to Demo", use_container_width=True, disabled=st.session_state.mode == "demo"):
            st.session_state.mode = "demo"
            st.session_state.virlo_api_key = None
            st.session_state.cache = {}
            save_cache_to_file()
            st.rerun()
    
    with col2:
        new_key = st.text_input("New API Key", type="password")
        if st.button("Go Live", use_container_width=True, disabled=not new_key):
            st.session_state.mode = "live"
            st.session_state.virlo_api_key = new_key
            st.session_state.cache = {}
            save_cache_to_file()
            st.rerun()
    
    st.divider()
    
    st.subheader("Data")
    if st.button("🗑️ Clear Cache", use_container_width=True):
        st.session_state.cache = {}
        st.session_state.weekly_plan = None
        st.session_state.generated_brief = None
        save_cache_to_file()
        st.toast("Cache cleared!")
    
    if st.button("🔄 Reset App", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
        st.rerun()

# ==================== MAIN ====================
def main():
    if not st.session_state.mode:
        show_welcome()
        return
    
    with st.sidebar:
        st.title("🔥 ContentCompass")
        
        mode_label = "🔴 Live" if st.session_state.mode == "live" else "📊 Demo"
        st.caption(f"{mode_label} | {format_number(st.session_state.credits_used)} credits")
        
        st.divider()
        
        pages = ["📊 Trend Hub", "🎬 Video Vault", "📋 Weekly Blueprint", "📄 Brief Creator", "⚙️ Settings"]
        
        page = st.radio(
            "Navigate",
            pages,
            index=min(st.session_state.current_page, len(pages) - 1),
            label_visibility="collapsed",
            key="nav_radio"
        )
        
        st.session_state.current_page = pages.index(page)
        
        st.divider()
        
        # Data refresh
        st.caption("💾 Data")
        refresh_options = ["All Data", "Trends", "Hashtags", "Videos"]
        refresh_target = st.selectbox("Refresh", refresh_options, label_visibility="collapsed")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            if refresh_target == "All Data":
                st.session_state.cache = {}
            else:
                target_key = refresh_target.lower()
                keys_to_remove = [k for k in st.session_state.cache.keys() if target_key in k]
                for k in keys_to_remove:
                    del st.session_state.cache[k]
            save_cache_to_file()
            st.toast(f"✅ {refresh_target} refreshed!")
            st.rerun()
        
        st.divider()
        
        if st.session_state.mode == "demo":
            st.caption("Ready for real data?")
            key = st.text_input("API Key", type="password", key="sidebar_key")
            if st.button("Go Live 🔴", use_container_width=True, disabled=not key):
                st.session_state.mode = "live"
                st.session_state.virlo_api_key = key
                st.session_state.cache = {}
                st.rerun()
    
    # Page routing
    if page == "📊 Trend Hub":
        show_trend_hub()
    elif page == "🎬 Video Vault":
        show_video_vault()
    elif page == "📋 Weekly Blueprint":
        show_weekly_blueprint()
    elif page == "📄 Brief Creator":
        show_brief_creator()
    elif page == "⚙️ Settings":
        show_settings()

if __name__ == "__main__":
    main()
