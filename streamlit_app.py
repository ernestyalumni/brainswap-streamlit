import streamlit as st
import sys
import subprocess
import os
from pathlib import Path

# Function to initialize git submodules
def initialize_submodules():
    """Initialize git submodules if they don't exist."""
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            # We're in a git repo, try to initialize submodules
            subprocess.run(['git', 'submodule', 'update', '--init', '--recursive'], 
                         cwd=Path(__file__).parent, check=True)
            st.success("Git submodules initialized successfully!")
        else:
            st.warning("Not in a git repository, skipping submodule initialization")
    except subprocess.CalledProcessError as e:
        st.error(f"Failed to initialize submodules: {e}")
    except FileNotFoundError:
        st.error("Git not found. Please ensure git is installed in the deployment environment.")

# Initialize submodules first
initialize_submodules()

# Define the path to MoreGroq library
moregroq_path = Path(__file__).resolve().parent / "submodules" / \
    "InServiceOfX" / "PythonLibraries" / "ThirdParties" / "APIs" / "MoreGroq"

# Check if the path exists and add to sys.path if not already there
if moregroq_path.exists():
    moregroq_path_str = str(moregroq_path)
    if moregroq_path_str not in sys.path:
        sys.path.append(moregroq_path_str)
        st.info(f"Added MoreGroq path to sys.path: {moregroq_path_str}")
else:
    st.error(f"MoreGroq library not found at: {moregroq_path}")
    st.error("This might be due to git submodules not being initialized.")
    st.error("Please ensure the deployment environment has git installed and submodules are initialized.")
    st.stop()

# Now import the GroqAPIWrapper
try:
    from moregroq.Wrappers import GroqAPIWrapper
except ImportError as e:
    st.error(f"Failed to import GroqAPIWrapper: {e}")
    st.error("Please check that the MoreGroq library is properly installed and accessible.")
    st.stop()

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses Groq's models to generate responses. "
    "To use this app, you need to provide a Groq API key, which you can get [here](https://console.groq.com/keys). "
)

# Ask user for their Groq API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
groq_api_key = st.text_input("Groq API Key", type="password")
if not groq_api_key:
    st.info("Please add your Groq API key to continue.", icon="🗝️")
else:

    # Create a Groq API wrapper.
    groq_wrapper = GroqAPIWrapper(api_key=groq_api_key)
    # Configure for streaming
    groq_wrapper.configuration.stream = True

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the Groq API.
        try:
            response = groq_wrapper.create_chat_completion(
                st.session_state.messages)
            
            # Extract the response content
            if response and hasattr(response, 'choices') and \
                len(response.choices) > 0:
                assistant_message = response.choices[0].message.content
                
                # Display the response
                with st.chat_message("assistant"):
                    st.markdown(assistant_message)
                
                # Store the response in session state
                st.session_state.messages.append(
                    {"role": "assistant", "content": assistant_message})
            else:
                with st.chat_message("assistant"):
                    st.error("No response received from Groq API")
                    
        except Exception as e:
            with st.chat_message("assistant"):
                st.error(f"Error: {str(e)}")
