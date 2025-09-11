import streamlit as st
import requests

API_URL = "http://localhost:8000/ask_agent"  # adjust if running on another host/port

st.set_page_config(page_title="Finance Research Chat", layout="centered")

# Custom CSS for chat bubbles and loader
st.markdown("""
    <style>
    .chat-bubble {
        max-width: 80%%;
        padding: 0.7em 1.2em;
        margin: 0.5em 0;
        border-radius: 1.2em;
        font-size: 1.05em;
        line-height: 1.5;
        display: inline-block;
        word-break: break-word;
    }
    .user-bubble {
        background: #e3f2fd;
        color: #1565c0;
        margin-left: auto;
        margin-right: 0;
        text-align: right;
    }
    .ai-bubble {
        background: #f1f8e9;
        color: #33691e;
        margin-right: auto;
        margin-left: 0;
        text-align: left;
    }
    .loader {
        border: 6px solid #f3f3f3;
        border-top: 6px solid #1565c0;
        border-radius: 50%%;
        width: 36px;
        height: 36px;
        animation: spin 1s linear infinite;
        display: inline-block;
        vertical-align: middle;
        margin-right: 10px;
    }
    @keyframes spin {
        0%% { transform: rotate(0deg);}
        100%% { transform: rotate(360deg);}
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>💬 Finance Research Agent</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Ask anything about stocks, sectors, or financial trends.<br>Powered by Gemini LLM.</p>", unsafe_allow_html=True)

# Store chat history in Streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

query = st.text_input("Ask a financial question:", "")

if st.button("Send") and query.strip():
    with st.spinner("🤔 Thinking..."):
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

                # Add user and agent turns to chat history
                st.session_state.chat_history.append({"type": "human", "content": query})
                st.session_state.chat_history.append({"type": "ai", "content": output})

                st.markdown("<div class='ai-bubble chat-bubble'><b>🤖 Agent:</b> " + output + "</div>", unsafe_allow_html=True)
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

st.markdown("---")

# Display conversation history as chat bubbles
if st.session_state.chat_history:
    st.markdown("### 📝 Conversation History")
    for turn in st.session_state.chat_history:
        role = turn.get("type")
        content = turn.get("content", "")
        if role == "human":
            st.markdown(
                f"<div class='user-bubble chat-bubble'><b>👤 You:</b> {content}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='ai-bubble chat-bubble'><b>🤖 Agent:</b> {content}</div>",
                unsafe_allow_html=True
            )
