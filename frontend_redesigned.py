import os
import requests
import streamlit as st

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="InsureAI | Premium Predictor",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
PREDICT_URL = f"{API_BASE_URL}/predict"
ASSISTANT_URL = f"{API_BASE_URL}/assistant"
REGISTER_URL = f"{API_BASE_URL}/auth/register"
LOGIN_URL = f"{API_BASE_URL}/auth/login"

# -------------------- STYLE --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --bg:#0a0f1e; --panel:#111a2e; --panel2:#151f36; --line:rgba(148,163,184,.17); --muted:#94a3b8; --text:#f1f5f9; --purple:#9b8cff; --cyan:#67e8f9; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: radial-gradient(ellipse at 12% 0%, rgba(92,70,190,.20), transparent 34%), radial-gradient(ellipse at 90% 8%, rgba(34,211,238,.09), transparent 27%), var(--bg); color:var(--text); }
[data-testid="stHeader"] { background:rgba(10,15,30,.65); }
.block-container { max-width:1240px; padding-top:2.1rem; padding-bottom:3rem; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.035em; color:#f8fafc; }
h1 { font-size:2.25rem !important; font-weight:800 !important; }
p, label, .stCaption { color:#cbd5e1; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#10172a,#0c1221); border-right:1px solid var(--line); }
[data-testid="stSidebar"] .block-container { padding-top:2rem; }
div[data-testid="stVerticalBlockBorderWrapper"], .glass-card { background:linear-gradient(145deg,rgba(21,31,54,.92),rgba(15,23,42,.88)); border:1px solid var(--line); border-radius:20px; padding:1.2rem; box-shadow:0 16px 45px rgba(0,0,0,.16); }
div[data-testid="stMetric"] { background:linear-gradient(135deg,rgba(139,92,246,.15),rgba(34,211,238,.07)); border:1px solid rgba(167,139,250,.24); padding:1rem 1.1rem; border-radius:16px; }
[data-testid="stMetricLabel"] { color:#a5b4fc !important; }
[data-testid="stMetricValue"] { color:#f8fafc !important; font-family:'Manrope',sans-serif; }
.stButton > button, [data-testid="stFormSubmitButton"] button { border:0; border-radius:12px; padding:.65rem 1rem; font-weight:700; color:#0b1020; background:linear-gradient(100deg,#a78bfa,#67e8f9); transition:transform .15s ease,filter .15s ease; }
.stButton > button:hover, [data-testid="stFormSubmitButton"] button:hover { filter:brightness(1.08); transform:translateY(-1px); color:#0b1020; border:0; }
.stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] > div, [data-testid="stChatInput"] textarea { background:#0b1325 !important; color:#f8fafc !important; border-color:#2b3854 !important; border-radius:11px !important; }
[data-testid="stChatMessage"] { background:rgba(21,31,54,.72); border:1px solid var(--line); border-radius:16px; }
hr { border-color:var(--line); }
.eyebrow { color:#a5b4fc; text-transform:uppercase; letter-spacing:.16em; font-size:.73rem; font-weight:800; }
.hero { background:linear-gradient(115deg,rgba(124,92,246,.22),rgba(34,211,238,.08)),#111a2e; border:1px solid rgba(167,139,250,.28); border-radius:24px; padding:1.65rem 1.8rem; margin-bottom:1.4rem; }
.hero-title { font-family:'Manrope',sans-serif; font-size:2rem; font-weight:800; line-height:1.2; margin:.35rem 0 .55rem; color:#fff; }
.hero-sub { color:#aab8ce; max-width:720px; }
.small-note { color:#94a3b8; font-size:.85rem; }
.auth-wrap { max-width:560px; margin:2rem auto; }
.badge { display:inline-block; border:1px solid rgba(167,139,250,.35); background:rgba(139,92,246,.12); color:#c4b5fd; border-radius:999px; padding:.35rem .7rem; font-size:.78rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# -------------------- SESSION STATE --------------------
defaults = {
    "authenticated": False,
    "access_token": None,
    "auth_user": None,
    "auth_mode": "Login",
    "predicted_premium": None,
    "customer_data": None,
    "messages": [],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def response_detail(response):
    try:
        payload = response.json()
        return payload.get("detail", payload.get("message", response.text))
    except (ValueError, AttributeError):
        return getattr(response, "text", "Unknown error")


# -------------------- AUTH PAGE --------------------
def show_auth_page():
    st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="hero"><div class="eyebrow">✦ INSUREAI · SMARTER ESTIMATES</div><div class="hero-title">Understand your insurance premium.</div><div class="hero-sub">A simple, AI-assisted way to explore an estimated medical insurance cost based on your profile.</div><br><span class="badge">Machine learning · Personalised insights</span></div>', unsafe_allow_html=True)
    mode = st.radio("Welcome", ["Login", "Sign Up"], horizontal=True,
                    index=0 if st.session_state.auth_mode == "Login" else 1,
                    label_visibility="collapsed")
    st.session_state.auth_mode = mode

    if mode == "Sign Up":
        with st.form("signup_form", clear_on_submit=False):
            username = st.text_input("Username", max_chars=100, placeholder="How should we call you?")
            email = st.text_input("Email address", placeholder="you@example.com")
            password = st.text_input("Password (minimum 8 characters)", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create account  →", use_container_width=True)
        if submitted:
            if not username.strip() or not email.strip() or not password:
                st.error("Please complete all fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters long.")
            else:
                try:
                    response = requests.post(
                        REGISTER_URL,
                        json={"username": username.strip(), "email": email.strip(), "password": password},
                        timeout=25,
                    )
                    if response.status_code in (200, 201):
                        payload = response.json()
                        token = payload.get("access_token")
                        if token:
                            st.session_state.authenticated = True
                            st.session_state.access_token = token
                            st.session_state.auth_user = payload.get("user", {"username": username.strip(), "email": email.strip()})
                            st.success("Account created successfully!")
                            st.rerun()
                        else:
                            st.success("Account created. Please log in.")
                            st.session_state.auth_mode = "Login"
                            st.rerun()
                    else:
                        st.error(f"Sign up failed: {response_detail(response)}")
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the backend. Start FastAPI and try again.")
    else:
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email address", placeholder="you@example.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login securely  →", use_container_width=True)
        if submitted:
            if not email.strip() or not password:
                st.error("Enter your email and password.")
            else:
                try:
                    response = requests.post(
                        LOGIN_URL, json={"email": email.strip(), "password": password}, timeout=25
                    )
                    if response.status_code == 200:
                        payload = response.json()
                        st.session_state.authenticated = True
                        st.session_state.access_token = payload.get("access_token")
                        st.session_state.auth_user = payload.get("user", {"email": email.strip()})
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(f"Login failed: {response_detail(response)}")
                except requests.exceptions.RequestException:
                    st.error("Could not connect to the backend. Start FastAPI and try again.")
    st.markdown('<p class="small-note" style="text-align:center">Your estimate is informational only and is not a quote or guarantee of coverage.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# -------------------- AUTH GATE --------------------
if not st.session_state.authenticated:
    show_auth_page()
    st.stop()

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown('<div class="eyebrow">✦ INSUREAI</div>', unsafe_allow_html=True)
    st.markdown("## Premium Predictor")
    st.caption("AI-assisted insurance insights")
    st.divider()
    user = st.session_state.auth_user or {}
    st.markdown("**Signed in as**")
    st.write(user.get("username", "User"))
    st.caption(user.get("email", ""))
    st.divider()
    st.markdown("**Your workspace**")
    st.markdown("🧮  Premium estimate")
    st.markdown("🤖  AI insurance assistant")
    st.markdown("<br><span class='small-note'>Built with machine learning + Gemini</span>", unsafe_allow_html=True)
    if st.button("Log out", use_container_width=True):
        for key in defaults:
            st.session_state[key] = defaults[key]
        st.session_state.auth_mode = "Login"
        st.rerun()

# -------------------- DASHBOARD --------------------
user = st.session_state.auth_user or {}
st.markdown('<div class="eyebrow">YOUR INSURANCE WORKSPACE</div>', unsafe_allow_html=True)
st.markdown(f'<div class="hero"><div class="hero-title">Welcome back, {user.get("username", "there")} 👋</div><div class="hero-sub">Explore an estimated premium and ask the AI assistant to explain the factors behind your result.</div></div>', unsafe_allow_html=True)

tab_predict, tab_assistant = st.tabs(["✦  Premium Predictor", "◉  AI Assistant"])

with tab_predict:
    st.markdown("### Customer profile")
    st.caption("Enter the details below to generate a machine-learning estimate.")
    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age", min_value=1, max_value=119, value=30)
            sex = st.selectbox("Gender", ["male", "female"])
        with col2:
            bmi = st.number_input("BMI", min_value=10.0, max_value=60.0, value=25.0, step=0.1, format="%.1f")
            smoker = st.selectbox("Smoking status", ["no", "yes"])
        with col3:
            children = st.number_input("Number of children", min_value=0, max_value=10, value=0)
            region = st.selectbox("Region", ["southwest", "southeast", "northwest", "northeast"])

        submitted = st.button("✦  Calculate estimated premium", use_container_width=True)

    if submitted:
        input_data = {"age": age, "bmi": bmi, "smoker": smoker, "region": region, "children": children, "sex": sex}
        try:
            response = requests.post(PREDICT_URL, json=input_data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                prediction = result["response"]
                predicted_premium = float(prediction["predicted_premium"])
                st.session_state.predicted_premium = predicted_premium
                st.session_state.customer_data = input_data.copy()
                st.session_state.messages = []
                st.success("Prediction generated successfully.")
            else:
                st.error(f"Prediction failed ({response.status_code}): {response_detail(response)}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to FastAPI: {e}")

    if st.session_state.predicted_premium is not None:
        st.markdown("### Your estimate")
        metric_col, info_col = st.columns([1.15, 1])
        with metric_col:
            st.metric("Predicted annual premium", f"₹ {st.session_state.predicted_premium:,.2f}")
            st.markdown('<p class="small-note">This is a model-generated estimate, not a guaranteed insurer quote.</p>', unsafe_allow_html=True)
        with info_col:
            customer = st.session_state.customer_data or {}
            st.markdown('<div class="glass-card"><div class="eyebrow">PROFILE SUMMARY</div>', unsafe_allow_html=True)
            st.markdown(f"**{customer.get('age', '—')} years** · {customer.get('sex', '—').title()}  ")
            st.write(f"BMI: {customer.get('bmi', '—')}  ·  Smoker: {customer.get('smoker', '—').title()}")
            st.write(f"Children: {customer.get('children', '—')}  ·  Region: {customer.get('region', '—').title()}")
            st.markdown("</div>", unsafe_allow_html=True)
        st.info("Want to understand what may influence this estimate? Open the **AI Assistant** tab and ask a question.")

with tab_assistant:
    st.markdown("### Your AI insurance assistant")
    st.caption("Ask questions about your current premium estimate and customer profile.")
    if st.session_state.predicted_premium is None or not st.session_state.customer_data:
        st.markdown('<div class="glass-card"><div class="eyebrow">GET STARTED</div><h3>Generate a premium estimate first</h3><p class="small-note">Once you have a prediction, you can ask the assistant to explain it.</p></div>', unsafe_allow_html=True)
    else:
        suggested = st.columns(3)
        suggestions = [
            "Why is my predicted premium high?",
            "How does smoking affect the estimate?",
            "Explain BMI in simple terms.",
        ]
        for col, suggestion in zip(suggested, suggestions):
            with col:
                if st.button(suggestion, use_container_width=True):
                    st.session_state.pending_question = suggestion

        if "pending_question" not in st.session_state:
            st.session_state.pending_question = ""

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        question = st.chat_input("Ask about your insurance estimate...")
        if not question and st.session_state.pending_question:
            question = st.session_state.pending_question
            st.session_state.pending_question = ""

        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            customer = st.session_state.customer_data
            assistant_data = {
                "question": question,
                "predicted_premium": st.session_state.predicted_premium,
                "age": customer["age"],
                "bmi": customer["bmi"],
                "smoker": customer["smoker"],
                "region": customer["region"],
                "children": customer["children"],
                "sex": customer["sex"],
            }
            with st.chat_message("assistant"):
                with st.spinner("Thinking through your estimate..."):
                    try:
                        response = requests.post(ASSISTANT_URL, json=assistant_data, timeout=90)
                        if response.status_code == 200:
                            answer = response.json().get("answer", "The assistant returned an empty response.")
                            st.markdown(answer)
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                        else:
                            st.error(f"Assistant unavailable ({response.status_code}): {response_detail(response)}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Could not connect to the AI assistant: {e}")

st.divider()
st.markdown('<p class="small-note" style="text-align:center">InsureAI · Machine-learning estimates are for informational purposes only.</p>', unsafe_allow_html=True)
