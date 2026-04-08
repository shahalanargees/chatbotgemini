import os
import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()


def get_api_key():
    try:
        # Try Streamlit secrets (for deployment)
        return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        # Fallback to .env (for local)
        return os.getenv("GOOGLE_API_KEY")

GOOGLE_API_KEY = get_api_key()

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY not found. Add it in .env or secrets.toml")
    st.stop()


st.set_page_config(
    page_title="Gemini AI Chatbot",
    page_icon="🤖"
)

client = genai.Client(api_key=GOOGLE_API_KEY)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


st.title("🤖 Gemini AI Chatbot")
st.caption("Powered by Gemini 2.0 Flash")


for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])



user_prompt = st.chat_input("Ask me anything...")

if user_prompt:
    # Save user message
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_prompt
    })

    st.chat_message("user").markdown(user_prompt)

    # Limit history (performance safe)
    st.session_state.chat_history = st.session_state.chat_history[-6:]

    try:
        with st.spinner("🤔 Thinking..."):

            # Convert to Gemini format
            contents = []
            for msg in st.session_state.chat_history:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })

            # Generate response
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contents
            )

            
            reply = ""
            try:
                reply = response.candidates[0].content.parts[0].text
            except Exception:
                reply = "⚠️ No response generated."

        # Show assistant reply
        st.chat_message("assistant").markdown(reply)

        # Save assistant reply
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": reply
        })

    except Exception as e:
        error_msg = str(e)

        if "429" in error_msg:
            st.warning("⚠️ Rate limit reached. Please wait and try again.")
        else:
            st.error(f"❌ Error: {error_msg}")


with st.sidebar:
    st.header("⚙️ Settings")

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    st.markdown("**Model:** gemini-2.0-flash")
    st.markdown("**Status:** 🟢 Running")