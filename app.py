import os
import uuid
import html
import pandas as pd
import streamlit as st

from SRC.ui import (
    apply_premium_theme,
    render_sidebar
)

from SRC.resume_parser import (
    extract_resume_text,
    extract_candidate_details
)

from SRC.text_cleaner import clean_resume_text
from SRC.skill_extractor import extract_skills

from SRC.database import (
    save_candidate,
    save_resume,
    save_candidate_skills,
    get_dashboard_metrics,
    save_match_result,
    get_recent_screenings,
    save_job_description,
    get_job_descriptions,
    get_candidates_by_job
)

from SRC.job_matcher import calculate_skill_match


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="TalentAI | Resume Intelligence",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_premium_theme()
render_sidebar()


# ==========================================
# NAVIGATION CALLBACK
# ==========================================

def navigate_to(page):
    st.session_state["main_navigation"] = page


# ==========================================
# NAVIGATION
# ==========================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            color:#64748B;
            font-size:10px;
            font-weight:800;
            letter-spacing:1.8px;
            margin:12px 0 8px 5px;
        ">
            MAIN MENU
        </div>
        """,
        unsafe_allow_html=True
    )

    selected_page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Resume Screening",
            "Job Management",
            "Candidate Ranking",
            "Screening History"
        ],
        label_visibility="collapsed",
        format_func=lambda page: {
            "Dashboard": "🏠  Dashboard",
            "Resume Screening": "📄  Resume Screening",
            "Job Management": "💼  Job Management",
            "Candidate Ranking": "🏆  Candidate Ranking",
            "Screening History": "🕘  Screening History"
        }[page],
        key="main_navigation"
    )

    st.divider()


# ==========================================
# LOAD APPLICATION DATA
# ==========================================

try:
    saved_jobs = get_job_descriptions() or []
except Exception as error:
    saved_jobs = []
    st.error(f"Unable to fetch saved jobs: {error}")


try:
    (
        total_candidates,
        total_resumes,
        average_match_score
    ) = get_dashboard_metrics()

except Exception as error:
    total_candidates = 0
    total_resumes = 0
    average_match_score = 0
    st.error(f"Unable to load dashboard metrics: {error}")


# ==========================================
# REUSABLE FUNCTIONS
# ==========================================

def render_page_header(eyebrow, title, subtitle):

    st.html(f"""
    <div style="
        margin-bottom:28px;
        padding-bottom:18px;
        border-bottom:1px solid rgba(167,139,250,0.15);
    ">
        <div style="
            color:#A78BFA;
            font-size:10px;
            font-weight:800;
            letter-spacing:2px;
            margin-bottom:9px;
        ">
            {html.escape(eyebrow.upper())}
        </div>

        <div style="
            color:#F8FAFC;
            font-size:32px;
            font-weight:850;
            letter-spacing:-1px;
        ">
            {html.escape(title)}
        </div>

        <div style="
            color:#94A3B8;
            font-size:13px;
            margin-top:8px;
        ">
            {html.escape(subtitle)}
        </div>
    </div>
    """)


def render_job_selector(key):

    if not saved_jobs:
        st.warning("Please create a job description first.")
        return None

    return st.selectbox(
        "Select Job Description",
        options=saved_jobs,
        format_func=lambda job: (
            f"{job[1]} | {job[2]}-{job[3]} Years"
        ),
        key=key
    )


# ==========================================
# DASHBOARD PAGE
# ==========================================

if selected_page == "Dashboard":

    recent_screenings = get_recent_screenings(limit=10) or []

    # ------------------------------------------
    # DASHBOARD DATA
    # ------------------------------------------

    safe_candidates = int(total_candidates or 0)
    safe_resumes = int(total_resumes or 0)
    safe_average = float(average_match_score or 0)
    safe_jobs = len(saved_jobs)

    # ------------------------------------------
    # CUSTOM ANALYTICS CHART
    # ------------------------------------------

    chart_points = []

    if recent_screenings:
        chart_rows = list(reversed(recent_screenings[:10]))

        chart_values = [
            max(0, min(float(row[3] or 0), 100))
            for row in chart_rows
        ]

        chart_width = 760
        chart_height = 260
        left = 55
        right = 20
        top = 20
        bottom = 45

        plot_width = chart_width - left - right
        plot_height = chart_height - top - bottom

        for index, value in enumerate(chart_values):
            x = (
                left + index * plot_width / max(len(chart_values) - 1, 1)
            )
            y = top + (100 - value) / 100 * plot_height

            chart_points.append({
                "x": x,
                "y": y,
                "value": value
            })

        polyline = " ".join(
            f"{point['x']:.1f},{point['y']:.1f}"
            for point in chart_points
        )

        area_points = (
            f"{left},{top + plot_height} "
            + polyline
            + f" {left + plot_width},{top + plot_height}"
        )

        chart_grid = ""

        for tick in [0, 25, 50, 75, 100]:
            y = top + (100 - tick) / 100 * plot_height

            chart_grid += f"""
            <line x1="{left}" y1="{y}" x2="{left + plot_width}"
                  y2="{y}" stroke="#29213D" stroke-width="1"
                  stroke-dasharray="5 6"/>

            <text x="12" y="{y + 5}" fill="#9187A9"
                  font-size="12">{tick}%</text>
            """

        chart_dots = ""

        for index, point in enumerate(chart_points):
            chart_dots += f"""
            <circle cx="{point['x']}" cy="{point['y']}" r="5"
                    fill="#C4B5FD" stroke="#090710"
                    stroke-width="3"/>

            <text x="{point['x']}" y="{point['y'] - 13}"
                  fill="#E9D5FF" font-size="11"
                  text-anchor="middle">
                {point['value']:.0f}
            </text>

            <text x="{point['x']}" y="{top + plot_height + 25}"
                  fill="#8D849F" font-size="11"
                  text-anchor="middle">
                {index + 1}
            </text>
            """

        chart_svg = f"""
        <svg viewBox="0 0 {chart_width} {chart_height}"
             width="100%" role="img"
             aria-label="Candidate match score trend">

            <defs>
                <linearGradient id="taArea" x1="0" y1="0"
                                x2="0" y2="1">
                    <stop offset="0%" stop-color="#A855F7"
                          stop-opacity=".35"/>
                    <stop offset="100%" stop-color="#A855F7"
                          stop-opacity="0"/>
                </linearGradient>

                <filter id="taGlow">
                    <feGaussianBlur stdDeviation="4"
                                    result="blur"/>
                    <feMerge>
                        <feMergeNode in="blur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>

            {chart_grid}

            <polygon points="{area_points}"
                     fill="url(#taArea)"/>

            <polyline points="{polyline}"
                      fill="none" stroke="#B57AFF"
                      stroke-width="3.5"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      filter="url(#taGlow)"/>

            {chart_dots}

        </svg>
        """

        latest_score = chart_values[-1]
        highest_score = max(chart_values)
        chart_count = len(chart_values)

    else:
        chart_svg = ""
        latest_score = 0
        highest_score = 0
        chart_count = 0

    # ------------------------------------------
    # DASHBOARD STYLING
    # ------------------------------------------

    st.html("""
    <style>

    .ta-dashboard {
        color: #F8F7FF;
    }

    .ta-hero {
        position: relative;
        overflow: hidden;
        padding: 46px 44px;
        border-radius: 24px;
        background:
            radial-gradient(
                circle at 85% 20%,
                rgba(147, 51, 234, .30),
                transparent 32%
            ),
            radial-gradient(
                circle at 55% 120%,
                rgba(91, 33, 182, .22),
                transparent 45%
            ),
            linear-gradient(120deg, #08060D, #130B20 65%, #190D2D);
        border: 1px solid rgba(168, 85, 247, .38);
        box-shadow:
            0 0 30px rgba(147, 51, 234, .12),
            inset 0 0 30px rgba(139, 92, 246, .04);
        margin-bottom: 32px;
    }

    .ta-hero-label {
        color: #C4A5FF;
        font-size: 13px;
        font-weight: 850;
        letter-spacing: 2.8px;
    }

    .ta-hero-title {
        color: #FFFFFF;
        font-size: 44px;
        line-height: 1.2;
        font-weight: 900;
        letter-spacing: -1.7px;
        margin-top: 17px;
    }

    .ta-hero-title span {
        color: #B77AFF;
        text-shadow: 0 0 25px rgba(168, 85, 247, .8);
    }

    .ta-hero-description {
        color: #B8AEC9;
        font-size: 16px;
        line-height: 1.8;
        max-width: 610px;
        margin-top: 15px;
    }

    .ta-hero-status {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        margin-top: 26px;
        padding: 11px 17px;
        border-radius: 30px;
        background: rgba(34, 197, 94, .09);
        border: 1px solid rgba(74, 222, 128, .3);
        color: #86EFAC;
        font-size: 12px;
        font-weight: 850;
        letter-spacing: 1.3px;
    }

    .ta-hero-art {
        position: absolute;
        right: 48px;
        top: 18px;
        font-size: 150px;
        color: #B57AFF;
        opacity: .16;
        text-shadow: 0 0 50px #A855F7;
    }

    .ta-section-title {
        color: #F7F2FF;
        font-size: 27px;
        font-weight: 850;
        letter-spacing: -.7px;
        margin: 30px 0 5px;
    }

    .ta-section-subtitle {
        color: #9B91AC;
        font-size: 14px;
        margin-bottom: 21px;
    }

    .ta-kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 17px;
        margin: 0 0 30px;
    }

    .ta-kpi {
        position: relative;
        overflow: hidden;
        min-height: 165px;
        padding: 23px;
        border-radius: 19px;
        background:
            radial-gradient(
                circle at 100% 0%,
                rgba(147, 51, 234, .13),
                transparent 48%
            ),
            linear-gradient(145deg, #17121F, #0D0B13);
        border: 1px solid rgba(168, 85, 247, .25);
        box-shadow: 0 10px 30px rgba(0, 0, 0, .25);
        transition: .25s ease;
    }

    .ta-kpi:hover {
        transform: translateY(-5px);
        border-color: rgba(192, 132, 252, .75);
        box-shadow: 0 0 25px rgba(147, 51, 234, .18);
    }

    .ta-kpi-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .ta-kpi-label {
        color: #B8ADC9;
        font-size: 12px;
        font-weight: 850;
        letter-spacing: 1px;
    }

    .ta-kpi-icon {
        width: 43px;
        height: 43px;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 13px;
        font-size: 22px;
        background: rgba(168, 85, 247, .15);
        border: 1px solid rgba(168, 85, 247, .22);
    }

    .ta-kpi-value {
        color: #FFFFFF;
        font-size: 39px;
        line-height: 1.2;
        font-weight: 900;
        letter-spacing: -1.3px;
        margin-top: 17px;
    }

    .ta-kpi-description {
        color: #958AA7;
        font-size: 13px;
        margin-top: 7px;
    }

    .ta-panel {
        background:
            radial-gradient(
                circle at 100% 0%,
                rgba(126, 34, 206, .10),
                transparent 40%
            ),
            linear-gradient(145deg, #17121F, #0D0B13);
        border: 1px solid rgba(168, 85, 247, .23);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, .20);
        height: 100%;
    }

    .ta-panel-title {
        color: #F7F2FF;
        font-size: 19px;
        font-weight: 850;
    }

    .ta-panel-subtitle {
        color: #968BA8;
        font-size: 13px;
        margin-top: 7px;
        line-height: 1.6;
    }

    .ta-insight {
        padding: 21px;
        margin-top: 20px;
        border-radius: 16px;
        background: rgba(139, 92, 246, .10);
        border: 1px solid rgba(168, 85, 247, .25);
    }

    .ta-insight-label {
        color: #C4A5FF;
        font-size: 12px;
        font-weight: 850;
        letter-spacing: 1.2px;
    }

    .ta-insight-value {
        color: #FFFFFF;
        font-size: 37px;
        font-weight: 900;
        margin-top: 8px;
    }

    .ta-insight-description {
        color: #A79BB9;
        font-size: 13px;
        margin-top: 5px;
    }

    .ta-status {
        padding: 19px;
        margin-top: 14px;
        border-radius: 16px;
        background: rgba(34, 197, 94, .055);
        border: 1px solid rgba(34, 197, 94, .20);
    }

    .ta-status-title {
        color: #86EFAC;
        font-size: 12px;
        font-weight: 850;
        letter-spacing: 1.2px;
    }

    .ta-status-value {
        color: #F3FFF6;
        font-size: 18px;
        font-weight: 800;
        margin-top: 11px;
    }

    .ta-chart-summary {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 22px;
    }

    .ta-chart-stat {
        flex: 1;
        min-width: 115px;
        padding: 13px;
        background: rgba(168, 85, 247, .08);
        border: 1px solid rgba(168, 85, 247, .17);
        border-radius: 13px;
    }

    .ta-chart-stat-label {
        color: #A99BBE;
        font-size: 11px;
        font-weight: 750;
    }

    .ta-chart-stat-value {
        color: #E9D5FF;
        font-size: 23px;
        font-weight: 850;
        margin-top: 5px;
    }

    .ta-activity {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 15px;
        padding: 17px 20px;
        margin-bottom: 12px;
        border-radius: 16px;
        background: linear-gradient(110deg, #17121F, #0E0B14);
        border: 1px solid rgba(168, 85, 247, .19);
        transition: .2s ease;
    }

    .ta-activity:hover {
        border-color: rgba(192, 132, 252, .65);
        box-shadow: 0 0 20px rgba(147, 51, 234, .10);
    }

    .ta-activity-left {
        display: flex;
        align-items: center;
        gap: 15px;
        min-width: 0;
    }

    .ta-avatar {
        width: 49px;
        height: 49px;
        min-width: 49px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 15px;
        background: linear-gradient(135deg, #9333EA, #581C87);
        border: 1px solid rgba(216, 180, 254, .35);
        color: white;
        font-size: 19px;
        font-weight: 900;
        box-shadow: 0 0 16px rgba(147, 51, 234, .25);
    }

    .ta-candidate-name {
        color: #F8F4FF;
        font-size: 16px;
        font-weight: 800;
    }

    .ta-resume-name {
        color: #A49AB3;
        font-size: 13px;
        margin-top: 6px;
    }

    .ta-score {
        font-size: 24px;
        font-weight: 900;
        text-align: right;
    }

    .ta-score-label {
        font-size: 10px;
        font-weight: 850;
        letter-spacing: .7px;
        text-align: right;
        margin-top: 4px;
    }

    .ta-quick-card {
        padding: 23px;
        min-height: 185px;
        border-radius: 18px;
        background:
            radial-gradient(
                circle at 100% 0%,
                rgba(147, 51, 234, .16),
                transparent 50%
            ),
            linear-gradient(145deg, #17121F, #0D0B13);
        border: 1px solid rgba(168, 85, 247, .24);
        box-shadow: 0 10px 25px rgba(0, 0, 0, .20);
        transition: .25s ease;
    }

    .ta-quick-card:hover {
        transform: translateY(-4px);
        border-color: rgba(192, 132, 252, .7);
        box-shadow: 0 0 25px rgba(147, 51, 234, .16);
    }

    .ta-quick-icon {
        font-size: 31px;
    }

    .ta-quick-title {
        color: #F5EEFF;
        font-size: 18px;
        font-weight: 850;
        margin-top: 14px;
    }

    .ta-quick-description {
        color: #A79BB8;
        font-size: 13px;
        line-height: 1.7;
        margin-top: 8px;
    }

    @media(max-width: 900px) {
        .ta-kpi-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .ta-hero-art {
            display: none;
        }
    }

    @media(max-width: 550px) {
        .ta-kpi-grid {
            grid-template-columns: 1fr;
        }

        .ta-hero {
            padding: 28px;
        }

        .ta-hero-title {
            font-size: 32px;
        }

        .ta-hero-description {
            font-size: 14px;
        }
    }

    </style>
    """)

    # ------------------------------------------
    # HERO SECTION
    # ------------------------------------------

    st.html("""
    <div class="ta-hero">

        <div class="ta-hero-label">
            ✦ TALENTAI / INTELLIGENT RECRUITMENT PLATFORM
        </div>

        <div class="ta-hero-title">
            Find the right talent<span>.</span>
        </div>

        <div class="ta-hero-description">
            Welcome to your AI-powered recruitment workspace.
            Analyze resumes, discover candidate skills and identify
            the best talent with intelligent matching.
        </div>

        <div class="ta-hero-status">
            ● &nbsp; AI ENGINE ONLINE
        </div>

        <div class="ta-hero-art">✧</div>

    </div>
    """)

    # ------------------------------------------
    # KPI CARDS
    # ------------------------------------------

    st.html(f"""
    <div class="ta-section-title">Dashboard Overview</div>

    <div class="ta-section-subtitle">
        Your recruitment performance at a glance
    </div>

    <div class="ta-kpi-grid">

        <div class="ta-kpi">
            <div class="ta-kpi-top">
                <div class="ta-kpi-label">TOTAL CANDIDATES</div>
                <div class="ta-kpi-icon">👥</div>
            </div>
            <div class="ta-kpi-value">{safe_candidates}</div>
            <div class="ta-kpi-description">
                Registered candidate profiles
            </div>
        </div>

        <div class="ta-kpi">
            <div class="ta-kpi-top">
                <div class="ta-kpi-label">RESUMES ANALYZED</div>
                <div class="ta-kpi-icon">📄</div>
            </div>
            <div class="ta-kpi-value">{safe_resumes}</div>
            <div class="ta-kpi-description">
                Documents processed by AI
            </div>
        </div>

        <div class="ta-kpi">
            <div class="ta-kpi-top">
                <div class="ta-kpi-label">AVERAGE MATCH SCORE</div>
                <div class="ta-kpi-icon">🎯</div>
            </div>
            <div class="ta-kpi-value">{safe_average:.1f}%</div>
            <div class="ta-kpi-description">
                Candidate compatibility score
            </div>
        </div>

        <div class="ta-kpi">
            <div class="ta-kpi-top">
                <div class="ta-kpi-label">ACTIVE JOBS</div>
                <div class="ta-kpi-icon">💼</div>
            </div>
            <div class="ta-kpi-value">{safe_jobs}</div>
            <div class="ta-kpi-description">
                Available job descriptions
            </div>
        </div>

    </div>
    """)

    # ------------------------------------------
    # RECRUITMENT ANALYTICS
    # ------------------------------------------

    st.html("""
    <div class="ta-section-title">Recruitment Analytics</div>

    <div class="ta-section-subtitle">
        Monitor candidate matching performance and workspace activity
    </div>
    """)

    analytics_col, insights_col = st.columns(
        [1.8, 1],
        gap="large"
    )

    with analytics_col:

        st.html("""
        <div class="ta-panel">

            <div class="ta-panel-title">
                📈 Screening Performance
            </div>

            <div class="ta-panel-subtitle">
                Candidate match scores across recent screenings
            </div>

        """)

        if recent_screenings:

            st.html(f"""
            <div style="margin-top:25px;">
                {chart_svg}
            </div>

            <div class="ta-chart-summary">

                <div class="ta-chart-stat">
                    <div class="ta-chart-stat-label">
                        LATEST MATCH
                    </div>
                    <div class="ta-chart-stat-value">
                        {latest_score:.1f}%
                    </div>
                </div>

                <div class="ta-chart-stat">
                    <div class="ta-chart-stat-label">
                        HIGHEST MATCH
                    </div>
                    <div class="ta-chart-stat-value">
                        {highest_score:.1f}%
                    </div>
                </div>

                <div class="ta-chart-stat">
                    <div class="ta-chart-stat-label">
                        SCREENINGS
                    </div>
                    <div class="ta-chart-stat-value">
                        {chart_count}
                    </div>
                </div>

            </div>
            </div>
            """)

        else:

            st.html("""
            <div style="
                padding:45px 15px;
                text-align:center;
                color:#A79BB8;
                font-size:14px;
            ">
                <div style="font-size:38px;margin-bottom:12px;">
                    📊
                </div>
                Your analytics will appear here after
                your first resume screening.
            </div>
            </div>
            """)

    with insights_col:

        st.html(f"""
        <div class="ta-panel">

            <div class="ta-panel-title">
                ✦ AI Workspace Insights
            </div>

            <div class="ta-panel-subtitle">
                Your recruitment workspace status
            </div>

            <div class="ta-insight">

                <div class="ta-insight-label">
                    JOB DESCRIPTIONS
                </div>

                <div class="ta-insight-value">
                    {safe_jobs}
                </div>

                <div class="ta-insight-description">
                    Recruitment roles created
                </div>

            </div>

            <div class="ta-status">

                <div class="ta-status-title">
                    SYSTEM STATUS
                </div>

                <div class="ta-status-value">
                    ● All systems ready
                </div>

                <div class="ta-insight-description">
                    Resume parsing and skill matching are available
                </div>

            </div>

        </div>
        """)

    # ------------------------------------------
    # RECENT SCREENING ACTIVITY
    # ------------------------------------------

    st.html("""
    <div class="ta-section-title">
        Recent Screening Activity
    </div>

    <div class="ta-section-subtitle">
        Latest candidates analyzed by TalentAI
    </div>
    """)

    if recent_screenings:

        activity_html = ""

        for row in recent_screenings[:5]:

            candidate_name = html.escape(
                str(row[1] or "Unknown")
            )

            resume_name = html.escape(
                str(row[2] or "Resume")
            )

            match_score = max(
                0,
                min(float(row[3] or 0), 100)
            )

            if match_score >= 75:
                score_color = "#86EFAC"
                score_label = "STRONG MATCH"

            elif match_score >= 50:
                score_color = "#FCD34D"
                score_label = "MODERATE MATCH"

            else:
                score_color = "#FCA5A5"
                score_label = "LOW MATCH"

            initial = html.escape(
                candidate_name[0].upper()
            )

            activity_html += f"""
            <div class="ta-activity">

                <div class="ta-activity-left">

                    <div class="ta-avatar">
                        {initial}
                    </div>

                    <div>
                        <div class="ta-candidate-name">
                            {candidate_name}
                        </div>

                        <div class="ta-resume-name">
                            {resume_name}
                        </div>
                    </div>

                </div>

                <div>
                    <div class="ta-score"
                         style="color:{score_color};">
                        {match_score:.1f}%
                    </div>

                    <div class="ta-score-label"
                         style="color:{score_color};">
                        {score_label}
                    </div>
                </div>

            </div>
            """

        st.html(activity_html)

    else:

        st.info(
            "No screening activity available yet. "
            "Analyze your first resume to see candidate activity here."
        )

    # ------------------------------------------
    # QUICK ACTIONS
    # ------------------------------------------

    st.html("""
    <div class="ta-section-title">
        Quick Actions
    </div>

    <div class="ta-section-subtitle">
        Continue working in your recruitment workspace
    </div>
    """)

    action1, action2, action3 = st.columns(
        3,
        gap="medium"
    )

    with action1:

        st.html("""
        <div class="ta-quick-card">

            <div class="ta-quick-icon">📄</div>

            <div class="ta-quick-title">
                Resume Screening
            </div>

            <div class="ta-quick-description">
                Upload and analyze candidate resumes with
                AI-powered skill matching.
            </div>

        </div>
        """)

        st.button(
            "Start Screening →",
            key="dashboard_screening",
            use_container_width=True,
            on_click=navigate_to,
            args=("Resume Screening",)
        )

    with action2:

        st.html("""
        <div class="ta-quick-card">

            <div class="ta-quick-icon">💼</div>

            <div class="ta-quick-title">
                Job Management
            </div>

            <div class="ta-quick-description">
                Create, organize and manage your recruitment
                job descriptions.
            </div>

        </div>
        """)

        st.button(
            "Manage Jobs →",
            key="dashboard_jobs",
            use_container_width=True,
            on_click=navigate_to,
            args=("Job Management",)
        )

    with action3:

        st.html("""
        <div class="ta-quick-card">

            <div class="ta-quick-icon">🏆</div>

            <div class="ta-quick-title">
                Candidate Ranking
            </div>

            <div class="ta-quick-description">
                Compare candidate profiles and discover
                your strongest matches.
            </div>

        </div>
        """)

        st.button(
            "View Rankings →",
            key="dashboard_ranking",
            use_container_width=True,
            on_click=navigate_to,
            args=("Candidate Ranking",)
        )



elif selected_page == "Job Management":

    render_page_header(
        "Recruitment Workspace",
        "Job Management",
        "Create, organize and manage job descriptions for candidate screening."
    )

    st.markdown("### ✦ Create New Job")

    with st.container(border=True):

        with st.form("job_management_form"):

            job_title = st.text_input(
                "Job Title",
                placeholder="Example: Python Developer"
            )

            experience_col1, experience_col2 = st.columns(2)

            with experience_col1:

                min_experience = st.number_input(
                    "Minimum Experience (Years)",
                    min_value=0,
                    max_value=50,
                    value=1,
                    step=1
                )

            with experience_col2:

                max_experience = st.number_input(
                    "Maximum Experience (Years)",
                    min_value=0,
                    max_value=50,
                    value=3,
                    step=1
                )

            new_job_description = st.text_area(
                "Job Description",
                placeholder=(
                    "Paste the complete job description here...\n\n"
                    "Example:\n"
                    "Required skills: Python, SQL, PostgreSQL, "
                    "Data Analysis..."
                ),
                height=220
            )

            save_job_button = st.form_submit_button(
                "＋ Save Job Description",
                use_container_width=True,
                type="primary"
            )

            if save_job_button:

                if not job_title.strip():

                    st.error("Please enter a job title.")

                elif not new_job_description.strip():

                    st.error("Please enter the job description.")

                elif max_experience < min_experience:

                    st.error(
                        "Maximum experience cannot be less than "
                        "minimum experience."
                    )

                else:

                    try:

                        save_job_description(
                            job_title.strip(),
                            int(min_experience),
                            int(max_experience),
                            new_job_description.strip()
                        )

                        st.success(
                            "Job description saved successfully!"
                        )

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Unable to save job description: {error}"
                        )

    # SAVED JOBS

    st.markdown("")
    st.markdown("### 📋 Saved Job Descriptions")

    if saved_jobs:

        st.caption(
            f"{len(saved_jobs)} recruitment roles available"
        )

        for job in saved_jobs:

            with st.container(border=True):

                job_col, experience_col = st.columns(
                    [3, 1],
                    vertical_alignment="center"
                )

                with job_col:

                    st.markdown(f"#### 💼 {job[1]}")

                    st.caption(
                        f"Job ID: {job[0]}"
                    )

                with experience_col:

                    st.metric(
                        "Experience",
                        f"{job[2]}–{job[3]} Years"
                    )

                with st.expander("View Job Description"):

                    st.write(job[5])

    else:

        st.info(
            "No job descriptions found. Create your first job above."
        )


# ==========================================
# RESUME SCREENING PAGE
# ==========================================

elif selected_page == "Resume Screening":

    render_page_header(
        "AI Intelligence",
        "Resume Screening",
        "Upload candidate resumes and discover their compatibility with your job requirements."
    )

    st.markdown("### 📂 Upload Candidate Resume")

    upload_col, job_col = st.columns(2, gap="large")

    with upload_col:

        with st.container(border=True):

            st.markdown("#### 📄 Resume Upload")

            uploaded_file = st.file_uploader(
                "Upload resume in PDF format",
                type=["pdf"],
                help="Upload a candidate's PDF resume.",
                key="resume_upload"
            )

            st.caption("Supported format: PDF")

            if uploaded_file:
                st.success(f"Selected: {uploaded_file.name}")

    with job_col:

        with st.container(border=True):

            st.markdown("#### 💼 Select Job Description")

            selected_job = render_job_selector("selected_job")

            if selected_job:

                selected_job_id = selected_job[0]
                job_description = selected_job[5]

                st.success(
                    f"Selected Job: {selected_job[1]}"
                )

                with st.expander("👁️ View Job Description"):
                    st.write(job_description)

            else:

                selected_job_id = None
                job_description = ""

    st.markdown("")

    analyze_button = st.button(
        "✨ Analyze Resume",
        use_container_width=True,
        type="primary",
        disabled=not saved_jobs
    )

    if analyze_button:

        if uploaded_file is None:

            st.warning("Please upload a PDF resume first.")

        elif selected_job is None:

            st.warning("Please select a saved job description.")

        elif not job_description.strip():

            st.warning("The selected job description is empty.")

        else:

            try:

                with st.spinner(
                    "AI is analyzing the candidate resume..."
                ):

                    # STEP 1: SAVE UPLOADED PDF

                    upload_folder = os.path.join(
                        "data",
                        "resumes",
                        "uploads"
                    )

                    os.makedirs(upload_folder, exist_ok=True)

                    unique_file_name = (
                        str(uuid.uuid4())
                        + "_"
                        + os.path.basename(uploaded_file.name)
                    )

                    file_path = os.path.join(
                        upload_folder,
                        unique_file_name
                    )

                    with open(file_path, "wb") as file:
                        file.write(uploaded_file.getbuffer())

                    # STEP 2: EXTRACT RESUME TEXT

                    resume_text = extract_resume_text(file_path)

                    cleaned_text = clean_resume_text(resume_text)

                    # STEP 3: EXTRACT CANDIDATE DETAILS AND SKILLS

                    candidate_details = extract_candidate_details(
                        resume_text
                    )

                    candidate_skills = extract_skills(cleaned_text)

                    required_skills = extract_skills(
                        job_description
                    )

                    # STEP 4: VALIDATE INFORMATION

                    required_fields = [
                        "full_name",
                        "email",
                        "phone",
                        "location",
                        "experience_years",
                        "education"
                    ]

                    missing_fields = [
                        field
                        for field in required_fields
                        if (
                            candidate_details.get(field) is None
                            or candidate_details.get(field) == ""
                        )
                    ]

                    if missing_fields:

                        st.error(
                            "Some candidate details could not be "
                            "extracted: "
                            + ", ".join(missing_fields)
                        )

                        st.stop()

                    if not candidate_skills:

                        st.warning(
                            "No recognized skills were found in this resume."
                        )

                        st.stop()

                    if not required_skills:

                        st.warning(
                            "No recognized skills were found in "
                            "the selected job description."
                        )

                        st.stop()

                    # STEP 5: SAVE CANDIDATE

                    candidate_id = save_candidate(
                        candidate_details["full_name"],
                        candidate_details["email"],
                        candidate_details["phone"],
                        candidate_details["location"],
                        candidate_details["experience_years"],
                        candidate_details["education"]
                    )

                    if candidate_id is None:
                        st.error("Unable to save candidate.")
                        st.stop()

                    # STEP 6: SAVE RESUME

                    resume_id = save_resume(
                        candidate_id,
                        uploaded_file.name,
                        file_path,
                        "PDF",
                        cleaned_text
                    )

                    if resume_id is None:
                        st.error("Unable to save resume.")
                        st.stop()

                    # STEP 7: SAVE CANDIDATE SKILLS

                    save_candidate_skills(
                        candidate_id,
                        candidate_skills
                    )

                    # STEP 8: CALCULATE MATCH SCORE

                    (
                        match_percentage,
                        matched_skills,
                        missing_skills
                    ) = calculate_skill_match(
                        candidate_skills,
                        required_skills
                    )

                    # STEP 9: SAVE MATCH RESULT

                    match_id = save_match_result(
                        candidate_id,
                        resume_id,
                        match_percentage,
                        matched_skills,
                        missing_skills,
                        job_id=selected_job_id
                    )

                    if match_id is None:
                        st.error("Unable to save match result.")
                        st.stop()

                # SCREENING RESULTS

                st.success(
                    "Resume analyzed and saved successfully!"
                )

                st.markdown("---")
                st.markdown("## 🎯 Screening Results")

                st.caption(
                    f"Selected Job: {selected_job[1]}"
                )

                score = max(
                    0,
                    min(float(match_percentage), 100)
                )

                circumference = 314.16
                dash_value = score / 100 * circumference

                score_col, analysis_col = st.columns(
                    [1, 2],
                    gap="large"
                )

                with score_col:

                    st.html(f"""
                    <div style="
                        background:linear-gradient(
                            145deg,
                            rgba(124,58,237,0.22),
                            rgba(30,41,75,0.65)
                        );
                        border:1px solid rgba(167,139,250,0.35);
                        border-radius:22px;
                        padding:25px 15px;
                        text-align:center;
                    ">

                        <div style="
                            color:#A78BFA;
                            font-size:13px;
                            font-weight:700;
                            letter-spacing:1.5px;
                            margin-bottom:18px;
                        ">
                            RESUME MATCH SCORE
                        </div>

                        <div style="
                            position:relative;
                            width:190px;
                            height:190px;
                            margin:auto;
                        ">

                            <svg width="190" height="190"
                                 viewBox="0 0 120 120">

                                <circle
                                    cx="60" cy="60" r="50"
                                    fill="none"
                                    stroke="rgba(148,163,184,0.15)"
                                    stroke-width="9"
                                />

                                <circle
                                    cx="60" cy="60" r="50"
                                    fill="none"
                                    stroke="#A78BFA"
                                    stroke-width="9"
                                    stroke-linecap="round"
                                    stroke-dasharray="{dash_value:.2f} {circumference:.2f}"
                                    transform="rotate(-90 60 60)"
                                />

                            </svg>

                            <div style="
                                position:absolute;
                                inset:0;
                                display:flex;
                                flex-direction:column;
                                justify-content:center;
                                align-items:center;
                            ">

                                <div style="
                                    color:white;
                                    font-size:34px;
                                    font-weight:850;
                                ">
                                    {score:.2f}%
                                </div>

                                <div style="
                                    color:#94A3B8;
                                    font-size:11px;
                                ">
                                    MATCH SCORE
                                </div>

                            </div>
                        </div>

                        <div style="
                            color:#94A3B8;
                            font-size:12px;
                            margin-top:15px;
                        ">
                            Candidate skills compatibility
                        </div>

                    </div>
                    """)

                with analysis_col:

                    with st.container(border=True):

                        st.markdown("### 📈 Match Analysis")

                        st.progress(score / 100)

                        metric1, metric2 = st.columns(2)

                        metric1.metric(
                            "Matched Skills",
                            len(matched_skills)
                        )

                        metric2.metric(
                            "Missing Skills",
                            len(missing_skills)
                        )

                        st.caption(
                            "Score is calculated using recognized skills "
                            "found in the resume and selected job description."
                        )

                # CANDIDATE INFORMATION

                st.markdown("### 👤 Candidate Information")

                with st.container(border=True):

                    info_col1, info_col2 = st.columns(2)

                    with info_col1:

                        st.write(
                            "**Full Name:**",
                            candidate_details["full_name"]
                        )

                        st.write(
                            "**Email:**",
                            candidate_details["email"]
                        )

                        st.write(
                            "**Phone:**",
                            candidate_details["phone"]
                        )

                    with info_col2:

                        st.write(
                            "**Location:**",
                            candidate_details["location"]
                        )

                        st.write(
                            "**Experience:**",
                            f'{candidate_details["experience_years"]} years'
                        )

                        st.write(
                            "**Education:**",
                            candidate_details["education"]
                        )

                # SKILL ANALYSIS

                st.markdown("### 🧠 Skill Analysis")

                skill_col1, skill_col2 = st.columns(2)

                with skill_col1:

                    with st.container(border=True):

                        st.markdown("#### 🟢 Matched Skills")

                        if matched_skills:

                            for skill in matched_skills:

                                safe_skill = html.escape(str(skill))

                                st.html(f"""
                                <div style="
                                    background:rgba(34,197,94,0.10);
                                    border:1px solid rgba(34,197,94,0.25);
                                    padding:10px 13px;
                                    border-radius:10px;
                                    margin-bottom:8px;
                                    color:#86EFAC;
                                    font-weight:600;
                                ">
                                    ✓ {safe_skill}
                                </div>
                                """)

                        else:

                            st.info("No matching skills found.")

                with skill_col2:

                    with st.container(border=True):

                        st.markdown("#### 🔴 Missing Skills")

                        if missing_skills:

                            for skill in missing_skills:

                                safe_skill = html.escape(str(skill))

                                st.html(f"""
                                <div style="
                                    background:rgba(239,68,68,0.10);
                                    border:1px solid rgba(239,68,68,0.25);
                                    padding:10px 13px;
                                    border-radius:10px;
                                    margin-bottom:8px;
                                    color:#FCA5A5;
                                    font-weight:600;
                                ">
                                    ✕ {safe_skill}
                                </div>
                                """)

                        else:

                            st.success("All required skills matched!")

                # EXTRACTED SKILLS

                with st.expander("🧠 View all extracted skills"):

                    st.write("**Candidate Skills:**")
                    st.write(", ".join(candidate_skills))

                    st.write("**Job Required Skills:**")
                    st.write(", ".join(required_skills))

                # DATABASE RECORDS

                with st.expander("🗄️ Database Record Information"):

                    st.write("Candidate ID:", candidate_id)
                    st.write("Resume ID:", resume_id)
                    st.write("Match ID:", match_id)
                    st.write("Job ID:", selected_job_id)

            except Exception as error:

                st.error(f"Something went wrong: {error}")

                st.info(
                    "Please check the terminal for more details."
                )


# ==========================================
# CANDIDATE RANKING PAGE
# ==========================================

elif selected_page == "Candidate Ranking":

    render_page_header(
        "Recruitment Analytics",
        "Candidate Ranking",
        "Compare candidate compatibility, explore skill gaps and identify top talent."
    )

    comparison_job = render_job_selector("comparison_job")

    if comparison_job:

        st.markdown("")

        if st.button(
            "🔍 Compare Candidates",
            use_container_width=True,
            type="primary",
            key="compare_candidates_button"
        ):

            comparison_results = get_candidates_by_job(
                comparison_job[0]
            )

            if comparison_results:

                st.success(
                    f"{len(comparison_results)} candidate records found!"
                )

                rank_badges = {
                    1: "🥇",
                    2: "🥈",
                    3: "🥉"
                }

                leaderboard = []

                for rank, candidate in enumerate(
                    comparison_results,
                    start=1
                ):

                    leaderboard.append({
                        "Rank": rank_badges.get(
                            rank,
                            f"#{rank}"
                        ),
                        "Candidate": candidate[2],
                        "Match Score": float(candidate[6] or 0),
                        "Experience": candidate[4],
                        "Education": candidate[5] or "N/A"
                    })

                leaderboard_df = pd.DataFrame(leaderboard)

                # TOP CANDIDATE

                top_candidate = comparison_results[0]

                top_name = html.escape(
                    str(top_candidate[2])
                )

                top_score = float(top_candidate[6] or 0)
                top_experience = top_candidate[4]

                st.markdown("### 🏆 Top Candidate")

                with st.container(border=True):

                    st.html(f"""
                    <div style="
                        background:linear-gradient(
                            135deg,
                            rgba(124,58,237,0.20),
                            rgba(30,41,75,0.50)
                        );
                        border:1px solid rgba(167,139,250,0.4);
                        border-radius:18px;
                        padding:22px;
                    ">

                        <div style="
                            color:#FBBF24;
                            font-size:14px;
                            font-weight:700;
                            letter-spacing:1px;
                        ">
                            🥇 TOP MATCH
                        </div>

                        <div style="
                            color:white;
                            font-size:26px;
                            font-weight:800;
                            margin-top:8px;
                        ">
                            {top_name}
                        </div>

                        <div style="
                            color:#A78BFA;
                            font-size:15px;
                            margin-top:5px;
                        ">
                            {top_score:.2f}% Compatibility
                        </div>

                    </div>
                    """)

                    top_col1, top_col2, top_col3 = st.columns(3)

                    top_col1.metric(
                        "Match Score",
                        f"{top_score:.2f}%"
                    )

                    top_col2.metric(
                        "Experience",
                        f"{top_experience} Years"
                    )

                    top_col3.metric(
                        "Candidate ID",
                        top_candidate[1]
                    )

                # LEADERBOARD

                st.markdown("### 📊 Candidate Leaderboard")

                st.dataframe(
                    leaderboard_df,
                    use_container_width=True,
                    hide_index=True
                )

                # MATCH SCORE CHART

                st.markdown(
                    "### 📈 Candidate Match Score Comparison"
                )

                score_chart_data = pd.DataFrame({
                    "Candidate": [
                        str(candidate[2])
                        for candidate in comparison_results
                    ],
                    "Match Score": [
                        float(candidate[6] or 0)
                        for candidate in comparison_results
                    ]
                })

                score_chart_data = score_chart_data.set_index(
                    "Candidate"
                )

                st.bar_chart(
                    score_chart_data,
                    y="Match Score",
                    height=350
                )

                # SKILL COMPARISON

                st.markdown("### 🧠 Candidate Skills Comparison")

                skill_chart_rows = []

                for candidate in comparison_results:

                    skill_chart_rows.append({
                        "Candidate": str(candidate[2]),
                        "Matched Skills": len(candidate[7] or []),
                        "Missing Skills": len(candidate[8] or [])
                    })

                skill_chart_data = pd.DataFrame(
                    skill_chart_rows
                ).set_index("Candidate")

                st.bar_chart(
                    skill_chart_data,
                    height=350
                )

                # CSV REPORT

                st.markdown("### 📥 Download Candidate Report")

                csv_data = leaderboard_df.to_csv(
                    index=False
                ).encode("utf-8")

                st.download_button(
                    label="⬇️ Download Candidate Ranking CSV",
                    data=csv_data,
                    file_name=(
                        f"TalentAI_Candidate_Report_"
                        f"{comparison_job[0]}.csv"
                    ),
                    mime="text/csv",
                    use_container_width=True
                )

                # CANDIDATE DETAILS

                st.markdown("### 👥 Candidate Details")

                for rank, candidate in enumerate(
                    comparison_results,
                    start=1
                ):

                    (
                        match_id,
                        candidate_id,
                        full_name,
                        email,
                        experience,
                        education,
                        match_percentage,
                        matched_skills,
                        missing_skills,
                        created_at
                    ) = candidate

                    rank_icon = rank_badges.get(
                        rank,
                        f"#{rank}"
                    )

                    with st.expander(
                        f"{rank_icon} {full_name} — "
                        f"{float(match_percentage or 0):.2f}% Match",
                        expanded=(rank == 1)
                    ):

                        col1, col2, col3 = st.columns(3)

                        col1.metric(
                            "Match Score",
                            f"{float(match_percentage or 0):.2f}%"
                        )

                        col2.metric(
                            "Experience",
                            f"{experience} Years"
                        )

                        col3.metric(
                            "Candidate ID",
                            candidate_id
                        )

                        st.write(f"**Email:** {email}")
                        st.write(f"**Education:** {education or 'N/A'}")

                        st.write("🟢 **Matched Skills**")

                        st.write(
                            ", ".join(matched_skills or [])
                            or "No matched skills"
                        )

                        st.write("🔴 **Missing Skills**")

                        st.write(
                            ", ".join(missing_skills or [])
                            or "No missing skills"
                        )

                        st.caption(
                            f"Screening Date: {created_at}"
                        )

            else:

                st.warning(
                    "No candidates have been screened for this job yet."
                )


# ==========================================
# SCREENING HISTORY PAGE
# ==========================================

elif selected_page == "Screening History":

    render_page_header(
        "Activity Center",
        "Screening History",
        "Review previously analyzed resumes, candidate match scores and skill comparisons."
    )

    recent_screenings = get_recent_screenings(limit=10) or []

    st.metric(
        "Recent Screening Records",
        len(recent_screenings)
    )

    if recent_screenings:

        history_table = []

        for screening in recent_screenings:

            history_table.append({
                "Candidate": screening[1],
                "Resume": screening[2],
                "Match Score": float(screening[3] or 0),
                "Screened On": (
                    screening[6].strftime("%d %b %Y, %I:%M %p")
                    if screening[6] else "N/A"
                )
            })

        st.markdown("### 📋 Screening Records")

        
        if history_table:

            table_headers = list(history_table[0].keys())

            header_html = "".join(
                f"<th>{html.escape(str(header))}</th>"
                for header in table_headers
            )

            rows_html = ""

            for record in history_table:

                cells_html = "".join(
                    f"<td>{html.escape(str(record.get(header, 'N/A')))}</td>"
                    for header in table_headers
                )

                rows_html += f"<tr>{cells_html}</tr>"

            st.markdown(
                f"""
                <div style="
                    width:100%;
                    overflow-x:auto;
                    border:1px solid rgba(168,85,247,0.25);
                    border-radius:14px;
                    background:#100d19;
                    padding:12px;
                ">
                    <table style="
                        width:100%;
                        border-collapse:collapse;
                        color:#eee8ff;
                        font-size:16px;
                    ">
                        <thead>
                            <tr style="
                                background:#241538;
                                color:#d8b4fe;
                                text-align:left;
                            ">
                                {header_html}
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            st.info("No screening records available yet.")


        st.markdown("### 🔍 Screening Details")

        for screening in recent_screenings:

            match_id = screening[0]
            candidate_name = screening[1]
            resume_name = screening[2]
            match_score = float(screening[3] or 0)
            matched_skills = screening[4] or []
            missing_skills = screening[5] or []
            screened_on = screening[6]

            with st.expander(
                f"👤 {candidate_name} | {match_score:.2f}% Match"
            ):

                detail_col1, detail_col2 = st.columns(2)

                detail_col1.metric(
                    "Match Score",
                    f"{match_score:.2f}%"
                )

                detail_col2.write(
                    f"**Match ID:** {match_id}"
                )

                st.write("**Resume:**", resume_name)

                st.write(
                    "**Matched Skills:**",
                    ", ".join(matched_skills) or "None"
                )

                st.write(
                    "**Missing Skills:**",
                    ", ".join(missing_skills) or "None"
                )

                st.caption(
                    screened_on.strftime("%d %b %Y, %I:%M %p")
                    if screened_on
                    else "Screening date unavailable"
                )

    else:

        st.info("No screening records found yet.")


# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        color:#64748B;
        font-size:11px;
        padding:10px;
    ">
        TALENTAI • AI-POWERED RESUME INTELLIGENCE
        <br>
        Intelligent Recruitment Workspace
    </div>
    """,
    unsafe_allow_html=True
)











































































