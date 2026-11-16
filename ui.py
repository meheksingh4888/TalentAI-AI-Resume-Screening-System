
import streamlit as st


# ==========================================
# TALENTAI PREMIUM DESIGN SYSTEM
# ==========================================

def apply_premium_theme():

    st.html("""
    <style>

    /* GLOBAL APPLICATION */

    .stApp {
        background:
            radial-gradient(ellipse at 5% 0%, rgba(124,58,237,0.16), transparent 32%),
            radial-gradient(ellipse at 95% 5%, rgba(59,130,246,0.10), transparent 30%),
            #080B16;
        color: #F8FAFC;
    }

    .block-container {
        max-width: 1500px;
        padding: 2rem 2.5rem 4rem;
    }

    /* TYPOGRAPHY */

    h1, h2, h3, h4 {
        color: #F8FAFC !important;
        font-weight: 750 !important;
        letter-spacing: -0.6px;
    }

    p, label, .stMarkdown {
        color: #CBD5E1;
    }

    .hero-eyebrow {
        color: #A78BFA;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2.5px;
        margin-bottom: 12px;
    }

    .hero-title {
        font-size: clamp(32px, 4vw, 48px);
        font-weight: 850;
        letter-spacing: -1.8px;
        background: linear-gradient(100deg, #FFFFFF, #C4B5FD 48%, #818CF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.15;
    }

    .hero-subtitle {
        color: #94A3B8;
        font-size: 14px;
        line-height: 1.8;
        margin-top: 12px;
        max-width: 650px;
    }

    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111426, #0B0E1B);
        border-right: 1px solid rgba(167,139,250,0.16);
    }

    [data-testid="stSidebar"] > div {
        padding-top: 1.2rem;
    }

    [data-testid="stSidebar"] p {
        color: #AAB4CC;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(167,139,250,0.15);
        margin: 18px 0;
    }

    /* SIDEBAR NAVIGATION RADIO */

    [data-testid="stSidebar"] [data-testid="stRadio"] > label {
        color: #94A3B8;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.6px;
        margin-bottom: 10px;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
        gap: 7px;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label {
        background: transparent;
        border: 1px solid transparent;
        border-radius: 11px;
        padding: 10px 13px;
        transition: all 0.2s ease;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background: rgba(124,58,237,0.12);
        border-color: rgba(167,139,250,0.20);
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label p {
        color: #CBD5E1;
        font-weight: 600;
        font-size: 13px;
    }

    /* METRIC CARDS */

    [data-testid="stMetric"] {
        background: linear-gradient(145deg, rgba(30,35,61,0.96), rgba(15,19,37,0.98));
        border: 1px solid rgba(167,139,250,0.20);
        border-radius: 17px;
        padding: 21px 22px;
        box-shadow: 0 12px 35px rgba(0,0,0,0.20);
        transition: all 0.25s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        border-color: rgba(167,139,250,0.65);
        box-shadow: 0 15px 35px rgba(124,58,237,0.12);
    }

    [data-testid="stMetricLabel"] {
        color: #A5B4FC !important;
        font-size: 13px !important;
        font-weight: 650 !important;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 30px !important;
        font-weight: 850 !important;
    }

    /* BUTTONS */

    .stButton > button,
    .stFormSubmitButton > button,
    .stDownloadButton > button {
        background: linear-gradient(110deg, #7C3AED, #6366F1);
        color: #FFFFFF;
        border: 1px solid rgba(196,181,253,0.25);
        border-radius: 11px;
        padding: 10px 19px;
        font-weight: 700;
        transition: all 0.25s ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover,
    .stDownloadButton > button:hover {
        background: linear-gradient(110deg, #9333EA, #4F46E5);
        border-color: #A78BFA;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(124,58,237,0.28);
    }

    /* INPUTS */

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {
        background: #12172A !important;
        color: #F8FAFC !important;
        border: 1px solid #303957 !important;
        border-radius: 10px !important;
    }

    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 0 2px rgba(139,92,246,0.15) !important;
    }

    /* SELECT BOX */

    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background: #12172A;
        border-color: #303957;
        border-radius: 10px;
        color: #F8FAFC;
    }

    /* FILE UPLOADER */

    [data-testid="stFileUploader"] {
        background: rgba(30,27,58,0.40);
        border: 1px dashed rgba(167,139,250,0.65);
        border-radius: 16px;
        padding: 18px;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: #C4B5FD;
        background: rgba(124,58,237,0.10);
    }

    /* CONTAINERS */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(145deg, rgba(25,30,53,0.80), rgba(15,19,36,0.90));
        border: 1px solid rgba(148,163,184,0.15);
        border-radius: 17px;
    }

    /* EXPANDERS */

    [data-testid="stExpander"] {
        background: rgba(21,26,46,0.72);
        border: 1px solid rgba(167,139,250,0.18);
        border-radius: 13px;
    }

    [data-testid="stExpander"] summary {
        color: #E2E8F0;
        font-weight: 650;
    }

    /* TABLES */

    [data-testid="stDataFrame"] {
        border: 1px solid rgba(167,139,250,0.18);
        border-radius: 12px;
        overflow: hidden;
    }

    /* PROGRESS */

    .stProgress > div > div > div {
        background: linear-gradient(90deg, #9333EA, #6366F1, #38BDF8);
    }

    /* CHARTS */

    [data-testid="stVegaLiteChart"],
    [data-testid="stArrowVegaLiteChart"] {
        background: rgba(18,23,42,0.45);
        border: 1px solid rgba(167,139,250,0.13);
        border-radius: 15px;
        padding: 12px;
    }

    /* ALERTS AND DIVIDERS */

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    hr {
        border-color: rgba(167,139,250,0.18);
    }

    /* HERO SECTION */

    .talentai-hero {
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(circle at 90% 20%, rgba(124,58,237,0.22), transparent 35%),
            linear-gradient(115deg, rgba(30,27,75,0.85), rgba(17,24,49,0.88));
        border: 1px solid rgba(167,139,250,0.23);
        border-radius: 22px;
        padding: 32px;
        margin-bottom: 27px;
        box-shadow: 0 15px 45px rgba(0,0,0,0.18);
    }

    /* RESPONSIVE */

    @media (max-width: 768px) {
        .block-container {
            padding: 1.2rem 1rem 2rem;
        }

        .hero-title {
            font-size: 32px;
        }

        [data-testid="stMetric"] {
            padding: 15px;
        }

        .talentai-hero {
            padding: 23px;
        }
    }

    </style>
    """)


# ==========================================
# TALENTAI SIDEBAR BRANDING
# ==========================================

def render_sidebar():

    with st.sidebar:

        st.html("""
        <div style="padding: 12px 5px 25px 5px;">

            <div style="display:flex; align-items:center; gap:12px;">

                <div style="
                    width:46px;
                    height:46px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    background:linear-gradient(135deg,#9333EA,#4F46E5);
                    border-radius:14px;
                    font-size:23px;
                    box-shadow:0 5px 20px rgba(124,58,237,0.35);
                ">
                    🤖
                </div>

                <div>
                    <div style="
                        font-size:22px;
                        font-weight:850;
                        color:#FFFFFF;
                        letter-spacing:-0.6px;
                    ">
                        TalentAI
                    </div>

                    <div style="
                        font-size:9px;
                        color:#A78BFA;
                        font-weight:800;
                        letter-spacing:1.8px;
                        margin-top:4px;
                    ">
                        RESUME INTELLIGENCE
                    </div>
                </div>

            </div>
        </div>

        <div style="
            color:#64748B;
            font-size:10px;
            font-weight:800;
            letter-spacing:1.8px;
            padding:5px 5px 12px;
        ">
            WORKSPACE
        </div>
        """)

        st.markdown("### ✨ AI Resume Screening")

        st.caption("Intelligent candidate matching")

        st.divider()

        st.html("""
        <div style="
            background:linear-gradient(135deg,rgba(124,58,237,0.16),rgba(59,130,246,0.07));
            border:1px solid rgba(167,139,250,0.25);
            border-radius:14px;
            padding:15px;
            margin-top:15px;
        ">

            <div style="color:#C4B5FD;font-size:13px;font-weight:800;">
                ✦ AI ENGINE
            </div>

            <div style="color:#94A3B8;font-size:11px;margin-top:7px;">
                Resume intelligence system
            </div>

            <div style="display:flex;align-items:center;gap:8px;margin-top:13px;">

                <div style="
                    width:7px;
                    height:7px;
                    background:#22C55E;
                    border-radius:50%;
                    box-shadow:0 0 8px #22C55E;
                "></div>

                <span style="color:#86EFAC;font-size:11px;font-weight:700;">
                    SYSTEM READY
                </span>

            </div>
        </div>

        <div style="
            padding:22px 5px 5px;
            color:#64748B;
            font-size:10px;
            line-height:1.8;
        ">
            TALENTAI PLATFORM<br>
            Intelligent Recruitment Workspace
        </div>
        """)


# ==========================================
# HERO SECTION
# ==========================================

def render_hero():

    st.html("""
    <div class="talentai-hero">

        <div class="hero-eyebrow">
            ✦ INTELLIGENT RECRUITMENT PLATFORM
        </div>

        <div class="hero-title">
            AI Resume Intelligence
        </div>

        <div class="hero-subtitle">
            Analyze resumes. Discover skills.
            Find the right talent with intelligent matching.
        </div>

        <div style="
            display:flex;
            align-items:center;
            gap:9px;
            margin-top:20px;
        ">

            <div style="
                width:7px;
                height:7px;
                background:#22C55E;
                border-radius:50%;
                box-shadow:0 0 9px #22C55E;
            "></div>

            <span style="
                color:#86EFAC;
                font-size:11px;
                font-weight:700;
                letter-spacing:0.5px;
            ">
                AI ENGINE ONLINE
            </span>

            <span style="
                color:#64748B;
                font-size:11px;
                margin-left:7px;
            ">
                • Resume screening workspace
            </span>

        </div>

    </div>
    """)
