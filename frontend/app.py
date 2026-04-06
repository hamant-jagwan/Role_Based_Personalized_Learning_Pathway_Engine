import streamlit as st
import requests

# ── Page config ──
st.set_page_config(
    page_title="RB-PLPE",
    page_icon="🎯",
    layout="centered"
)

# ── Title ──
st.title("🎯 RB-PLPE")
st.subheader("Role-Based Personalised Learning Pathway Engine")
st.markdown("---")

# ── Base URL ──
API = "http://localhost:8000"

# ── Job roles list — all 27 IT roles ──
JOB_ROLES = [
    "Select a role...",
    # Data & AI
    "Data Scientist",
    "Machine Learning Engineer",
    "Data Analyst",
    "Data Engineer",
    "AI Engineer",
    "Business Intelligence Analyst",
    "NLP Engineer",
    "Computer Vision Engineer",
    # Web & Software
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    # Mobile
    "Android Developer",
    "iOS Developer",
    "Mobile App Developer",
    # DevOps & Cloud
    "DevOps Engineer",
    "Cloud Engineer",
    # Security
    "Cybersecurity Analyst",
    # Database
    "Database Administrator",
    # QA
    "QA Engineer",
    # Network & Systems
    "Network Engineer",
    "System Administrator",
    # Design & Other IT
    "UI/UX Designer",
    "Business Analyst",
    "Solutions Architect",
    "Tech Lead",
    "Embedded Systems Engineer",
    "Blockchain Developer",
]

# ════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None


# ════════════════════════════════════════════
# STEP 1 — Register
# ════════════════════════════════════════════
if st.session_state.user_id is None:

    st.markdown("### 👤 Step 1 — Register or Login")

    tab1, tab2 = st.tabs(["New User — Register", "Existing User — Login"])

    # ── Register tab ──
    with tab1:
        with st.form("register_form"):
            name  = st.text_input("Your Name",  placeholder="e.g. Hamant Jagwan")
            email = st.text_input("Your Email", placeholder="e.g. hamant@gmail.com")
            register_btn = st.form_submit_button("Register & Continue", use_container_width=True)

        if register_btn:
            if not name.strip() or not email.strip():
                st.error("⚠️ Please enter both name and email.")
            else:
                response = requests.post(
                    f"{API}/api/v1/register",
                    json={"name": name.strip(), "email": email.strip()}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.user_id   = data["id"]
                    st.session_state.user_name = data["name"]
                    st.success(f"✅ Welcome {data['name']}!")
                    st.rerun()
                elif response.status_code == 400:
                    st.error("❌ Email already registered. Please use the Login tab.")
                else:
                    st.error(f"❌ Something went wrong: {response.text}")

    # ── Login tab ──
    with tab2:
        with st.form("login_form"):
            login_email = st.text_input("Your Email", placeholder="e.g. hamant@gmail.com")
            login_btn   = st.form_submit_button("Login & Continue", use_container_width=True)

        if login_btn:
            if not login_email.strip():
                st.error("⚠️ Please enter your email.")
            else:
                response = requests.get(
                    f"{API}/api/v1/login",
                    params={"email": login_email.strip()}
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.user_id   = data["id"]
                    st.session_state.user_name = data["name"]
                    st.success(f"✅ Welcome back {data['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Email not found. Please register first.")


# ════════════════════════════════════════════
# STEP 2 — Pathway Form
# ════════════════════════════════════════════
else:
    st.success(f"👋 Welcome, {st.session_state.user_name}! (User ID: {st.session_state.user_id})")

    if st.button("Switch User"):
        st.session_state.user_id   = None
        st.session_state.user_name = None
        st.rerun()

    st.markdown("---")
    st.markdown("### 📝 Step 2 — Generate Your Learning Pathway")

    with st.form("pathway_form"):

        # 1. Current skills
        current_skills = st.text_area(
            label="What skills do you currently have?",
            placeholder="e.g. Python, SQL, Pandas, basic statistics, Excel",
            height=100,
            help="Enter your skills separated by commas"
        )

        # 2. Target role
        target_role = st.selectbox(
            label="Which job role are you targeting?",
            options=JOB_ROLES
        )

        # 3. Experience level
        experience = st.radio(
            label="Your current experience level",
            options=["Fresher (0-1 years)", "Mid-level (1-3 years)", "Senior (3+ years)"],
            horizontal=True
        )

        # 4. Hours per week
        hours_per_week = st.slider(
            label="How many hours per week can you dedicate to learning?",
            min_value=1,
            max_value=40,
            value=5,
            step=1
        )

        st.markdown("---")
        submitted = st.form_submit_button("🚀 Generate My Learning Pathway", use_container_width=True)

    # ── On Submit ──
    if submitted:

        if not current_skills.strip():
            st.error("⚠️ Please enter at least one skill.")
        elif target_role == "Select a role...":
            st.error("⚠️ Please select a target job role.")
        else:
            skills_list = [s.strip().lower() for s in current_skills.split(",") if s.strip()]

            payload = {
                "user_id"       : st.session_state.user_id,
                "skills"        : skills_list,
                "target_role"   : target_role,
                "experience"    : experience,
                "hours_per_week": hours_per_week
            }

            with st.spinner("⏳ Generating your pathway..."):
                response = requests.post(
                    f"{API}/api/v1/generate-pathway",
                    json=payload
                )

            if response.status_code == 200:
                result = response.json()
                st.success("✅ Pathway generated and saved to database!")

                # ── Summary metrics ──
                st.markdown("### 📊 Your Results")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Target Role",     result["target_role"])
                col2.metric("Gap Score",       f"{round(result['gap_score'] * 100)}%")
                col3.metric("Est. Weeks",      f"{result['estimated_weeks']} weeks")
                col4.metric("Courses",         f"{len(result['pathway'])} courses")

                st.markdown("---")

                # ── Missing skills ──
                if result["missing_skills"]:
                    st.markdown("### 🔍 Missing Skills")
                    cols = st.columns(4)
                    for i, skill in enumerate(result["missing_skills"]):
                        cols[i % 4].markdown(f"❌ `{skill}`")

                st.markdown("---")

                # ── Learning pathway ──
                if result["pathway"]:
                    st.markdown("### 🗺️ Your Learning Pathway")
                    for course in result["pathway"]:
                        with st.expander(f"📚 Course {course['rank']} — {course['course_title']}"):
                            c1, c2, c3 = st.columns(3)
                            c1.metric("Rating",     course["rating"])
                            c2.metric("Difficulty", course["difficulty"])
                            c3.metric("Duration",   f"{course['duration_hrs']} hrs")

                            st.markdown(f"**Covers skill:** `{course['covers_skill']}`")
                            st.markdown(f"**Platform:** {course.get('platform', 'Online')}")
                            st.markdown(f"**Skills taught:** {course['skills']}")
                            st.markdown(f"[🔗 Open Course]({course['course_url']})")
                else:
                    st.info("🔧 No courses found for these missing skills.")

            else:
                st.error(f"❌ Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")