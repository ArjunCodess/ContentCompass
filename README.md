<h2 align="center">ContentCompass - AI-Powered Trend Intelligence & Content Planning Platform</h2>

<p align="center">
  AI-powered trend intelligence and content planning tool for creators — discover trending content, optimize hashtag strategies, and generate actionable briefs using Gemini AI.
</p>

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Deployment](#deployment)
- [Usage](#usage)
- [Built Using](#built_using)
- [Documentation](./docs/)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>

ContentCompass is a creator-focused trend intelligence and content planning tool built with Python + Streamlit. It features two modes: **Demo Mode** (uses locally-generated JSON sample data, no API calls) and **Live Mode** (uses Virlo API with BYOK authentication).

The app helps creators discover trending content, optimize hashtag strategies, and generate actionable content briefs using Gemini AI. Users can explore trend hubs, analyze hashtag performance, scout content niches, browse top-performing videos, generate weekly content plans, and create professional briefs for their teams.

Key features include:
- **Trend Hub**: Discover hottest, most stable, and emerging trends
- **Hashtag Lab**: Generate strategic hashtag combinations (Safe, Aggressive, Hidden Gems)
- **Video Vault**: Browse top-performing content with embedded players
- **Weekly Blueprint**: AI-generated 5-day content plans
- **Brief Creator**: Professional content briefs with export functionality
- **Credit Tracking**: Monitor API usage in Live Mode

The platform emphasizes data-driven insights and creator-friendly workflows to streamline content creation and planning.

## 🏁 Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

- **Python** (v3.8 or higher)
- **pip** package manager
- **Virlo API Key** (optional, for Live Mode features)
- **Gemini API Key** (optional, for AI content generation)

### Installing

1. **Clone the repository**

   ```bash
   git clone https://github.com/contentcompass/app.git
   cd contentcompass
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional)**

   Create a `.env` file for API access:

   ```env
   VIRLO_API_KEY=your_virlo_api_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

5. **Start the application**

   ```bash
   streamlit run app.py
   ```

The application will be available at `http://localhost:8501`.

### Demo Data

The app comes with pre-generated demo data in `data/demo/` for instant testing. To generate fresh demo data from real APIs, run:

```bash
python generate_demo_data.py
```

## 🔧 Running the tests <a name = "tests"></a>

Currently, the project uses manual testing. Automated testing setup is planned for future releases.

### Manual Testing

1. **Demo Mode Testing**

   - Run `streamlit run app.py` and select "Try Demo"
   - Test all screens: Trend Hub, Video Vault, Weekly Blueprint, Brief Creator
   - Verify demo data loads correctly from `data/demo/` JSON files

2. **Live Mode Testing** (requires API keys)

   - Set up `.env` file with `VIRLO_API_KEY` and `GEMINI_API_KEY`
   - Test API connections and credit tracking
   - Verify real data fetching and AI content generation

3. **Feature Testing**

   - **Mode switching**: Demo ↔ Live mode transitions
   - **Data refresh**: Cache clearing and fresh API calls
   - **Content generation**: Weekly plans and briefs with Gemini AI
   - **Export functionality**: Text downloads for plans and briefs

4. **Data Generation Testing**

   - Run `python generate_demo_data.py` with valid Virlo API key
   - Verify all demo JSON files are created with real data

### Code Quality Checks

```bash
# Basic Python syntax checking
python -m py_compile app.py
python -m py_compile generate_demo_data.py
```

## 🎈 Usage <a name="usage"></a>

### Core Features

1. **Mode Selection**

   - **Demo Mode**: Instant access with pre-generated sample data (no API required)
   - **Live Mode**: Real-time trend data via Virlo API with credit tracking

2. **Trend Hub**

   - Discover trending topics and hashtag strategies
   - View top trends and strategic hashtag combinations
   - Three hashtag sets: Safe Play, Aggressive Growth, Hidden Gems

3. **Video Vault**

   - Browse top-performing videos across platforms
   - Embedded video players for YouTube and TikTok
   - Filter by platform and view video insights
   - Copy hashtag strategies from successful content

4. **Weekly Blueprint**

   - AI-generated 5-day content plans using Gemini
   - Customizable by niche, platform, and tone
   - Export plans as text files
   - Use ideas to jump to Brief Creator

5. **Brief Creator**

   - Generate professional content briefs using Gemini AI
   - Include trend analysis, creative angles, and hashtag strategies
   - Export briefs as text files or copy to clipboard

6. **Settings**

   - Switch between Demo and Live modes
   - API key management
   - Data cache management and app reset

### Getting Started Workflow

1. Launch the app and choose Demo Mode for instant access
2. Explore Trend Hub to discover trends and hashtag strategies
3. Browse Video Vault to see top-performing content examples
4. Generate a Weekly Blueprint for content planning
5. Create professional briefs with the Brief Creator
6. Switch to Live Mode with API keys for real-time data

For detailed guides, see the [documentation](./docs/) folder.

## 🚀 Deployment <a name = "deployment"></a>

The project is a Streamlit application that can be deployed on platforms supporting Python and Streamlit.

### Production Deployment

1. **Streamlit Cloud Deployment** (Recommended)

   - Connect your GitHub repository to [Streamlit Cloud](https://share.streamlit.io/)
   - Configure secrets for API keys in the Streamlit dashboard:
     - `VIRLO_API_KEY`
     - `GEMINI_API_KEY`
   - Deploy automatically on pushes to main branch

2. **Other Platform Options**

   - **Heroku**: Deploy as a Python web app
   - **Railway**: Python application deployment
   - **Render**: Web service deployment
   - **AWS/GCP/Azure**: Cloud platform deployment with Python support

### Environment Variables

Create a `.env` file in your project root:

```env
VIRLO_API_KEY=your_virlo_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### Local Development

For local development with API access, ensure you have the `.env` file with valid API keys.

### Monitoring and Analytics

- Built-in credit tracking for Virlo API usage
- Session-based analytics for user engagement
- Error logging and graceful failure handling

## ⛏️ Built Using <a name = "built_using"></a>

### Core Framework

- [Python](https://python.org/) - Programming Language
- [Streamlit](https://streamlit.io/) - Web App Framework

### AI & External APIs

- [Google Gemini AI](https://ai.google.dev/) - Content Generation & Brief Writing
- [Virlo API](https://virlo.com/) - Trend Intelligence & Social Data

### Data & Storage

- [JSON](https://www.json.org/) - Demo Data Storage
- [Requests](https://requests.readthedocs.io/) - HTTP Client for API Calls

### Development & Deployment

- [Git](https://git-scm.com/) - Version Control
- [pip](https://pip.pypa.io/) - Package Management

### Additional Libraries

- [python-dotenv](https://pypi.org/project/python-dotenv/) - Environment Variables

## ✍️ Authors <a name = "authors"></a>

- **ArjunCodess** - Project development and maintenance

_Note: This project embraces open-source values and transparency. We love open source because it keeps us accountable, fosters collaboration, and drives innovation. For collaboration opportunities or questions, please reach out through the appropriate channels._

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- **Google AI** for providing the Gemini API that powers content generation
- **Virlo** for the trend intelligence API that enables real-time data
- **Streamlit** for the excellent web app framework
- **Python Community** for the rich ecosystem of libraries
- **Open Source Community** for the countless libraries and tools that make modern development possible

---

<div align="center">

**ContentCompass** - Your AI-powered guide to trending content

_Built with ❤️ for creators and content strategists_

</div>
