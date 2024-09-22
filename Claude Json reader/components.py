import streamlit as st
from utils import format_message

def ChatMessage(sender, text, timestamp):
    with st.container():
        col1, col2 = st.columns([1, 5])
        with col1:
            st.write(sender.capitalize())
        with col2:
            st.write(text)
        st.caption(format_message(timestamp))
        st.markdown("---")