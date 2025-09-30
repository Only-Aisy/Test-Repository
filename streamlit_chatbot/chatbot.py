##Include the following at the top before writing any code

import streamlit as st
import pandas as pd



def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def main():
    st.title("My First Chatbot")
    
    initialize_session_state()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("What's on your mind?"):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Add simple bot response
        response = f"You said: {prompt}"
        with st.chat_message("assistant"):
            st.write(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()


with st.sidebar:
    st.title("Sidebar") 

    st.radio("Radio-button select", ["Friendly", "Formal", "Funny"], index=0)
    st.multiselect("Multi-select", ["Movies", "Travel", "Food", "Sports"], default=["Food"])
    st.selectbox("Dropdown select", ["Data", "Code", "Travel", "Food", "Sports"], index=0)
    st.slider("Slider", min_value=1, max_value=200, value=60)
    st.select_slider("Option Slider", options=["Very Sad", "Sad", "Okay", "Happy", "Very Happy"], value="Okay")


use_emoji = "👤" # Change this to any emojis you like
robot_img = "robot.jpg" # Find a picture online(jpg/png), download it and drag to
												# your files under the Chatbot folder

# Replace the section in the code that says "Display chat messages" with this code
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar=robot_img):
            st.write(f"{message['content']}")
    else:
        with st.chat_message("user", avatar=user_emoji):
            st.write(f"{message['content']}")

import streamlit as st
import google.generativeai as genai

# Configure Gemini API
GOOGLE_API_KEY = "AIzaSyAfuGACGyyhen5xUkyLQzDHGc7pPL02SzQ"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def get_gemini_response(prompt, persona_instructions):
    full_prompt = f"{persona_instructions}\n\nUser: {prompt}\nAssistant:"
    response = model.generate_content(full_prompt)
    return response.text

def main():
    st.title("Gemini AI Chatbot")

    # Sidebar options
    persona = st.sidebar.radio("Choose bot personality", ["Friendly", "Formal", "Funny"], index=0)
    persona_instructions = {
        "Friendly": "You are a friendly assistant, always kind and polite.",
        "Formal": "You are a formal assistant, always professional.",
        "Funny": "You are a hilarious roast bot. Be playful and witty. Your roasts should be light-hearted, never offensive. Use funny emojis and sarcasm."
    }[persona]

    initialize_session_state()

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message("assistant", avatar="robot.jpg"):  # You can use an emoji or an image
                st.write(f"{message['content']}")
        else:
            with st.chat_message("user", avatar="👤"):  # Or use a user emoji
                st.write(f"{message['content']}")

    # Chat input
    if prompt := st.chat_input("Chat with Gemini"):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get Gemini response with persona instructions
        response = get_gemini_response(prompt, persona_instructions)

        # Display assistant response
        with st.chat_message("assistant"):
            st.write(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()


persona_instructions = """
You are a hilarious roast bot.
Be playful and witty.
Your roasts should be light-hearted, never offensive.
Use funny emojis and sarcasm in your replies.
"""

##Find the "get_gemini_response" function in your code and replace it with this function below

def get_gemini_response(prompt, persona_instructions):
    full_prompt = f"{persona_instructions}\n\nUser: {prompt}\nAssistant:"
    response = model.generate_content(full_prompt)
    return response.text

if prompt := st.chat_input("Chat with Gemini"):
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get Gemini response with persona
    response = get_gemini_response(prompt, persona_instructions)

    # Display assistant response
    with st.chat_message("assistant"):
        st.write(response)

    st.session_state.messages.append({"role": "assistant", "content": response})


