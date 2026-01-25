import os
import time
import asyncio
import streamlit as st
from streamlit.components.v1 import html
from streamlit_chat_widget import chat_input_widget
from streamlit_float import *
from google import genai
from groq import Groq
import boto3
from agent_utilities import DatabaseAgent
from llm_utilities import transcribe_audio, synthesize_speech,save_audio_file

def _get_session():
    from streamlit.runtime import get_instance
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    runtime = get_instance()
    session_id = get_script_run_ctx().session_id
    # session_info = runtime._session_mgr.get_session_info(session_id)
    # if session_info is None:
    #     raise RuntimeError("Couldn't get your Streamlit Session object.")
    return session_id
def main():
        
    # --- Streamlit UI Setup ---
    st.set_page_config(layout="wide") # Use wide layout for better chat display
    st.title("AI Assistant for Patient Queries")
    # --- Sidebar for API Key and Patient Selection ---
    with st.sidebar:
        st.header("API Configuration")
        # Use st.secrets for production or environment variables for local development
        # st.text_input("Enter Gemini API Key", key="gemini_api_key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
        # For a persistent text input for API key:
        GOOGLE_API_KEY = st.text_input("Enter Gemini API Key", type="password", value=st.session_state.get("gemini_api_key_input", os.environ.get("GEMINI_API_KEY", "")))
        if GOOGLE_API_KEY:
            st.session_state["gemini_api_key_input"] = GOOGLE_API_KEY # Store in session state for persistence
        
        st.markdown("---")
        st.header("Patient Selection")
        # Patient selection dropdown
        # Using a placeholder for the dropdown to avoid showing it when no patients are available
        # In a real application, you would fetch this list from a database or API
        option = st.selectbox(
            "Which patient would you like to look up?",
            ["132#Kate Ann Evans", 
             "133#Daniel John Thomas", 
             "134#Emily George Walker",
             "135#Daniel Kevin White",
             "136#Daniel David Jackson",
             "143#Alexander Michael Lewis",
             "157#Aiden Nicholas Baker",
             "168#Aiden Juan Green",
             "174#Luna Timothy Flores",
             "178#Luna Stephen Wright"],
            index=None,
            placeholder="Select a patient to chat with",
            help="Select a patient to chat with. The ID is used for backend operations.",
        )
        st.write("You selected:", option)
        st.markdown("---")
        st.header("Debug Info")
        show_debug = st.checkbox("Show Debug Info", value=False)
    
    # st.markdown("---")
    # --- API Key Validation and Client Initialization ---
    # Check if API keys are provided
    if GOOGLE_API_KEY: #and GROQ_API_KEY:
        try:
            genai_client = genai.Client(api_key=GOOGLE_API_KEY)
            # groq_client  = Groq(api_key=GROQ_API_KEY)
        except Exception as e:
            st.error(f"Failed to initialize Gemini client: {e}")
            st.info("Please check your API key.")
            st.stop() # Stop execution if client initialization fails  
        
    else:
        st.info("🔑 Please add your Gemini API key in the sidebar to continue.")
        st.stop() # Stop execution if no API key
    
    # Create a client for Amazon Polly
    polly_client = boto3.client('polly', 
                        aws_access_key_id="key_id", 
                        aws_secret_access_key="secret_key",
                        region_name="region_name") # Replace with your AWS credentials and region
        
    if option:
        patient_id = option.split("#")[0] # Extract user ID from the selected option
        st.session_state["user_id"] = patient_id # Store user ID in session state for later use
         # --- Streamlit Chat Logic ---
        # Initialize session state for messages
        if "messages" not in st.session_state:
            st.session_state.messages = []
    if not option:
        st.info("Please select a patient to continue.")
        st.stop()
        
    # Display existing messages
    # Removed custom column layout as st.chat_message handles alignment and avatars
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑‍💻" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # Input widget at the bottom using streamlit_extras
    float_init()
    footer_container = st.container()
    with footer_container:
        user_input_data = chat_input_widget() # The widget returns a dictionary with 'text' or 'audioFile'
    footer_container.float(
        "display:flex; align-items:center;justify-content:center; overflow:hidden visible;flex-direction:column; position:fixed;bottom:15px;"
    )
    
    # Process user input only if something was provided
    if user_input_data:
        user_query = None
        session_id = _get_session()
        ts = int(time.time())
        # Handle text input
        if "text" in user_input_data and user_input_data["text"]:
            user_query = user_input_data["text"]
        
        # Handle audio input
        elif "audioFile" in user_input_data and user_input_data["audioFile"]:
            with st.spinner("Transcribing audio..."):
                audio_file_bytes = user_input_data["audioFile"]
                # Streamlit's file_uploader gives bytes, need to save to a temp file for GenAI API
                # Use a more robust temporary file naming (e.g., uuid or time-based) for real apps
                temp_audio_path = f"audio/temp_audio_input_{session_id}_{ts}.wav" 
                
                try:
                    with open(temp_audio_path, "wb") as f:
                        f.write(bytes(audio_file_bytes))
                    f.close()
                    # Call transcribe_audio with the client instance and temp file path
                    # Assuming the widget provides WAV, specify mime_type accordingly
                    user_query = transcribe_audio(genai_client, temp_audio_path, mime_type='audio/wav')
                    if show_debug:
                        st.write(f"Transcribed audio to: {user_query}")
                except Exception as e:
                    st.error(f"Error transcribing audio: {e}")
                    if show_debug:
                        st.exception(e)
                    user_query = None # Clear query if transcription fails
                # finally:
                #     if os.path.exists(temp_audio_path):
                #         os.remove(temp_audio_path) # Clean up the temporary file

        # If a valid user_query was obtained (from text or successful transcription)
        
        if user_query:
            # Add user message to chat history and display it
            st.session_state.messages.append({"role": "user", "content": user_query})
            # Display user message immediately (optional, but good UX)
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(user_query)
                
            # Generate response from the AI assistant
            
            database_agent = DatabaseAgent(patient_id, GOOGLE_API_KEY, user_query)
            assistant_response = database_agent.create_agent()
            # Get assistant response and display it
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..."):
                    # Call respond_user with the client instance and user query
                    # output_audio_path = f"audio/temp_audio_output_{session_id}_{ts}.wav"
                    output_audio_path = f"audio/temp_audio_output_{session_id}_{ts}.mp3"
                    synthesized_audio = synthesize_speech(polly_client=polly_client,
                                                          text=assistant_response)

                    save_audio_file(synthesized_audio, output_audio_path)
                    # asyncio.run(output_audio(groq_client, assistant_response, output_audio_path))
                    st.markdown(assistant_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            
            # Play the audio 
            audio_container = st.container()
            with audio_container:
                st.audio(output_audio_path, format="audio/mp3", autoplay=True)
            audio_container.float(
            "display:flex;align-items:center;justify-content:center; overflow:hidden visible;flex-direction:column; position:fixed;bottom:100px;")
            html(
            """
            <div id="div" />
            <script>
                // Scroll the div into view smoothly
                var div = document.getElementById('div');
                div.scrollIntoView({ behavior: 'smooth', block: 'end' });
            </script>
            """
        )
        
            

if __name__ == "__main__":
    main()