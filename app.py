import streamlit as st
from groq import Groq
import urllib.parse

st.set_page_config(page_title="JARVIS", layout="wide")
st.title("JARVIS 5-in-1")

# Handle Groq API Key
KEY = st.secrets.get("GROQ_KEY")
if not KEY:
    KEY = st.sidebar.text_input("Groq Key", type="password")
if not KEY:
    st.stop()

client = Groq(api_key=KEY)

# CORRECTED: Groq uses models like Llama 3, Mixtral, or Gemma, not OpenAI models.
MODEL = "llama3-8b-8192" 

t1, t2, t3, t4, t5 = st.tabs(["Chat", "Maths", "Image", "Video", "Music"])

# --- Tab 1: Chat ---
with t1:
    if "c" not in st.session_state:
        st.session_state.c = []
        
    for m in st.session_state.c:
        with st.chat_message(m["r"]):
            st.write(m["t"])
            
    p = st.chat_input("Pucho Boss...")
    if p:
        st.session_state.c.append({"r": "user", "t": p})
        with st.chat_message("user"):
            st.write(p)
            
        r = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": x["r"], "content": x["t"]} for x in st.session_state.c]
        )
        a = r.choices[0].message.content
        with st.chat_message("assistant"):
            st.write(a)
        st.session_state.c.append({"r": "assistant", "t": a})

# --- Tab 2: Maths ---
with t2:
    q = st.text_area("Maths Question:")
    if st.button("Solve Maths"):
        if q:
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": f"Solve step by step: {q}"}]
            )
            st.markdown(r.choices[0].message.content)

# --- Tab 3: Image ---
with t3:
    ip = st.text_input("Image Prompt:")
    if st.button("Make Image"):
        if ip:
            u = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(ip)
            st.image(u)
            st.link_button("Download Image", u)

# --- Tab 4: Video ---
with t4:
    vp = st.text_input("Video Prompt:")
    if st.button("Make Video"):
        if vp:
            v = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(vp) + "?model=video"
            st.video(v)
            st.link_button("Download Video", v)

# --- Tab 5: Music ---
with t5:
    st.subheader("Music & Guitar")
    top = st.text_input("Song Topic / Mood:")
    typ = st.selectbox("Type", ["Normal Song", "Guitar Tabs", "Guitar Chords"])
    
    if st.button("Make Lyrics"):
        if top:
            pr = f"Write {typ} for {top} with chords"
            r = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": pr}]
            )
            st.session_state.ly = r.choices[0].message.content
            
    # CORRECTED: Keep text visible on screen even after clicking "Play Music" button
    if "ly" in st.session_state:
        st.markdown(st.session_state.ly)
        
        if st.button("Play Music"):
            # Truncate text context safely for the API endpoint
            au = "https://text.pollinations.ai/" + urllib.parse.quote(st.session_state.ly[:250]) + "?model=openai-audio&voice=alloy"
            st.audio(au)
            st.link_button("Download Music", au)

st.sidebar.success("JARVIS Ready!")
