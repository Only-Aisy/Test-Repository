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
    (#anything added inside this indented section will pop up in the sidebar#)

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