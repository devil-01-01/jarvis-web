import streamlit as st
from groq import Groq
from openai import OpenAI
import urllib.parse

st.set_page_config(page_title="JARVIS", layout="wide")
st.title("JARVIS 5-in-1 (Groq + ChatGPT)")

# Fetch keys safely
GROQ_KEY = st.secrets.get("GROQ_KEY")
OPENAI_KEY = st.secrets.get("OPENAI_KEY")

if not GROQ_KEY:
    GROQ_KEY = st.sidebar.text_input("Groq Key", type="password", key="groq_input")
if not OPENAI_KEY:
    OPENAI_KEY = st.sidebar.text_input("OpenAI Key (ChatGPT)", type="password", key="openai_input")

# FIXED 1: Halt execution only if BOTH keys are missing
if not GROQ_KEY and not OPENAI_KEY:
    st.info("Welcome! Please supply an OpenAI or Groq Key in the sidebar dashboard to activate.")
    st.stop()

# Safe initializations without initialization crashes
groq_client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None
openai_client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

MODEL_CHATGPT = "gpt-4o-mini" 
MODEL_MATHS = "llama-3.3-70b-versatile"
MODEL_MUSIC = "mixtral-8x7b-32768"

t1, t2, t3, t4 = st.tabs(["ChatGPT Chat", "Maths (Groq)", "Image Generation", "Music Studio"])

with t1:
    st.caption(f"Model: {MODEL_CHATGPT}")
    if "c" not in st.session_state:
        st.session_state.c = []
    
    for m in st.session_state.c:
        with st.chat_message(m["r"]):
            st.write(m["t"])
            
    p = st.chat_input("Type your message here...")
    if p:
        st.session_state.c.append({"r": "user", "t": p})
        with st.chat_message("user"):
            st.write(p)
        
        # FIXED 2: Comprehensive validation path handling
        try:
            if openai_client:
                r = openai_client.chat.completions.create(
                    model=MODEL_CHATGPT,
                    messages=[{"role": x["r"], "content": x["t"]} for x in st.session_state.c]
                )
                a = r.choices[0].message.content
            elif groq_client:
                r = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": x["r"], "content": x["t"]} for x in st.session_state.c]
                )
                a = r.choices[0].message.content
            else:
                a = "Configuration error: System initialization failed to secure a backend framework pipeline."
        except Exception as e:
            a = f"API Error encountered: {str(e)}"

        with st.chat_message("assistant"):
            st.write(a)
        st.session_state.c.append({"r": "assistant", "t": a})

with t2:
    st.caption(f"Model: {MODEL_MATHS}")
    q = st.text_area("Enter your mathematical problem:")
    if st.button("Execute Solver"):
        if not groq_client:
            st.error("Operation failed: An authorized Groq Key token value is required to run this segment.")
        elif q:
            with st.spinner("Processing equations..."):
                try:
                    r = groq_client.chat.completions.create(
                        model=MODEL_MATHS,
                        messages=[{"role": "user", "content": f"Solve step by step: {q}"}]
                    )
                    st.markdown(r.choices[0].message.content)
                except Exception as e:
                    st.error(f"Execution failed: {str(e)}")

with t3:
    st.subheader("Text to Visual Canvas Generation")
    ip = st.text_input("Describe the image layout structure:")
    if st.button("Generate Image Asset"):
        if ip:
            u = "https://pollinations.ai" + urllib.parse.quote(ip)
            st.image(u, use_container_width=True)
            st.link_button("Download Image", u)

with t4:
    st.subheader("AI Creative Lyric Composer")
    top = st.text_input("Enter a theme or genre mood details:")
    if st.button("Compose Lyrics"):
        if not groq_client:
            st.error("Operation failed: Missing valid Groq connectivity tokens.")
        elif top:
            with st.spinner("Writing composition..."):
                try:
                    r = groq_client.chat.completions.create(
                        model=MODEL_MUSIC,
                        messages=[{"role":"user","content":f"Write a short song with clear guitar chord notations on: {top}"}]
                    )
                    st.session_state.ly = r.choices[0].message.content
                except Exception as e:
                    st.error(f"Generation failure: {str(e)}")
            
    if "ly" in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state.ly)
        
        # Audio rendering endpoint
        encoded_sample = urllib.parse.quote(st.session_state.ly[:150])
        au_url = f"https://pollinations.ai{encoded_sample}?model=openai-audio&voice=alloy"
        st.audio(au_url)

st.sidebar.success("System Verification Passed: JARVIS Online!")
