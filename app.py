import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
from streamlit_cookies_manager import EncryptedCookieManager

# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="Short Story Generator", page_icon="📚")

# Initialize cookie manager
cookies = EncryptedCookieManager(
    prefix="auth_",  # prefix for all cookies
    password=os.getenv("COOKIE_SECRET")  # use a secret from env
)
if not cookies.ready():
    st.stop()  # Wait until cookies are ready
    
# Check if already authenticated via cookie
if cookies.get("authenticated") == "true":
    st.session_state.authenticated = True

CORRECT_PASSCODE = os.getenv("APP_PASSCODE")
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("## 🔐 Authentication")
    with st.form("passcode_form"):
        passcode_input = st.text_input("Passcode", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if passcode_input == CORRECT_PASSCODE:
                st.session_state.authenticated = True
                cookies["authenticated"] = "true"
                cookies.save()
                st.success("✅ Access granted!")
                st.rerun()  # Reload to show app
            else:
                st.error("❌ Incorrect passcode. Try again.")
    st.stop()
    
# Configure Google Gemini API
try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    st.error(f"Error configuring Gemini API. : {e}")
    st.stop() # Stop the app if API key is not configured
    
def generate_short_story(story_text):
    prompt = f"""
        You are a Hindi children's storyteller and scriptwriter.

        Your task is to summarize the given Hindi story into a **short version of no more than 140 words**, written in **pure plain Hindi**. This short version should be suitable for **YouTube Shorts** — designed to fit a video length of 50 seconds or less.

        **Rules:**
        - Do NOT include any title or heading.
        - Do NOT write any introduction or explanation.
        - Do NOT use bold formatting like **text** or symbols like * or #.
        - Write in a **natural storytelling tone**, suitable for voice-over.
        - Maintain the emotional and moral impact of the original story.

        Now rewrite the following story:

        {story_text}
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="text/plain",
            )
        )
        data = response.text.strip()
        return data
    except Exception as e:
        st.error(f"Error in Generate Context : {str(e)}")

# Streamlit UI
st.markdown("<h3 style='text-align: center;'>Short Story Generator</h3>", unsafe_allow_html=True)

story_input = st.text_area("✍️ Enter full Hindi story:", height=300)

if st.button("🧠 Generate Short Story"):
    if story_input.strip():
        with st.spinner("Generating short story ..."):
            try:
                short_story_text = generate_short_story(story_input)
                st.success("✅ Short story generated!")
                st.code(short_story_text, language="markdown")
            except Exception as e:
                st.error(f"❌ Failed to generate short story: {str(e)}")
    else:
        st.warning("❌ Please enter a full story first.")