"""
TrendForge - Trend Intelligence & Content Planning

Single-page Streamlit app with sidebar navigation.
"""
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Initialize session state FIRST before any other imports that use it
if "mode" not in st.session_state:
    st.session_state.mode = None
if "virlo_api_key" not in st.session_state:
    st.session_state.virlo_api_key = None
if "credits_used" not in st.session_state:
    st.session_state.credits_used = 0
if "credit_log" not in st.session_state:
    st.session_state.credit_log = []
if "cache" not in st.session_state:
    st.session_state.cache = {}
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = {}
if "weekly_plan" not in st.session_state:
    st.session_state.weekly_plan = None
if "generated_brief" not in st.session_state:
    st.session_state.generated_brief = None
if "saved_ideas" not in st.session_state:
    st.session_state.saved_ideas = []

# Page config
st.set_page_config(
    page_title="TrendForge",
    page_icon="🔥",
    layout="wide",
)

# Data paths
DEMO_DATA_PATH = Path(__file__).parent / "data" / "demo"

def load_demo_file(filename: str) -> Dict[str, Any]:
    """Load demo JSON file"""
    filepath = DEMO_DATA_PATH / filename
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"results": 0, "data": []}

def format_number(num: int) -> str:
    """Format large numbers"""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)

def format_growth(growth: int) -> str:
    """Format growth percentage"""
    if growth > 0:
        return f"+{growth}%"
    elif growth < 0:
        return f"{growth}%"
    return "0%"

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
        if st.button("Try Demo", type="primary", use_container_width=True):
            st.session_state.mode = "demo"
            st.rerun()
    
    with col2:
        st.markdown("### 🔌 Live Mode")
        st.write("• Connect Virlo API")
        st.write("• Real-time data")
        if st.button("Connect API", use_container_width=True):
            st.session_state.mode = "setup"
            st.rerun()

def show_api_setup():
    st.title("🔌 API Setup")
    
    api_key = st.text_input("Virlo API Key", type="password", placeholder="vrl_xxx...")
    st.caption("Get your key from [virlo.ai](https://virlo.ai)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Connect", type="primary", use_container_width=True, disabled=not api_key):
            st.session_state.mode = "live"
            st.session_state.virlo_api_key = api_key
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.mode = None
            st.rerun()

# ==================== TREND HUB ====================
def show_trend_hub():
    st.title("📊 Trend Hub")
    
    data = load_demo_file("trends.json")
    trends = data.get("data", [{}])[0].get("trends", [])
    
    if not trends:
        st.warning("No trends available")
        return
    
    # Top stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Trends", len(trends))
    with col2:
        hot = len([t for t in trends if t.get("status") == "hot"])
        st.metric("Hot 🔥", hot)
    with col3:
        total_views = sum(t.get("views_24h", 0) for t in trends)
        st.metric("Views (24h)", format_number(total_views))
    with col4:
        emerging = len([t for t in trends if t.get("status") == "emerging"])
        st.metric("Emerging 🌪️", emerging)
    
    st.divider()
    
    # Trend grid - 4 columns
    st.subheader("Trending Now")
    
    cols = st.columns(4)
    for idx, trend in enumerate(trends[:12]):
        with cols[idx % 4]:
            with st.container(border=True):
                name = trend.get("trend", {}).get("name", trend.get("name", "Unknown"))
                status = trend.get("status", "stable")
                growth = trend.get("growth_percent", 0)
                views = trend.get("views_24h", 0)
                
                emoji = "🔥" if status == "hot" else "🌪️" if status == "emerging" else "📈"
                st.markdown(f"**{emoji} {name}**")
                st.caption(f"{format_growth(growth)} • {format_number(views)} views")

# ==================== HASHTAG LAB ====================
def show_hashtag_lab():
    st.title("🏷️ Hashtag Lab")
    
    data = load_demo_file("hashtags.json")
    hashtags = data.get("data", [])
    
    if not hashtags:
        st.warning("No hashtags available")
        return
    
    # Search
    search = st.text_input("Search hashtags", placeholder="Type to filter...")
    
    if search:
        hashtags = [h for h in hashtags if search.lower() in h.get("hashtag", "").lower()]
    
    st.divider()
    
    # Hashtag grid - 4 columns
    cols = st.columns(4)
    for idx, h in enumerate(hashtags[:20]):
        with cols[idx % 4]:
            with st.container(border=True):
                tag = h.get("hashtag", "")
                count = h.get("count", 0)
                views = h.get("total_views", 0)
                growth = h.get("growth_7d", 0)
                score = h.get("opportunity_score", 50)
                
                st.markdown(f"**{tag}**")
                
                c1, c2 = st.columns(2)
                with c1:
                    st.caption(f"📊 {format_number(count)}")
                with c2:
                    st.caption(f"👁️ {format_number(views)}")
                
                c1, c2 = st.columns(2)
                with c1:
                    color = "green" if growth > 0 else "red" if growth < 0 else "gray"
                    st.caption(f":{color}[{format_growth(growth)}]")
                with c2:
                    st.caption(f"⭐ {score}/100")

# ==================== NICHE SCOUT ====================
def show_niche_scout():
    st.title("🎯 Niche Scout")
    
    data = load_demo_file("niches.json")
    niches = data.get("data", [])
    
    if not niches:
        st.warning("No niches available")
        return
    
    # Categorize
    emerging = [n for n in niches if n.get("status") == "emerging"]
    stable = [n for n in niches if n.get("status") == "stable"]
    cooling = [n for n in niches if n.get("status") == "cooling"]
    
    # Emerging - 4 columns
    if emerging:
        st.subheader("🌪️ Emerging")
        cols = st.columns(4)
        for idx, n in enumerate(emerging[:8]):
            with cols[idx % 4]:
                with st.container(border=True):
                    st.markdown(f"**{n.get('label', 'Unknown')}**")
                    st.caption(f"+{n.get('growth', 0)}% growth")
    
    st.divider()
    
    # Stable - 4 columns
    if stable:
        st.subheader("📈 Stable")
        cols = st.columns(4)
        for idx, n in enumerate(stable[:12]):
            with cols[idx % 4]:
                with st.container(border=True):
                    st.markdown(f"**{n.get('label', 'Unknown')}**")
                    st.caption(f"+{n.get('growth', 0)}% growth")
    
    st.divider()
    
    # Cooling - 4 columns
    if cooling:
        st.subheader("↘️ Cooling")
        cols = st.columns(4)
        for idx, n in enumerate(cooling[:4]):
            with cols[idx % 4]:
                with st.container(border=True):
                    st.markdown(f"**{n.get('label', 'Unknown')}**")
                    st.caption(f"{n.get('growth', 0)}% growth")

# ==================== VIDEO VAULT ====================
def show_video_vault():
    st.title("🎬 Video Vault")
    
    data = load_demo_file("videos.json")
    videos = data.get("data", [])
    
    if not videos:
        st.warning("No videos available")
        return
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        platform = st.selectbox("Platform", ["All", "TikTok", "YouTube"])
    with col2:
        limit = st.slider("Show", 5, 20, 12)
    
    if platform != "All":
        videos = [v for v in videos if v.get("type", "").lower() == platform.lower()]
    
    videos = videos[:limit]
    
    st.divider()
    
    # Video grid - 4 columns
    cols = st.columns(4)
    for idx, v in enumerate(videos):
        with cols[idx % 4]:
            with st.container(border=True):
                platform = v.get("type", "Unknown").upper()
                views = v.get("views", 0)
                desc = v.get("description", "")[:60] + "..."
                duration = v.get("duration", 0)
                
                st.caption(f"📹 {platform} • {duration}s")
                st.markdown(f"**{desc}**")
                st.caption(f"👁️ {format_number(views)} views")
                
                url = v.get("url", "#")
                st.link_button("Watch →", url, use_container_width=True)

# ==================== WEEKLY BLUEPRINT ====================
def show_weekly_blueprint():
    st.title("📋 Weekly Blueprint")
    
    # Setup
    col1, col2, col3 = st.columns(3)
    with col1:
        niche = st.selectbox("Niche", ["Tech", "Entertainment", "Lifestyle", "Gaming"])
    with col2:
        platform = st.selectbox("Platform", ["TikTok", "YouTube", "Reels"])
    with col3:
        tone = st.selectbox("Tone", ["Funny", "Educational", "Dramatic"])
    
    if st.button("✨ Generate Week", type="primary", use_container_width=True):
        st.session_state.weekly_plan = load_demo_file("weekly_plan.json")
    
    st.divider()
    
    # Show plan
    plan = st.session_state.get("weekly_plan")
    if plan:
        ideas = plan.get("ideas", [])
        
        for idea in ideas:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{idea.get('day', '')}** - {idea.get('trend', '')}")
                with col2:
                    st.caption(idea.get("difficulty", ""))
                
                st.write(idea.get("video_idea", ""))
                st.caption(f"🎬 Hook: _{idea.get('hook', '')}_")
                
                tags = idea.get("hashtag_set", [])
                if isinstance(tags, list):
                    st.code(" ".join(tags))
    else:
        st.info("Click 'Generate Week' to create your content plan")

# ==================== BRIEF CREATOR ====================
def show_brief_creator():
    st.title("📄 Brief Creator")
    
    # Input
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("Topic/Trend", placeholder="Enter topic...")
    with col2:
        niche = st.selectbox("Your Niche", ["General", "Tech", "Entertainment"])
    
    desc = st.text_area("Description", placeholder="Describe the trend...", height=100)
    
    if st.button("✨ Generate Brief", type="primary", use_container_width=True, disabled=not topic):
        brief_template = load_demo_file("brief_template.json")
        brief_template["trend_name"] = topic
        brief_template["prepared_date"] = datetime.now().strftime("%Y-%m-%d")
        st.session_state.generated_brief = brief_template
    
    st.divider()
    
    # Show brief
    brief = st.session_state.get("generated_brief")
    if brief:
        st.subheader(f"🔥 {brief.get('trend_name', 'Topic')}")
        st.caption(f"Prepared: {brief.get('prepared_date', '')}")
        
        sections = brief.get("sections", {})
        
        if "why_this_trend" in sections:
            st.markdown("**💡 Why This Trend**")
            st.write(sections["why_this_trend"])
        
        if "what_to_create" in sections:
            st.markdown("**🎬 What to Create**")
            wtc = sections["what_to_create"]
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"Format: {wtc.get('format', '')}")
            with col2:
                st.write(f"Time: {wtc.get('best_posting_time', '')}")
            st.write(f"Hook: _{wtc.get('hook_copy', '')}_")
        
        if "hashtag_strategy" in sections:
            st.markdown("**🏷️ Hashtag Strategy**")
            hs = sections["hashtag_strategy"]
            col1, col2, col3 = st.columns(3)
            with col1:
                st.caption("Safe")
                tags = hs.get("safe_set", {})
                if isinstance(tags, dict):
                    tags = tags.get("tags", [])
                st.code(" ".join(tags) if tags else "")
            with col2:
                st.caption("Aggressive")
                tags = hs.get("aggressive_set", {})
                if isinstance(tags, dict):
                    tags = tags.get("tags", [])
                st.code(" ".join(tags) if tags else "")
            with col3:
                st.caption("Hidden Gems")
                tags = hs.get("hidden_gems", {})
                if isinstance(tags, dict):
                    tags = tags.get("tags", [])
                st.code(" ".join(tags) if tags else "")
    else:
        st.info("Enter a topic and click 'Generate Brief'")

# ==================== SETTINGS ====================
def show_settings():
    st.title("⚙️ Settings")
    
    st.subheader("Mode")
    mode = "Demo" if st.session_state.mode == "demo" else "Live"
    st.write(f"Current: **{mode}**")
    
    if st.button("Switch to Demo", disabled=st.session_state.mode == "demo"):
        st.session_state.mode = "demo"
        st.rerun()
    
    st.divider()
    
    st.subheader("Saved Ideas")
    saved = st.session_state.get("saved_ideas", [])
    if saved:
        st.write(f"{len(saved)} ideas saved")
        if st.button("Clear All"):
            st.session_state.saved_ideas = []
            st.rerun()
    else:
        st.write("No saved ideas")
    
    st.divider()
    
    if st.button("🔄 Reset App", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==================== MAIN APP ====================
def main():
    # Check mode
    if st.session_state.mode is None:
        show_welcome()
        return
    
    if st.session_state.mode == "setup":
        show_api_setup()
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🔥 TrendForge")
        
        mode_label = "📊 Demo" if st.session_state.mode == "demo" else "🔴 Live"
        st.caption(mode_label)
        
        st.divider()
        
        page = st.radio(
            "Navigate",
            ["📊 Trend Hub", "🏷️ Hashtag Lab", "🎯 Niche Scout", 
             "🎬 Video Vault", "📋 Weekly Blueprint", "📄 Brief Creator", "⚙️ Settings"],
            label_visibility="collapsed"
        )
    
    # Show selected page
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
