import streamlit as st
import asyncio
import websockets
import json

WS_URL = "wss://fastapibackend.voctrum.com/chatbot/ask/"

# ── WebSocket helper ──────────────────────────────────────────────────────────

async def ask_question(question: str, chat_history: list) -> str:
    try:
        async with websockets.connect(WS_URL) as ws:
            await ws.send(json.dumps({
                "question": question,
                "chat_history": chat_history
            }))

            response = json.loads(await ws.recv())

            if response.get("status") == "success":
                return response.get("answer", "No answer received")
            else:
                return f"❌ Error: {response.get('message', 'Unknown error')}"

    except Exception as e:
        return f"❌ Connection Error: {str(e)}"


def send_message(question: str) -> str:
    return asyncio.run(ask_question(question, st.session_state.chat_history))


# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="VOCTRUM Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 VOCTRUM Chatbot")

# ── Initialize session state ──────────────────────────────────────────────────

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []


# ── Display chat messages ─────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ── User input ────────────────────────────────────────────────────────────────

if prompt := st.chat_input("Ask something..."):

    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare chat history for backend
    formatted_history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]
    st.session_state.chat_history = formatted_history

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = send_message(prompt)
            st.markdown(answer)

    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })


# ── Clear chat button ─────────────────────────────────────────────────────────

if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.session_state.chat_history = []
    st.rerun()
