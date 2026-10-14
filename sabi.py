import os
import streamlit as st
import time
import datetime
import csv
import PyPDF2
from google import genai
from google.genai import types

# --- TITLE ---
st.set_page_config(page_title="Sabi's AI Chatbot", layout="centered")
st.title("my first ai chatbot")
st.header("created by shaik sabiha")

# --- API KEY (works both local + Streamlit cloud) ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    from dotenv import load_dotenv
    load_dotenv()
    API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)
MODEL = "gemini-2.0-flash"

# --- MONITORING SETUP ---
if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0
if "total_pdfs" not in st.session_state:
    st.session_state.total_pdfs = 0
if "errors" not in st.session_state:
    st.session_state.errors = 0
if "logs" not in st.session_state:
    st.session_state.logs = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR MONITORING DASHBOARD ---
with st.sidebar:
    st.header("📊 Monitoring Dashboard")
    st.metric("Total Queries", st.session_state.total_queries)
    st.metric("PDFs Processed", st.session_state.total_pdfs)
    st.metric("Errors", st.session_state.errors)
    st.write(f"Uptime: {datetime.datetime.now().strftime('%H:%M:%S')}")
    if st.session_state.logs:
        st.subheader("Recent Logs")
        for log in st.session_state.logs[-5:][::-1]:
            st.text(log)

# --- PDF UPLOAD ---
file = st.file_uploader("uploaded folder", type=["pdf"])
pdf_text = ""

if file:
    st.session_state.total_pdfs += 1
    st.write("uploaded file", file.name)
    try:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            txt = page.extract_text()
            if txt:
                pdf_text += txt + "\n"
        st.session_state.logs.append(f"{datetime.datetime.now().strftime('%H:%M')} - PDF: {file.name}")
    except Exception as e:
        st.error(f"PDF error: {e}")

# --- SHOW OLD CHATS ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("ASK GEMINI"):
    start_time = time.time()
    st.session_state.total_queries += 1
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build prompt with PDF
    if pdf_text:
        full_prompt = f"PDF Content from {file.name}:\n{pdf_text[:15000]}\n\nUser Question: {prompt}\nAnswer based on PDF."
    else:
        full_prompt = prompt

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.models.generate_content(model=MODEL, contents=full_prompt)
                answer = response.text
                st.markdown(answer)
                latency = time.time() - start_time
                st.caption(f"⚡ Response: {latency:.2f}s")
        
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.logs.append(f"{datetime.datetime.now().strftime('%H:%M')} - Q: {prompt[:25]} | {latency:.2f}s OK")

    except Exception as e:
        st.session_state.errors += 1
        st.error(f"Error: {e}")
        st.session_state.logs.append(f"ERROR: {e}")
    
