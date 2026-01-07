# ContentCompass: Complete Product Specification for AI Code Agent

## Executive Summary

**ContentCompass** is a creator-focused trend intelligence and content planning tool built with Python + Streamlit. It features two modes:
- **Demo Mode**: Uses locally-generated JSON sample data (no API calls)
- **Live Mode**: Uses Virlo API with BYOK authentication (user provides API key)

The app helps creators discover trending content, optimize hashtag strategies, and generate actionable content briefs using Gemini AI.

**Tech Stack:**
- Backend: Python + Streamlit
- AI: Gemini 3-Flash (content generation, brief writing)
- Data: Virlo API (Live Mode), Local JSON snapshots (Demo Mode)

---

## Core Modes

### Mode 1: Demo Mode
- Uses pre-generated JSON sample data (bundled locally)
- Zero API calls
- Fully interactive UI
- Clear labeling: "📊 Demo Data – Sample snapshot from [date]"
- No API key required
- Perfect for onboarding

### Mode 2: Live Mode
- Requires Virlo API key (user provides via selector)
- Fetches data on demand
- Shows "🔴 Live Data – Last Updated: [timestamp]"
- Tracks total API credits consumed in session
- Displays credit cost before each API call

---

## Startup Flow

### Step 1: Mode Selection (First Screen)

On app launch, user sees two buttons:

```
┌─────────────────────────────────────────┐
│         Welcome to ContentCompass            │
│                                          │
│  [📊 Try Demo]    [🔌 Connect Live API] │
└─────────────────────────────────────────┘
```

**Button 1: "Try Demo"**
- Loads demo data instantly from JSON files
- No setup required
- Shows all features with sample data

**Button 2: "Connect Live API"**
- Opens API key setup screen (see Step 2)

### Step 2: API Key Setup (Live Mode Only)

**Screen Layout:**

```
┌──────────────────────────────────────────────┐
│  Set Up Your Virlo API                       │
│                                              │
│  Select which endpoints you'll use:          │
│  ☐ Trends (1,000 credits/call)              │
│  ☐ Hashtags (10 credits/call)               │
│  ☐ Videos (100 credits/call)                │
│  ☐ Niches (50 credits/call)                 │
│                                              │
│  📊 Total cost estimate: ~2,500 credits     │
│  (You control when to refresh data)          │
│                                              │
│  Paste your Virlo API Key:                  │
│  [••••••••••••••••••] (masked input)        │
│                                              │
│              [Connect]  [Cancel]            │
└──────────────────────────────────────────────┘
```

**On Connect:**
- Validate API key format
- Store in session state (never log it)
- Initialize credit counter in session: `credits_used = 0`
- Switch UI to Live Mode
- Load initial data (don't auto-fetch; let user click "Refresh" first)

---

## Main Screens & Features

### Screen 1: Trend Hub – "What's Hot Right Now"

**Purpose:** In 30 seconds, see what's trending and get a clear next action.

**Layout:**

```
Header Bar:
┌────────────────────────────────────────┐
│ 📊 Demo Data                           │
│ (or: 🔴 Live – Updated 5 min ago)      │
│                        [🔄 Refresh Data]
└────────────────────────────────────────┘

Main Content:
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ 🔥 Hottest     │  │ 📈 Most Stable │  │ 🌪️ Emerging    │
│ #AIReaction    │  │ #DanceTok      │  │ #TechSatire    │
│ ↗ +234%        │  │ → Stable       │  │ ↗ +156%        │
│ 2.3M views     │  │ 5.6M views     │  │ 234K views     │
│ TikTok         │  │ Mixed          │  │ YouTube        │
│                │  │                │  │                │
│[Explore Trend] │  │[Get Hashtags] │  │[Check My Brand]│
└────────────────┘  └────────────────┘  └────────────────┘

Below:
📊 Total Trends: 45 | 🔥 Hottest Platform: TikTok (67%)
```

**Data Source:**
- **Live Mode:** Virlo `/trends` endpoint [1 API call, ~1,000 credits]
- **Demo Mode:** `data/demo/trends.json`

**CTAs:**
- **"Explore Trend"** → Navigate to Hashtag Lab with trend pre-filled
- **"Get Hashtags"** → Same as above
- **"Check My Brand"** → Quick brand fit checker (simple yes/no)

---

### Screen 2: Hashtag Lab – "Find Your Tag Strategy"

**Purpose:** Turn a trend into 3 concrete, copy-paste hashtag combos.

**Layout:**

```
Search Section:
┌──────────────────────────────────────┐
│ Trend or Hashtag: [_____________]    │
│ Platform: [All ▼]                    │
│                       [Search] [Clear]
└──────────────────────────────────────┘

Results Section (if data found):

Hashtag Stats:
• Total posts: 45K
• Views (24h): 2.3M
• Trend: ↗ +234% (last 7 days)
• Opportunity Score: 87/100 🟢 Excellent

Three Hashtag Combos:

┌──────────────────────────────┐
│ Set A: Safe Play             │
│ #DanceTok #DanceChallenge    │
│ #NewDance #ViralDance        │
│                              │
│ "Mid competition, stable"    │
│                    [📋 Copy]  │
└──────────────────────────────┘

┌──────────────────────────────┐
│ Set B: Aggressive Growth     │
│ #DanceTok #ViralDance        │
│ #FYP #ForYou                 │
│                              │
│ "High reach, competitive"    │
│                    [📋 Copy]  │
└──────────────────────────────┘

┌──────────────────────────────┐
│ Set C: Hidden Gems           │
│ #MicroDance ↗ #DanceAI ↗     │
│ #EarlyTrend                  │
│                              │
│ "Low comp, rising fast"      │
│                    [📋 Copy]  │
└──────────────────────────────┘

Top Videos Using This Hashtag:

[Video 1: 245K views]  [Video 2: 189K]  [Video 3: 156K]
Platform: TikTok       YouTube           TikTok
Hashtags: See more...  [See more...]     [See more...]
```

**Data Source:**
- **Live Mode:**
  - Virlo `/hashtags?hashtag=X` [~10 credits]
  - Virlo `/videos?hashtag=X` [~100 credits]
  - Total: ~110 credits per search
- **Demo Mode:** `data/demo/hashtags.json`

**CTAs:**
- **"Copy"** on any hashtag set → Copy to clipboard, show toast "Copied!"
- **"See more videos"** → Expand to show 5–10 videos (if already fetched)
- **"Copy hashtags from video"** → Copy specific video's hashtag combo

---

### Screen 3: Niche Scout – "Pick Your Lane"

**Purpose:** Help creator choose which content category to focus on.

**Layout:**

```
┌─────────────────────────────────────┐
│ Emerging Niches (Fast Growing)      │
├─────────────────────────────────────┤
│ ↗ AI + Creativity                   │
│   +234% growth | 45K posts          │
│   [Explore Hashtags in This Niche]  │
│                                     │
│ ↗ Tech Satire                       │
│   +189% growth | 23K posts          │
│   [Explore Hashtags in This Niche]  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Stable Niches (Reliable)            │
├─────────────────────────────────────┤
│ → Dance Trends                      │
│   Stable | 2.3M posts              │
│   [Explore Hashtags in This Niche]  │
│                                     │
│ → Comedy Sketches                   │
│   Stable | 1.8M posts              │
│   [Explore Hashtags in This Niche]  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ Cooling Niches (Declining)          │
├─────────────────────────────────────┤
│ ↘ TikTok Sounds 2024                │
│   -45% decline | archive only       │
│   [View Anyway]                     │
└─────────────────────────────────────┘
```

**Data Source:**
- **Live Mode:** Virlo `/niches` endpoint [~50 credits]
- **Demo Mode:** `data/demo/niches.json`

**CTAs:**
- **"Explore Hashtags in This Niche"** → Go to Hashtag Lab with niche pre-selected as filter
- **"View Anyway"** → Load cooling niche hashtags

---

### Screen 4: Video Vault – "See What's Winning"

**Purpose:** Show concrete examples of top-performing content.

**Layout:**

```
Filters:
Platform: [All ▼]  Niche: [All ▼]

┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│              │  │              │  │              │
│   [Video 1]  │  │   [Video 2]  │  │   [Video 3]  │
│              │  │              │  │              │
│ 245K views   │  │ 189K views   │  │ 156K views   │
│ TikTok       │  │ YouTube      │  │ TikTok       │
│ #Dance...    │  │ #Tech...     │  │ #Comedy...   │
│ [Expand]     │  │ [Expand]     │  │ [Expand]     │
└──────────────┘  └──────────────┘  └──────────────┘

On Expand (Modal):
┌──────────────────────────────────┐
│ Video Player (Embedded)          │
│                                  │
│ 245K views | TikTok              │
│ Posted: 2 days ago               │
│                                  │
│ Hashtags used:                   │
│ #DanceTok #ViralDance #FYP       │
│ [Copy These Hashtags]            │
│                                  │
│ Insights:                        │
│ • Video length: 45 seconds       │
│ • Posted at: 2 PM UTC            │
│ • Likely hook: First 3 sec       │
│                                  │
│ [Go to Hashtag Lab] [Close]      │
└──────────────────────────────────┘

Below Videos Grid:

Insights from Top 10 Videos:
• Common length: 30–90 seconds
• Peak posting time: 2–4 PM UTC
• Top hashtags used: #FYP (8/10), #DanceTok (7/10), #Viral (6/10)
```

**Data Source:**
- **Live Mode:** Virlo `/videos` endpoint [~100 credits]
- **Demo Mode:** `data/demo/videos.json`

**Video Embedding:**
- **YouTube:** Embed iframe with video ID
- **TikTok:** Embed iframe or link to video
- **Fallback:** Show thumbnail + clickable link if embed unavailable

**CTAs:**
- **"Expand"** → Open modal with full video player and details
- **"Copy These Hashtags"** → Copy hashtag combo to clipboard
- **"Go to Hashtag Lab"** → Navigate with these hashtags pre-filled

---

### Screen 5: Weekly Blueprint – "Your 7-Day Content Plan"

**Purpose:** Generate 5 ready-to-shoot daily content ideas using AI.

**Trigger:**
- Dedicated nav item: "📋 Weekly Ideas"
- Or: CTA from Trend Hub

**Layout:**

```
Setup (First Time):
Your Niche: [AI & Creativity ▼]
Primary Platform: [TikTok ▼]
Content Tone: [Funny ▼]

[Generate My Week]

Generated Plan:

┌─────────────────────────────────┐
│ MONDAY                          │
│ Trend: #AIReaction ↗ +234%      │
│                                 │
│ 📹 Idea:                        │
│ React to AI's funniest fails,   │
│ add your confused reaction      │
│                                 │
│ 🎬 Hook:                        │
│ "Wait... is that actually AI?"  │
│                                 │
│ #️⃣ Hashtags: [Set C: Hidden Gem]│
│ #AIFails #Comedy #TechSatire    │
│                                 │
│ ⏰ Best Time: 2 PM UTC          │
│ ⭐ Difficulty: Easy             │
│                                 │
│ [Use This Idea] [Save]          │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ TUESDAY                         │
│ [Similar structure]             │
└─────────────────────────────────┘

[Wed, Thu, Fri follow same pattern]

[Export as PDF] [Regenerate Week]
```

**AI Prompt (Gemini 3-Flash):**

```
You are a social media content strategist. Given trending topics, generate 
5 daily content ideas (Monday–Friday) for a creator.

Trend data:
- Top trends (names, growth %, views)
- Creator's niche: [niche]
- Platform: [platform]
- Content tone: [tone]

For each day, generate:
{
  "day": "Monday",
  "trend": "trend name",
  "growth": "+234%",
  "video_idea": "One sentence concept",
  "hook": "First 3 second copy",
  "hashtag_set": "3-4 hashtags (type: Safe/Gem/Aggressive)",
  "posting_time": "HH:MM UTC",
  "difficulty": "Easy/Medium/Hard"
}

Return as JSON array with 5 objects.
```

**Data Source:**
- **Live Mode:** Data already fetched from `/trends` in Trend Hub screen (reuse)
- **AI:** Gemini 3-Flash (free, included in app cost estimate)
- **Demo Mode:** `data/demo/weekly_plan.json`

**CTAs:**
- **"Use This Idea"** → Navigate to Brief Creator with this day's data pre-filled
- **"Save"** → Add to user's saved collection
- **"Export as PDF"** → Download printable weekly plan
- **"Regenerate Week"** → Fetch fresh trends, generate new ideas

---

### Screen 6: Brief Creator – "Share with Your Team"

**Purpose:** Generate a professional, one-page brief for editors, clients, or team members.

**Trigger:**
- Dedicated nav item: "📄 Create Brief"
- Or: CTA from Weekly Ideas ("Use This Idea")
- Or: CTA from Hashtag Lab ("Generate Brief")

**Layout:**

```
Step 1: Select Source

○ Use a trend from Trend Hub
○ Use a hashtag from Hashtag Lab
○ Use an idea from Weekly Blueprint

[Next]

Step 2: Brief Preview

┌────────────────────────────────┐
│ 🔥 TREND BRIEF                 │
│ #AIReaction                    │
│                                │
│ Status: Early Window           │
│ Prepared: [Date] | By: [Name]  │
├────────────────────────────────┤
│ THE OPPORTUNITY                │
│ Growth: ↗ +234% (24h)          │
│ Views: 2.3M (24h)              │
│ Platforms: Hot on TikTok       │
│                                │
│ Why: Creators are craving      │
│ AI reaction content. This      │
│ trend is exploding but still   │
│ low competition on YouTube.    │
├────────────────────────────────┤
│ WHAT TO CREATE                 │
│ Format: Vertical, 30–90 sec    │
│ Angle: Reaction + your twist   │
│                                │
│ Top Example Videos:            │
│ 1. [Video Embed] 245K views    │
│ 2. [Video Embed] 189K views    │
│ 3. [Video Embed] 156K views    │
│                                │
│ Hook: "Wait... is that AI?"    │
│ Typical Length: 45 seconds     │
│ Best Posting Time: 2–4 PM UTC  │
├────────────────────────────────┤
│ HASHTAG STRATEGY               │
│ Safe: #AI #Reaction #Tech      │
│ [Copy]                         │
│                                │
│ Hidden Gem: #AIFails #Comedy   │
│ [Copy]                         │
├────────────────────────────────┤
│ WHEN TO POST                   │
│ Days: Tue–Thu                  │
│ Times: 2–4 PM UTC              │
│ Why: Mid-week momentum peaks   │
├────────────────────────────────┤
│ PLATFORM NOTES                 │
│ TikTok: 🔥 Hottest (2–3x reach)│
│ YouTube: 📈 Growing            │
│ Reels: → Stable (brand fit)    │
└────────────────────────────────┘

[Copy to Clipboard] [Export PDF] [Share Link] [Customize]
```

**AI Prompt (Gemini 3-Flash):**

```
You are a social media strategist creating a brief for a content creator.
Generate a professional, concise brief about this trend.

Trend: [name]
Growth: [%]
Views (24h): [number]
Platforms: [list]
Top video examples: [titles, views]
User's niche: [niche]

Generate JSON with sections:
{
  "why_this_trend": "Why this trend matters (1–2 sentences)",
  "creative_angle": "Specific creative angle based on top videos",
  "hook_copy": "First 3–5 seconds of video",
  "platform_recommendation": "Which platform(s) to prioritize",
  "hashtag_strategy": "Which hashtag sets to use and why"
}

Be concise, actionable, and ready-to-share.
```

**Data Source:**
- **Live Mode:** Data already fetched in previous screens (reuse Trend Hub, Hashtag Lab, Video Vault data)
- **AI:** Gemini 3-Flash (free)
- **Demo Mode:** `data/demo/brief_template.json`

**Output Formats:**
- **Copy to Clipboard:** Markdown-formatted text
- **Export PDF:** Printable brief
- **Share Link:** One-time shareable URL (optional, basic implementation)

**CTAs:**
- **"Copy to Clipboard"** → Copy brief text
- **"Export PDF"** → Download brief
- **"Share Link"** → Generate shareable link
- **"Customize"** → Edit any section before sharing
- **"Create Another Brief"** → Back to source selection

---

## Navigation Structure

```
ContentCompass
├── 📊 Trend Hub (What's Hot Right Now)
├── 🏷️ Hashtag Lab (Find Your Tag Strategy)
├── 🎯 Niche Scout (Pick Your Lane)
├── 🎬 Video Vault (See What's Winning)
├── 📋 Weekly Ideas (Your 7-Day Content Plan)
├── 📄 Brief Creator (Share with Your Team)
├── ⚙️ Settings
│   ├── Switch: Demo vs Live Mode
│   ├── API Key Management
│   └── Saved Collections
└── 💳 Credits Display (Live mode only)
```

---

## API Call Optimization

### Minimize API Calls

**One-time fetches per session:**

| Screen | Endpoint | Credits | When |
|--------|----------|---------|------|
| Trend Hub | `/trends` | 1,000 | User clicks "Refresh" on Trend Hub |
| Hashtag Lab | `/hashtags`, `/videos` | 110 | Per unique search (cached by hashtag name) |
| Niche Scout | `/niches` | 50 | User clicks "Refresh" on Niche Scout |
| Video Vault | `/videos` | 100 | User clicks "Refresh" on Video Vault |
| Weekly Ideas | (reuse `/trends` from Trend Hub) + Gemini | 0 | Uses existing trend data + free AI |
| Brief Creator | (reuse existing data) + Gemini | 0 | Uses existing trend/hashtag data + free AI |

**Total estimated credits per full session:** ~2,500 credits (if all screens refreshed once)

---

## Credit Display

**Location:** Bottom right corner of app (always visible)

**Display:**
```
💳 Session Credits Used: 2,260 / Unlimited
(or show against monthly/account limit if applicable)
```

**Before Each API Call:**
- Show modal: "This will cost ~[X] credits. Continue?"
- Option to cancel

**On API Call Completion:**
- Increment counter immediately
- Update display

**Tooltip on Credit Counter:**
```
Trend Hub fetch: 1,000 cr
Hashtag search (1): 110 cr
Videos fetch: 100 cr
Niches fetch: 50 cr
───────────────────
Total: 1,260 cr
```

---

## Gemini 3-Flash Integration

**Model:** `gemini-3-flash`  
**Cost:** Free (included in Gemini API quotas)

**Use Cases:**
1. **Weekly Ideas Generation**
   - Input: Top trends + niche + platform + tone
   - Output: 5 daily content ideas (JSON)

2. **Brief Creator**
   - Input: Trend + hashtag + video examples
   - Output: Professional brief sections (JSON)

**Implementation:**
- Call Gemini synchronously (no caching needed, responses are immediate)
- Parse JSON response
- Display formatted output

**Example Gemini Call:**
```python
import google.generativeai as genai

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-3-flash')

response = model.generate_content(prompt)
parsed_json = json.loads(response.text)
```

---

## Demo Data Files

User will generate these locally using a data generation script.

**File Structure:**
```
data/demo/
├── trends.json              # Top 10 trends
├── hashtags.json            # 50+ hashtags with analytics
├── videos.json              # 20 top videos
├── niches.json              # 10–15 niches
├── weekly_plan.json         # Pre-generated 5-day plan
└── brief_template.json      # Sample brief
```

**Example `trends.json`:**
```json
{
  "trends": [
    {
      "name": "#AIReaction",
      "growth_percent": 234,
      "views_24h": 2300000,
      "posts": 45000,
      "platform": "TikTok",
      "status": "emerging"
    },
    {
      "name": "#DanceTok",
      "growth_percent": 12,
      "views_24h": 5600000,
      "posts": 2300000,
      "platform": "Mixed",
      "status": "stable"
    },
    {
      "name": "#TechSatire",
      "growth_percent": 156,
      "views_24h": 234000,
      "posts": 23000,
      "platform": "YouTube",
      "status": "emerging"
    }
  ]
}
```

**Example `hashtags.json`:**
```json
{
  "hashtags": [
    {
      "name": "#AIReaction",
      "posts": 45000,
      "views_24h": 2300000,
      "growth_7d": 234,
      "opportunity_score": 87,
      "safe_set": ["#AI", "#Reaction", "#Tech"],
      "aggressive_set": ["#AI", "#Viral", "#FYP"],
      "gem_set": ["#AIComedy", "#EarlyTrend"],
      "platforms": ["TikTok", "YouTube", "Reels"]
    }
  ]
}
```

**Example `videos.json`:**
```json
{
  "videos": [
    {
      "id": "video_001",
      "platform": "TikTok",
      "views": 245000,
      "hashtags": ["#AI", "#Reaction", "#Comedy"],
      "length_seconds": 45,
      "video_url": "https://www.tiktok.com/@user/video/...",
      "thumbnail_url": "https://example.com/thumbnail.jpg"
    }
  ]
}
```

---

## Video Embedding

**Supported Platforms:**
- YouTube: Embed iframe with video ID
- TikTok: Embed iframe or redirect to TikTok
- Instagram Reels: Link to Reels

**YouTube Embed:**
```html
<iframe width="100%" height="315" src="https://www.youtube.com/embed/[VIDEO_ID]" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
```

**TikTok Embed:**
```html
<blockquote class="tiktok-embed" cite="[VIDEO_URL]" data-video-id="[VIDEO_ID]">
  <section></section>
</blockquote>
<script async src="https://www.tiktok.com/embed.js"></script>
```

**In Streamlit:**
```python
st.markdown(embed_html, unsafe_allow_html=True)
```

---

## Removed Features

❌ **Platform Split View** – Reduces complexity and API calls. Platform info embedded in other screens.

---

## High-Level Implementation Plan

### Phase 1: Foundation (Days 1–2)
- [ ] Streamlit app scaffold
- [ ] Mode selector (Demo vs Live)
- [ ] API key setup with endpoint selector + credit cost display
- [ ] Load demo JSON files

### Phase 2: Core Screens (Days 3–5)
- [ ] Trend Hub (Trend Snapshot)
- [ ] Hashtag Lab (Tag Strategy Lab)
- [ ] Niche Scout (Category Deep Dive)
- [ ] Video Vault (What's Winning)

### Phase 3: AI & Advanced Features (Days 6–7)
- [ ] Gemini 3-Flash integration
- [ ] Weekly Ideas (7-Day Content Plan)
- [ ] Brief Creator (Professional Briefs)

### Phase 4: Polish & Deployment (Days 8–9)
- [ ] Credit counter + display
- [ ] Video embedding (YouTube/TikTok)
- [ ] Collections/saved items
- [ ] Responsive design
- [ ] Error handling
- [ ] Testing

---

## Error Handling

**API Failures:**
- Show banner: "Live data unavailable. Showing cached data from [time]."
- Allow user to retry or switch to Demo mode

**Invalid API Key:**
- Show: "API key invalid. Check format and try again."

**No Data Found:**
- Show: "No results for '[search term]'. Try another trend or hashtag."

**Credit Limit Reached:**
- Show: "You've reached your credit limit. Check back tomorrow or upgrade."

---

## Design & UX Guidelines

**Visual Hierarchy:**
1. Hero cards/trends (immediate action)
2. Detailed stats (context)
3. CTAs (next step)

**Colors:**
- 🔥 Red/Orange: Hot, trending, urgent action
- 📈 Green: Stable, growing, safe
- 🌪️ Purple: Emerging, interesting, experimental
- ↘ Gray: Declining, archive-only

**Mobile-First:**
- All cards responsive
- Embeds resize correctly
- Copy buttons always accessible
- Navigation sticky/collapsible

**Copy Tone:**
- Casual, creator-friendly
- Action-oriented ("Explore", "Copy", "Use")
- Clear credit cost messaging

---

## Checklist for Code Agent

**Before Starting:**
- [ ] Understand all 6 screens and their data sources
- [ ] Know which endpoints are called in Live mode
- [ ] Review demo data file structures
- [ ] Understand Gemini API integration

**During Development:**
- [ ] Track total API calls (target: ~2,500 for full session)
- [ ] Test demo mode with local JSON
- [ ] Test all CTAs and navigation flows
- [ ] Test video embedding for YouTube/TikTok
- [ ] Display credit counter accurately

**Before Delivery:**
- [ ] All 6 screens fully functional
- [ ] Demo mode works without API key
- [ ] Gemini integration for ideas + briefs working
- [ ] Credit counter displays total
- [ ] Video embeds render correctly
- [ ] Error handling graceful
- [ ] Mobile-responsive design

---

## Final Notes

1. **User controls refresh:** No automatic API calls; user clicks "Refresh Data"
2. **Minimize API calls:** Reuse fetched data across screens (max ~2,500 credits per session)
3. **Free AI:** Gemini 3-Flash included; no separate cost for ideas/briefs
4. **Clear credit messaging:** Show cost before each API call, total at bottom
5. **Demo first:** Users should see fully functional app with demo data before adding API key
6. **Video-first UX:** Embeds, not links; inline in cards, not modal-only
7. **Mobile-ready:** All screens work on mobile
9. **Creator-friendly language:** "Copy", "Use", "Explore" – action verbs

---

**Ready for AI code agent. Build and ship!**
