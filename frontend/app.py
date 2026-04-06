import streamlit as st
import requests

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="RB-PLPE · Learning Pathway Engine",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════
#  GLOBAL CSS  — Dark editorial theme with amber accents
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Darker Input Fields (Black Background) ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-baseweb="select"] > div,
[data-baseweb="input"] {
    background: #0f0f17 !important;           /* True deep black */
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 2px !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.2s ease !important;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-baseweb="select"] > div:focus-within {
    background: #0a0a0f !important;           /* Even darker on focus */
    border-color: #f59e0b !important;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.12) !important;
    outline: none !important;
}

/* Placeholder text */
[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: #4a4540 !important;
    font-style: italic;
}

/* Selectbox improvement */
[data-baseweb="select"] > div {
    background: #0f0f17 !important;
}

[data-baseweb="select"] > div:hover {
    border-color: rgba(245,158,11,0.4) !important;
}

/* Keep the rest of your beautiful styling unchanged */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(251,191,36,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(251,191,36,0.04) 0%, transparent 60%),
        #0a0a0f !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] { display: none !important; }

/* ── Main container ── */
.block-container {
    max-width: 760px !important;
    padding: 3rem 2rem 6rem !important;
}

/* Hero, Divider, Section labels, Auth card, etc. — all your existing styles remain the same */
.hero { text-align: center; padding: 3.5rem 0 2rem; position: relative; }
.hero-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    color: #f59e0b;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    opacity: 0.9;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(3.5rem, 10vw, 6rem);
    line-height: 0.95;
    letter-spacing: 0.02em;
    color: #f5f0e8;
    margin-bottom: 0.5rem;
}
.hero-title span { color: #f59e0b; }
.hero-sub {
    font-size: 0.95rem;
    font-weight: 300;
    color: #8a8070;
    letter-spacing: 0.03em;
    margin-top: 1rem;
}

.rule {
    border: none;
    border-top: 1px solid rgba(245,158,11,0.15);
    margin: 2.5rem 0;
}

.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: #f59e0b;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(245,158,11,0.2);
}

/* Auth card */
.auth-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 2px;
    padding: 2rem;
    backdrop-filter: blur(10px);
}

/* Labels */
[data-testid="stTextInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
[data-baseweb="select"] label,
.stRadio label,
.stSlider label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    color: #a09880 !important;
    text-transform: uppercase !important;
    margin-bottom: 0.4rem !important;
}

/* Buttons, Tabs, Metrics, etc. — keeping all your original styles */
.stButton > button, [data-testid="stFormSubmitButton"] > button {
    background: #f59e0b !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.1em !important;
    padding: 0.75rem 2rem !important;
    width: 100%;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
    background: #fbbf24 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(245,158,11,0.25) !important;
}

/* All other styles (Radio, Slider, Tabs, Alerts, Metrics, Expanders, etc.) remain unchanged */
.stRadio [aria-checked="true"] [data-baseweb="radio"] div {
    border-color: #f59e0b !important;
    background: #f59e0b !important;
}

[data-testid="stAlert"] {
    border-radius: 2px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stSuccess { background: rgba(16,185,129,0.08) !important; border-left: 3px solid #10b981 !important; color: #6ee7b7 !important; }
.stError { background: rgba(239,68,68,0.08) !important; border-left: 3px solid #ef4444 !important; color: #fca5a5 !important; }
.stInfo { background: rgba(245,158,11,0.06) !important; border-left: 3px solid #f59e0b !important; color: #fcd34d !important; }

</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════
API = "http://localhost:8000"

JOB_ROLES = [
    "Select a role...",
    "Data Scientist", "Machine Learning Engineer", "Data Analyst",
    "Data Engineer", "AI Engineer", "Business Intelligence Analyst",
    "NLP Engineer", "Computer Vision Engineer",
    "Software Engineer", "Frontend Developer", "Backend Developer",
    "Full Stack Developer", "Android Developer", "iOS Developer",
    "Mobile App Developer", "DevOps Engineer", "Cloud Engineer",
    "Cybersecurity Analyst", "Database Administrator", "QA Engineer",
    "Network Engineer", "System Administrator", "UI/UX Designer",
    "Business Analyst", "Solutions Architect", "Tech Lead",
    "Embedded Systems Engineer", "Blockchain Developer",
]

# ══════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════
if "user_id"   not in st.session_state: st.session_state.user_id   = None
if "user_name" not in st.session_state: st.session_state.user_name = None

# ══════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Role-Based Personalised Learning Pathway Engine</div>
    <div class="hero-title">RB<span>·</span>PLPE</div>
    <div class="hero-sub">Map your skills. Find your gaps. Build your career.</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="rule">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  STEP 1 — AUTH
# ══════════════════════════════════════════════════════════════
if st.session_state.user_id is None:

    st.markdown('<div class="section-label">01 — Identify yourself</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["New user", "Returning user"])

    # ── Register ──
    with tab1:
        with st.form("register_form"):
            name  = st.text_input("Full name",  placeholder="Hamant Jagwan")
            email = st.text_input("Email address", placeholder="hamant@gmail.com")
            st.markdown("<br>", unsafe_allow_html=True)
            register_btn = st.form_submit_button("Create account →", use_container_width=True)

        if register_btn:
            if not name.strip() or not email.strip():
                st.error("Enter both your name and email to continue.")
            else:
                resp = requests.post(f"{API}/api/v1/register",
                                     json={"name": name.strip(), "email": email.strip().lower()})
                if resp.status_code == 200:
                    d = resp.json()
                    st.session_state.user_id   = d["id"]
                    st.session_state.user_name = d["name"]
                    st.rerun()
                elif resp.status_code == 400:
                    st.error("That email is already registered — use the Returning user tab.")
                else:
                    st.error(f"Server error: {resp.text}")

    # ── Login ──
    with tab2:
        with st.form("login_form"):
            login_email = st.text_input("Email address", placeholder="hamant@gmail.com")
            st.markdown("<br>", unsafe_allow_html=True)
            login_btn = st.form_submit_button("Continue →", use_container_width=True)

        if login_btn:
            if not login_email.strip():
                st.error("Enter your email to continue.")
            else:
                resp = requests.post(f"{API}/api/v1/login",
                                     json={"name": "", "email": login_email.strip().lower()})
                if resp.status_code == 200:
                    d = resp.json()
                    st.session_state.user_id   = d["id"]
                    st.session_state.user_name = d["name"]
                    st.rerun()
                elif resp.status_code == 404:
                    st.error("No account found for that email — register first.")
                else:
                    st.error(f"Server error: {resp.text}")

# ══════════════════════════════════════════════════════════════
#  STEP 2 — PATHWAY FORM
# ══════════════════════════════════════════════════════════════
else:
    # Welcome bar
    st.markdown(f"""
    <div class="welcome-bar">
        <div>
            <div class="welcome-bar-name">👋 {st.session_state.user_name}</div>
            <div class="welcome-bar-id">UID · {st.session_state.user_id:04d}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("↩ Switch account"):
        st.session_state.user_id   = None
        st.session_state.user_name = None
        st.rerun()

    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">02 — Define your pathway</div>', unsafe_allow_html=True)

    with st.form("pathway_form"):

        current_skills = st.text_area(
            "Skills you already have",
            placeholder="Python, SQL, Pandas, statistics, Excel  —  separate with commas",
            height=110,
        )

        target_role = st.selectbox("Target role", options=JOB_ROLES)

        st.markdown("<br>", unsafe_allow_html=True)

        experience = st.radio(
            "Experience level",
            options=["Fresher (0–1 yrs)", "Mid-level (1–3 yrs)", "Senior (3+ yrs)"],
            horizontal=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        hours_per_week = st.slider(
            "Learning hours per week",
            min_value=1, max_value=40, value=5, step=1,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Generate pathway →", use_container_width=True)

    # ── On submit ──
    if submitted:
        if not current_skills.strip():
            st.error("List at least one skill you have.")
        elif target_role == "Select a role...":
            st.error("Select a target role to continue.")
        else:
            skills_list = [s.strip().lower() for s in current_skills.split(",") if s.strip()]

            payload = {
                "user_id"       : st.session_state.user_id,
                "skills"        : skills_list,
                "target_role"   : target_role,
                "experience"    : experience,
                "hours_per_week": hours_per_week,
            }

            with st.spinner("Analysing your profile…"):
                resp = requests.post(f"{API}/api/v1/generate-pathway", json=payload)

            if resp.status_code == 200:
                result = resp.json()

                st.markdown('<hr class="rule">', unsafe_allow_html=True)
                st.markdown('<div class="section-label">03 — Your results</div>', unsafe_allow_html=True)

                # ── Metrics ──
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Role",    result["target_role"])
                c2.metric("Gap",     f"{round(result['gap_score'] * 100)}%")
                c3.metric("Weeks",   f"{result['estimated_weeks']}")
                c4.metric("Courses", f"{len(result['pathway'])}")

                # ── Missing skills ──
                if result["missing_skills"]:
                    st.markdown('<hr class="rule">', unsafe_allow_html=True)
                    st.markdown('<div class="section-label">Skills to acquire</div>', unsafe_allow_html=True)
                    tags_html = "".join(
                        f'<span class="skill-tag missing">{s}</span>'
                        for s in result["missing_skills"]
                    )
                    st.markdown(f'<div style="line-height:2.2">{tags_html}</div>',
                                unsafe_allow_html=True)

                # ── Pathway ──
                if result["pathway"]:
                    st.markdown('<hr class="rule">', unsafe_allow_html=True)
                    st.markdown('<div class="section-label">Learning pathway</div>', unsafe_allow_html=True)

                    for course in result["pathway"]:
                        with st.expander(
                            f"{'─' * 2}  {course['rank']:02d}  ·  {course['course_title']}"
                        ):
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Rating",     course["rating"])
                            m2.metric("Difficulty", course["difficulty"])
                            m3.metric("Duration",   f"{course['duration_hrs']} hrs")

                            st.markdown("<br>", unsafe_allow_html=True)

                            skill_tag = f'<span class="skill-tag">{course["covers_skill"]}</span>'
                            st.markdown(
                                f"**Targets skill** {skill_tag}",
                                unsafe_allow_html=True,
                            )
                            st.markdown(f"**Platform** · {course.get('platform', 'Online')}")
                            st.markdown(f"**Covers** · {course['skills']}")
                            st.markdown(f"[Open course →]({course['course_url']})")
                else:
                    st.info("No courses matched your missing skills — try broadening your target role.")

            else:
                st.error(f"Error {resp.status_code} — {resp.json().get('detail', 'Unknown error')}")