"""
TrendForge - Trend Intelligence & Content Planning

Full-featured app with Virlo API integration, video embeds, and export.
"""
import streamlit as st
import json
import requests
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
        "niches": True
    }

# Page config
st.set_page_config(
    page_title="TrendForge",
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
    "niches": 50,
}

ENDPOINT_DESCRIPTIONS = {
    "trends": "Today's trending topics",
    "hashtags": "Hashtag analytics & stats", 
    "videos": "Top performing videos",
    "niches": "Content categories list",
}

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
        pass  # Silently fail on cache save errors

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

def format_growth(growth: int) -> str:
    if growth > 0:
        return f"+{growth}%"
    return f"{growth}%"

def load_demo(filename: str) -> Dict:
    filepath = DEMO_DATA_PATH / filename
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"results": 0, "data": []}

def copy_to_clipboard(text: str):
    """Show toast for clipboard action"""
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
    
    def get_niches(self) -> Dict:
        st.session_state.credits_used += CREDIT_COSTS["niches"]
        return self._get("/niches")

def get_data(endpoint: str, force_refresh: bool = False, **kwargs) -> Dict:
    """Get data from API (live) or demo files - with caching"""
    cache_key = f"{endpoint}_{json.dumps(kwargs, sort_keys=True)}"
    
    # Check cache first (unless force refresh)
    if not force_refresh and cache_key in st.session_state.cache:
        return st.session_state.cache[cache_key]
    
    # Check if endpoint is enabled
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
        elif endpoint == "niches":
            data = api.get_niches()
        else:
            data = {"results": 0, "data": []}
        
        # Save to cache and persist
        st.session_state.cache[cache_key] = data
        save_cache_to_file()
    else:
        # Demo mode
        files = {
            "trends": "trends.json",
            "hashtags": "hashtags.json",
            "videos": "videos.json",
            "niches": "niches.json",
        }
        data = load_demo(files.get(endpoint, "trends.json"))
        st.session_state.cache[cache_key] = data
    
    return data

# ==================== WELCOME SCREEN ====================
def show_welcome():
    st.title("🔥 TrendForge")
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
        
        # Endpoint selector with credit costs
        st.markdown("**Select endpoints to fetch:**")
        
        total_cost = 0
        for endpoint, desc in ENDPOINT_DESCRIPTIONS.items():
            cost = CREDIT_COSTS[endpoint]
            enabled = st.checkbox(
                f"{desc} (~{cost:,} credits)",
                value=True,
                key=f"endpoint_{endpoint}"
            )
            st.session_state.enabled_endpoints[endpoint] = enabled
            if enabled:
                total_cost += cost
        
        st.info(f"💰 **Estimated initial cost:** ~{total_cost:,} credits")
        
        if st.button("Connect & Go Live", use_container_width=True, disabled=not api_key):
            st.session_state.mode = "live"
            st.session_state.virlo_api_key = api_key
            st.session_state.cache = {}
            st.rerun()

# ==================== TREND HUB ====================
def show_trend_hub():
    st.title("📊 Trend Hub")
    
    data = get_data("trends")
    trend_groups = data.get("data", [])
    trends = trend_groups[0].get("trends", []) if trend_groups else []
    
    if not trends:
        st.warning("No trends available. Try refreshing.")
        return
    
    # Top stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Trends", len(trends))
    with col2:
        st.metric("Credits Used", format_number(st.session_state.credits_used))
    with col3:
        hot = sum(1 for t in trends if t.get("ranking", 99) <= 3)
        st.metric("🔥 Top Picks", hot)
    with col4:
        mode = "🔴 Live" if st.session_state.mode == "live" else "📊 Demo"
        st.metric("Mode", mode)
    
    st.divider()
    
    # Hero: Top 3 trends
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
                    
                    if st.button("View Details", key=f"hero_{i}", use_container_width=True):
                        st.toast(f"ℹ️ {name} - Check Video Vault for related content")
    
    st.divider()
    
    # All trends in 4-column grid
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
                if st.button("View Details", key=f"trend_{idx}", use_container_width=True):
                    st.toast(f"ℹ️ {name} - Check Video Vault for related content")

# ==================== HASHTAG LAB ====================
def show_hashtag_lab():
    st.title("🏷️ Hashtag Lab")
    
    # Filter controls
    search = st.text_input("Search hashtags", placeholder="Filter...")
    
    data = get_data("hashtags", limit=50, order_by="views")
    hashtags = data.get("data", [])
    
    if search:
        hashtags = [h for h in hashtags if search.lower() in h.get("hashtag", "").lower()]
    
    if not hashtags:
        st.warning("No hashtags found")
        return
    
    st.divider()
    
    # 3 Strategy Sets
    st.subheader("🎯 Hashtag Strategies")
    
    # Split hashtags into 3 sets
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
    
    # All hashtags grid - with inline copy buttons
    st.subheader("📋 All Hashtags")
    cols = st.columns(4)
    
    for idx, h in enumerate(hashtags[:20]):
        tag = h.get("hashtag", "")
        count = h.get("count", 0)
        views = h.get("total_views", 0)
        
        with cols[idx % 4]:
            with st.container(border=True):
                st.markdown(f"**{tag}**")
                
                # Stats row
                c1, c2 = st.columns(2)
                with c1:
                    st.caption(f"📊 {format_number(count)}")
                with c2:
                    st.caption(f"👁️ {format_number(views)}")
                
                # Copy button on new row
                if st.button("📋 Copy", key=f"copy_tag_{idx}", use_container_width=True):
                    copy_to_clipboard(tag)

# ==================== NICHE SCOUT ====================
def show_niche_scout():
    st.title("🎯 Niche Scout")
    
    data = get_data("niches")
    niches = data.get("data", [])
    
    if not niches:
        st.warning("No niches available")
        return
    
    # Search
    search = st.text_input("Search niches", placeholder="Type to filter...")
    
    if search:
        niches = [n for n in niches if search.lower() in n.get("label", "").lower()]
    
    st.divider()
    
    # All niches in 4-column grid
    st.subheader(f"📋 {len(niches)} Niches Available")
    cols = st.columns(4)
    
    for idx, n in enumerate(niches):
        niche_id = n.get("id", "")
        label = n.get("label", "Unknown")
        
        with cols[idx % 4]:
            with st.container(border=True):
                st.markdown(f"**{label}**")
                st.caption(f"ID: {niche_id}")
                if st.button("Explore", key=f"niche_{idx}", use_container_width=True):
                    st.toast(f"✅ Use '{niche_id}' in Video Vault filter!")

# ==================== VIDEO VAULT ====================
def show_video_vault():
    st.title("🎬 Video Vault")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        niche_data = get_data("niches")
        niches = niche_data.get("data", [])
        niche_options = ["All"] + [n.get("id", "") for n in niches]
        selected_niche = st.selectbox("Niche", niche_options)
    
    with col2:
        limit = st.slider("Videos", 5, 30, 12)
    
    niche = None if selected_niche == "All" else selected_niche
    data = get_data("videos", limit=limit, niche=niche)
    videos = data.get("data", [])
    
    if not videos:
        st.warning("No videos found")
        return
    
    st.divider()
    
    # Video grid - 4 columns
    cols = st.columns(4)
    
    for idx, v in enumerate(videos):
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
                
                # Hashtags
                if hashtags:
                    tag_str = " ".join(hashtags[:3])
                    st.caption(f"🏷️ {tag_str}")
                
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
    
    st.divider()
    
    # Insights
    st.subheader("📊 Insights")
    if videos:
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

# ==================== WEEKLY BLUEPRINT ====================
def show_weekly_blueprint():
    st.title("📋 Weekly Blueprint")
    
    st.write("Get 5 ready-to-shoot content ideas for the week.")
    
    # Setup
    col1, col2, col3 = st.columns(3)
    
    niche_data = get_data("niches")
    niches = niche_data.get("data", [])
    niche_options = [n.get("label", n.get("id", "")) for n in niches]
    
    with col1:
        niche = st.selectbox("Your Niche", niche_options[:20] if niche_options else ["General"])
    with col2:
        platform = st.selectbox("Platform", ["TikTok", "YouTube Shorts", "Instagram Reels"])
    with col3:
        tone = st.selectbox("Tone", ["Funny", "Educational", "Dramatic", "Inspirational"])
    
    if st.button("✨ Generate My Week", type="primary", use_container_width=True):
        # Reuse trends data (no extra API call)
        trends_data = get_data("trends")
        trend_groups = trends_data.get("data", [])
        trends = trend_groups[0].get("trends", []) if trend_groups else []
        
        # Generate ideas from trends
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
                    "video_idea": f"Create a {tone.lower()} video about {trend_info.get('name', 'this trend')} for {platform}",
                    "hook": f"POV: You just discovered {trend_info.get('name', 'this')}...",
                    "hashtags": ["#fyp", "#viral", f"#{trend_info.get('name', 'trend').replace(' ', '').lower()[:15]}"],
                    "difficulty": ["Easy", "Medium", "Hard"][i % 3],
                    "best_time": f"{14 + i % 4}:00 UTC"
                })
        
        st.session_state.weekly_plan = {"ideas": ideas, "niche": niche, "platform": platform}
        save_cache_to_file()
        st.rerun()
    
    st.divider()
    
    # Show plan - 2 columns for better mobile view
    plan = st.session_state.weekly_plan
    if plan:
        ideas = plan.get("ideas", [])
        
        cols = st.columns(2)
        for idx, idea in enumerate(ideas):
            with cols[idx % 2]:
                with st.container(border=True):
                    # Header with copy button
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"### {idea['day']}")
                        st.caption(idea['trend'])
                    with c2:
                        st.caption(f"⭐ {idea['difficulty']}")
                    
                    st.write(f"📹 {idea['video_idea']}")
                    st.write(f"🎬 _{idea['hook']}_")
                    
                    tag_str = " ".join(idea['hashtags'])
                    st.code(tag_str)
                    
                    st.caption(f"⏰ {idea['best_time']}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ Use", key=f"use_{idx}", use_container_width=True):
                            st.session_state.brief_prefill = idea
                            st.toast(f"✅ Go to **Brief Creator**")
                    with c2:
                        if st.button("📋 Copy", key=f"copy_idea_{idx}", use_container_width=True):
                            copy_to_clipboard(f"{idea['day']}: {idea['video_idea']}\n{tag_str}")
    else:
        st.info("👆 Set your preferences and click 'Generate My Week'")

# ==================== BRIEF CREATOR ====================
def show_brief_creator():
    st.title("📄 Brief Creator")
    st.write("Create professional one-page briefs for your team.")
    
    # Pre-fill from weekly plan if available
    prefill = st.session_state.brief_prefill
    
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Topic/Trend", value=prefill.get("trend", "") if prefill else "")
    with col2:
        niche_data = get_data("niches")
        niches = niche_data.get("data", [])
        niche_options = ["General"] + [n.get("label", "") for n in niches[:20]]
        niche = st.selectbox("Your Niche", niche_options)
    
    description = st.text_area(
        "Description",
        value=prefill.get("description", "") if prefill else "",
        placeholder="Describe the trend or idea..."
    )
    
    if st.button("✨ Generate Brief", type="primary", use_container_width=True, disabled=not topic):
        brief = {
            "trend_name": topic,
            "niche": niche,
            "prepared_date": datetime.now().strftime("%Y-%m-%d"),
            "description": description,
            "sections": {
                "why_this_trend": f"The {topic} trend is gaining momentum and presents a timely opportunity for creators in the {niche} space.",
                "what_to_create": {
                    "format": "Vertical video, 30-60 seconds",
                    "hook_copy": prefill.get("hook", f"Wait... is this really {topic}? 🤯") if prefill else f"Wait... is this really {topic}? 🤯",
                    "best_time": prefill.get("best_time", "2-4 PM UTC") if prefill else "2-4 PM UTC"
                },
                "hashtags": {
                    "safe": ["#fyp", "#viral", "#trending"],
                    "aggressive": ["#fyp", "#foryou", "#explore", "#viral"],
                    "gems": ["#newtrend", "#underrated"]
                }
            }
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
        
        sections = brief["sections"]
        
        st.markdown("**💡 Why This Trend**")
        st.write(sections["why_this_trend"])
        
        st.markdown("**🎬 What to Create**")
        wtc = sections["what_to_create"]
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Format: {wtc['format']}")
        with col2:
            st.write(f"Best time: {wtc['best_time']}")
        st.write(f"Hook: _{wtc['hook_copy']}_")
        
        st.markdown("**🏷️ Hashtag Strategy**")
        hs = sections["hashtags"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption("Safe")
            st.code(" ".join(hs["safe"]))
        with col2:
            st.caption("Aggressive")
            st.code(" ".join(hs["aggressive"]))
        with col3:
            st.caption("Hidden Gems")
            st.code(" ".join(hs["gems"]))
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            brief_text = f"""
CONTENT BRIEF: {brief['trend_name']}
Niche: {brief['niche']} | Date: {brief['prepared_date']}

WHY THIS TREND
{sections['why_this_trend']}

WHAT TO CREATE
Format: {wtc['format']}
Hook: {wtc['hook_copy']}
Best time: {wtc['best_time']}

HASHTAGS
Safe: {' '.join(hs['safe'])}
Aggressive: {' '.join(hs['aggressive'])}
Gems: {' '.join(hs['gems'])}
"""
            st.download_button(
                "📄 Download Brief (.txt)",
                brief_text,
                file_name=f"brief_{topic.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            if st.button("📋 Copy Brief", use_container_width=True):
                copy_to_clipboard(brief_text)
    else:
        st.info("Enter a topic and generate your brief")

# ==================== SETTINGS ====================
def show_settings():
    st.title("⚙️ Settings")
    
    mode = "🔴 Live" if st.session_state.mode == "live" else "📊 Demo"
    st.write(f"**Current Mode:** {mode}")
    st.write(f"**Credits Used:** {format_number(st.session_state.credits_used)}")
    
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
    # Welcome screen if no mode selected
    if not st.session_state.mode:
        show_welcome()
        return
    
    # Sidebar
    with st.sidebar:
        st.title("🔥 TrendForge")
        
        mode_label = "🔴 Live" if st.session_state.mode == "live" else "📊 Demo"
        st.caption(f"{mode_label} | {format_number(st.session_state.credits_used)} credits")
        
        st.divider()
        
        pages = ["📊 Trend Hub", "🏷️ Hashtag Lab", "🎯 Niche Scout",
             "🎬 Video Vault", "📋 Weekly Blueprint", "📄 Brief Creator", "⚙️ Settings"]
        
        page = st.radio(
            "Navigate",
            pages,
            index=st.session_state.current_page,
            label_visibility="collapsed",
            key="nav_radio"
        )
        
        st.session_state.current_page = pages.index(page)
        
        st.divider()
        
        # Data refresh section
        st.caption("💾 Data")
        refresh_options = ["All Data", "Trends", "Hashtags", "Videos", "Niches"]
        refresh_target = st.selectbox("Refresh", refresh_options, label_visibility="collapsed")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            if refresh_target == "All Data":
                st.session_state.cache = {}
            else:
                # Clear specific cache keys
                target_key = refresh_target.lower()
                keys_to_remove = [k for k in st.session_state.cache.keys() if target_key in k]
                for k in keys_to_remove:
                    del st.session_state.cache[k]
            save_cache_to_file()
            st.toast(f"✅ {refresh_target} refreshed!")
            st.rerun()
        
        st.divider()
        
        # Live mode toggle in sidebar
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
    elif page == "🏷️ Hashtag Lab":
        show_hashtag_lab()
    elif page == "🎯 Niche Scout":
        show_niche_scout()
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
