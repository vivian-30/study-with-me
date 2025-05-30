import streamlit as st
import os
from dotenv import load_dotenv
import openai
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# OpenRouter setup
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENROUTER_API_KEY")

# Streamlit page config
st.set_page_config(page_title="AI Study App", layout="centered")

# Custom styles
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter&display=swap" rel="stylesheet">
<style>
body {
    font-family: 'Inter', sans-serif;
}
.aistudybuddy {
    color: #0000ff;
    font-size: 64px;
    font-family: 'Inter', sans-serif;
    text-align: center;
    filter: drop-shadow(6px 6px 8px rgba(0,0,0,0.25));
    margin-top: 30px;
    margin-bottom: 30px;
}
.wireframe-1 {
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 30px;
    padding: 40px;
    box-shadow: 0px 4px 20px rgba(0, 0, 0, 0.15);
    width: 90%;
    max-width: 800px;
    margin: 0 auto;
}
.stTextInput > div > input {
    font-size: 16px;
    padding: 10px;
}
.stButton > button {
    background-color: #0000ff;
    color: white;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 16px;
    transition: all 0.2s ease-in-out;
}
.stButton > button:hover {
    background-color: #3333ff;
}
</style>
""", unsafe_allow_html=True)

# Dark mode toggle
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

mode_toggle = st.checkbox("🌗 Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = mode_toggle

if mode_toggle:
    st.markdown("""
    <style>
    body { background-color: #121212; color: white; }
    .stTextInput > div > input { background-color: #333; color: white; }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown('<div class="aistudybuddy">📚 AI Study Buddy</div>', unsafe_allow_html=True)

# Session state setup
if "user" not in st.session_state:
    st.session_state.user = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Auth functions
def login(email, password):
    try:
        result = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = result.user
        st.success("✅ Logged in successfully.")
    except Exception as e:
        st.error("❌ Login failed: " + str(e))

def register(email, password):
    try:
        result = supabase.auth.sign_up({"email": email, "password": password})
        st.success("✅ Registration successful! Please log in.")
    except Exception as e:
        st.error("❌ Registration failed: " + str(e))

def chat_with_ai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI study assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

# UI - Auth
if not st.session_state.user:
    st.markdown('<div class="wireframe-1">', unsafe_allow_html=True)

    st.subheader("🔐 Login or Register")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            login(email, password)
    with col2:
        if st.button("Register"):
            register(email, password)

    st.markdown('</div>', unsafe_allow_html=True)

# UI - Main Chat
else:
    st.markdown(f"""
    <div style='display: flex; align-items: center; gap: 15px; margin-bottom: 20px;'>
        <img src="https://api.dicebear.com/7.x/initials/svg?seed={st.session_state.user.email}" width="60" style="border-radius: 50%; border: 2px solid #0000ff;" />
        <div style="font-size: 18px;">✅ Logged in as <strong>{st.session_state.user.email}</strong></div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("💬 Ask a Study Question")
    user_input = st.text_area("Enter your question")

    if st.button("Ask"):
        with st.spinner("🤖 Thinking..."):
            answer = chat_with_ai(user_input)
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("AI", answer))
            st.markdown("### 💡 AI Answer:")
            st.write(answer)

    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### 🕘 Previous Q&A:")
        for role, msg in st.session_state.chat_history:
            st.markdown(f"**{role}:** {msg}")

    if st.button("Log out"):
        st.session_state.user = None
        st.session_state.chat_history = []
