import streamlit as st
import requests

API_URL = "http://localhost:8000/ask_agent"  # adjust if running on another host/port

st.set_page_config(page_title="Finance Research Chat", layout="centered")

st.title("💬 Finance Research Agent")

# Store chat history in Streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

query = st.text_input("Ask a financial question:", "")

if st.button("Send") and query.strip():
    # Call backend
    try:
        response = requests.post(API_URL, json={"query": query})
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", {})

            # Sometimes answer is dict with "output", sometimes just string
            if isinstance(answer, dict):
                chat_history = answer.get("chat_history", [])
                output = answer.get("output", "")
            else:
                chat_history = []
                output = answer

            # Update session state
            st.session_state.chat_history = chat_history
            st.write("### 📊 Answer")
            st.write(output)
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Request failed: {e}")

# Display conversation history if available
if st.session_state.chat_history:
    st.write("### 📝 Conversation History")
    for turn in st.session_state.chat_history:
        role = "👤 User" if turn.get("type") == "human" else "🤖 Agent"
        content = turn.get("content", "")
        st.markdown(f"**{role}:** {content}")
