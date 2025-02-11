import streamlit as st
import requests

# Streamlit UI Configuration
st.set_page_config(page_title="QueryGenie: RAG-Powered Conversational AI", page_icon="💬", layout="wide")

# Title & Description
st.title("QueryGenie: RAG-Powered Conversational AI")
st.write("A conversational AI powered by Cohere API & FastAPI.")

# Collapsible Chat History
with st.expander("Show Chat History"):
    history_url = "http://127.0.0.1:8002/chat/history"
    history_response = requests.get(history_url)

    if history_response.status_code == 200:
        history_data = history_response.json()
        if history_data["status"] == "success" and history_data["conversation_history"]:
            for message in history_data["conversation_history"]:
                role = "🧑‍💻 You" if message["role"] == "user" else "🤖 AI"
                st.markdown(f"**{role}:** {message['content']}")
        else:
            st.info("No conversation history available.")
    else:
        st.error("Failed to retrieve chat history.")

# Chat Input Section
st.subheader("Chat")
user_input = st.text_input("Enter your message:", "")

if st.button("Send"):
    if user_input.strip() == "":
        st.error("⚠️ Input cannot be empty. Please enter a message.")
    else:
        # Make API request to FastAPI
        api_url = "http://127.0.0.1:8002/chat"
        params = {"user_input": user_input}
        response = requests.post(api_url, params=params)

        if response.status_code == 200:
            data = response.json()

            # Display AI or API response
            st.success("🤖 AI Response:")

            if data.get("api_response"):
                st.write(data["api_response"])
                st.caption("This information was retrieved from an external API.")
            else:
                st.write(data["ai_response"])
        else:
            st.error("Error communicating with the API. Please check your server.")

# Reset Chat Button
if st.button("Reset Chat"):
    reset_url = "http://127.0.0.1:8002/chat/reset"
    reset_response = requests.delete(reset_url)

    if reset_response.status_code == 200:
        st.success("🤖 Chat history cleared!")
    else:
        st.error("Failed to reset chat history.")
