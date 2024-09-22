import streamlit as st
import json
from utils import load_conversations, format_message
from components import ChatMessage

st.set_page_config(page_title="AI Chat Interface", layout="wide")

# Load conversations
conversations = load_conversations("conversations.json")

# Sidebar for conversation selection
st.sidebar.title("Conversations")
selected_conversation = st.sidebar.selectbox(
    "Select a conversation",
    options=conversations,
    format_func=lambda x: x['name']
)

# Main chat interface
st.title(f"Chat: {selected_conversation['name']}")

for message in selected_conversation['chat_messages']:
    ChatMessage(message['sender'], message['text'], message['created_at'])

# Input for new message
new_message = st.text_input("Type your message...")
if st.button("Send"):
    # Here you would typically send the message to your backend
    st.success("Message sent!")