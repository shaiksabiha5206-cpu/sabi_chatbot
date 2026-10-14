import os 
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
load_dotenv()
API_KEY=os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)
MODEL = "gemini-3.5-flash-lite"
st.title("my first ai chatboot")
st.header("created by shaik sabiha")
file = st.file_uploader("uploaded folder",type=["pdf"])
if file:
    st.write("uploaded file",file.name)
#create memory
if "messages" not in st.session_state:
    st.session_state.messages =[]
#show old chats
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
#take new input
if prompt := st.chat_input("ASK GEMINI"):
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
#get gemini reply
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role":"assistant","content":response.text})
    