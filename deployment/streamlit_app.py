import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.travel_agent import KenyaTravelAgent

st.set_page_config(page_title="Kenya Travel Assistant", page_icon="", layout="wide")

# Initialize
if 'agent' not in st.session_state:
    with st.spinner("Loading Kenya Travel Agent..."):
        st.session_state.agent = KenyaTravelAgent()
    st.session_state.messages = []

# Title
st.title("Kenya Travel Assistant")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("About")
    st.info("""
    This AI assistant uses:
    - Scraped travel data
    - Vector search
    - Language models
    
    Ask for specific, tailored information!
    """)
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            st.caption(f"Sources: {', '.join(message['sources'][:3])}")

# Input
prompt = st.chat_input("Ask about Kenyan travel...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            result = st.session_state.agent.ask(prompt)
            st.markdown(result["answer"])
            if result["sources"]:
                st.caption(f"Sources: {', '.join(result['sources'][:3])}")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": result["answer"],
                "sources": result["sources"]
            })