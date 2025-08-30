import streamlit as st
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from io import BytesIO
from pydub import AudioSegment
import matplotlib.pyplot as plt
import numpy as np

# ------------------ KEYS & URL ------------------
IBM_API_KEY = "a3hguuoy78tu2QfYBc7H-5IS7ien4v6BxIc9Gt9wnjVs"
TTS_URL = "https://api.au-syd.text-to-speech.watson.cloud.ibm.com/instances/9f8fd19d-6394-45ac-8473-c14c50b312fa"

# ------------------ CONFIGURE IBM WATSON TTS ------------------
tts_authenticator = IAMAuthenticator(IBM_API_KEY)
text_to_speech = TextToSpeechV1(authenticator=tts_authenticator)
text_to_speech.set_service_url(TTS_URL)

# ------------------ Helper function to generate waveform ------------------
def generate_waveform_plot(audio_bytes):
    try:
        audio_segment = AudioSegment.from_file(BytesIO(audio_bytes), format="mp3")
        samples = np.array(audio_segment.get_array_of_samples())
        
        # Downsample the data for a cleaner plot, without losing too much detail
        stride = max(1, len(samples) // 10000)
        downsampled_samples = samples[::stride]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.plot(downsampled_samples, color='#6A1B9A', linewidth=1)
        
        # Style the plot to match the app's dark theme
        ax.set_facecolor('#2A2A4A')
        fig.patch.set_facecolor('#2A2A4A')
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        plt.tight_layout()
        
        # Return the figure object
        return fig
        
    except Exception as e:
        st.error(f"Error generating waveform: {e}")
        return None

# ------------------ STREAMLIT UI SETUP ------------------
st.set_page_config(layout="wide", page_title="Audio Ninja AI", initial_sidebar_state="expanded")

# --- Custom CSS for a more app-like feel ---
st.markdown("""
    <style>
    /* Main app background */
    .stApp {
        background-color: #1a1a2e; /* Dark purple */
        color: #e0e0e0;
    }
    /* Sidebar styling */
    .stSidebar {
        background-color: #2a2a4a; /* Slightly lighter purple for sidebar */
        padding-top: 20px;
    }
    .stSidebar .stSelectbox, .stSidebar .stRadio, .stSidebar .stTextInput {
        background-color: #3b3b6b;
        color: #e0e0e0;
        border-radius: 5px;
        padding: 5px;
    }
    .stSidebar .stSelectbox > div > div, .stSidebar .stRadio > div > label, .stSidebar .stTextInput > div > div > input {
        color: #e0e0e0 !important;
    }
    /* Header (for search bar) */
    header {
        background-color: #1a1a2e;
        border-bottom: 1px solid #3b3b6b;
    }
    /* Custom button styling (e.g., for navigation) */
    div.stButton > button {
        background-color: #3b3b6b;
        color: #ffffff;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        margin: 5px 0;
        width: 100%;
        text-align: left;
    }
    div.stButton > button:hover {
        background-color: #4a4a8a;
        color: #ffffff;
    }
    /* Specific styling for the 'Generate Audio' button */
    #generate-audio-button > div > button {
        background-color: #6a1b9a; /* Purple color */
        color: #ffffff;
        padding: 12px 25px;
        font-size: 1.1em;
        border-radius: 8px;
        width: auto;
        float: right; /* Align right */
    }
    #generate-audio-button > div > button:hover {
        background-color: #8e24aa;
    }

    /* Text area styling */
    .stTextArea > label {
        color: #e0e0e0;
        font-size: 1.1em;
        margin-bottom: 10px;
    }
    .stTextArea textarea {
        background-color: #2a2a4a; /* Darker background for text input */
        color: #e0e0e0;
        border: 1px solid #4a4a8a;
        border-radius: 5px;
        padding: 10px;
        font-size: 1.05em;
    }

    /* Input text styling */
    .stTextInput > label {
        color: #e0e0e0;
        font-size: 1.1em;
        margin-bottom: 10px;
    }
    .stTextInput input {
        background-color: #2a2a4a;
        color: #e0e0e0;
        border: 1px solid #4a4a8a;
        border-radius: 5px;
        padding: 10px;
        font-size: 1.05em;
    }

    /* Make Streamlit's default elements darker */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size:1.2rem;
    }
    .stDownloadButton > div > button {
        background-color: #3b3b6b;
        color: #ffffff;
        border: none;
        padding: 8px 15px;
        border-radius: 5px;
        margin-top: 10px;
    }
    .stDownloadButton > div > button:hover {
        background-color: #4a4a8a;
    }

    /* Adjust audio player background to match app */
    .stAudio {
        background-color: #1a1a2e !important;
        border-radius: 8px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------ Session State Initialization ------------------
if 'audio_bytes' not in st.session_state:
    st.session_state['audio_bytes'] = None
if 'audio_generated' not in st.session_state:
    st.session_state['audio_generated'] = False
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Text to Audio'
if 'waveform_fig' not in st.session_state:
    st.session_state['waveform_fig'] = None

# ------------------ SIDEBAR ------------------
with st.sidebar:
    st.image("ninja_logo.png", width=50) 
    st.markdown("## Audio AI")

    if st.button("🎤 Text to Audio", key="nav_text_to_audio"):
        st.session_state['current_page'] = 'Text to Audio'
    if st.button("📜 Recent History", key="nav_recent_history"):
        st.session_state['current_page'] = 'Recent History'
    if st.button("📁 Upload Audio", key="nav_upload_audio"):
        st.session_state['current_page'] = 'Upload Audio'
    if st.button("🎶 My Audios", key="nav_my_audios"):
        st.session_state['current_page'] = 'My Audios'
    if st.button("⚙️ Settings", key="nav_settings"):
        st.session_state['current_page'] = 'Settings'

# ------------------ MAIN CONTENT AREA ------------------

# Top Search Bar
st.markdown("""
    <div style='display: flex; align-items: center; margin-bottom: 20px;'>
        <input type='text' placeholder='Search for audio or settings...' 
               style='flex-grow: 1; padding: 10px; border-radius: 5px; border: 1px solid #4a4a8a; 
                      background-color: #2a2a4a; color: #e0e0e0; font-size: 1.05em;'>
        <span style='margin-left: 10px; font-size: 1.5em; color: #e0e0e0;'>🔍</span>
    </div>
    """, unsafe_allow_html=True)


if st.session_state['current_page'] == 'Text to Audio':
    st.subheader("Enter the Prompt") # Updated heading
    # Display the waveform plot
    if st.session_state.get('waveform_fig'):
        st.pyplot(st.session_state['waveform_fig'], use_container_width=True)
    else:
        # Placeholder for the waveform
        st.markdown("<div style='height: 100px; background-color: #2a2a4a; border-radius: 8px;'></div>", unsafe_allow_html=True)
    
    # User text input area
    user_text = st.text_area("Enter text here to convert to audio...", height=150, key="input_text_main")

    # --- Layout for Voice Selection and Generate Audio Button ---
    col_voice, col_convert = st.columns([0.3, 0.7])

    with col_voice:
        voice_options = {
            "en-US_LisaV3Voice": "Female Voice",
            "en-US_MichaelV3Voice": "Male Voice",
            "en-US_AllisonV3Voice": "Allison (Female)"
        }
        selected_voice = st.radio("Choose Voice", list(voice_options.keys()), format_func=lambda x: voice_options[x], key="voice_select")

        # Adding tones as requested
        st.radio("Choose Tone", ["Neutral", "Suspenseful", "Inspiring"], key="tone_select")


    with col_convert:
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        if st.button("Generate Audio", key="generate_audio_button"): # Updated button label
            if user_text.strip():
                with st.spinner("Converting text to audio..."):
                    try:
                        audio_response = text_to_speech.synthesize(
                            text=user_text,
                            voice=selected_voice,
                            accept='audio/mp3'
                        ).get_result()
                        
                        st.session_state['audio_bytes'] = audio_response.content
                        st.session_state['audio_generated'] = True
                        
                        # Generate and store the waveform plot
                        st.session_state['waveform_fig'] = generate_waveform_plot(st.session_state['audio_bytes'])
                        
                        st.success("Audio converted successfully!")
                    except Exception as e:
                        st.error(f"Error generating audio: {e}")
                        st.session_state['audio_generated'] = False
                        st.session_state['waveform_fig'] = None
            else:
                st.warning("Please enter text to convert to audio.")

    # --- Display Audio Player and Download Button ---
    st.markdown("<hr style='border: 1px solid #3b3b6b; margin-top: 30px; margin-bottom: 20px;'>", unsafe_allow_html=True)
    st.markdown("### Play and Download Audio")

    if st.session_state.get('audio_generated') and st.session_state['audio_bytes'] is not None:
        st.audio(st.session_state['audio_bytes'], format='audio/mp3', start_time=0)
        st.download_button(
            label="Download MP3",
            data=st.session_state['audio_bytes'],
            file_name="converted_audio.mp3",
            mime="audio/mpeg"
        )
    elif st.session_state.get('audio_generated') is False:
        pass

elif st.session_state['current_page'] == 'Recent History':
    st.subheader("Recent History")
    st.info("This section will show your recent audio conversions.")

elif st.session_state['current_page'] == 'Upload Audio':
    st.subheader("Upload Audio")
    uploaded_audio = st.file_uploader("Upload an audio file (e.g., MP3, WAV)", type=["mp3", "wav"])
    if uploaded_audio:
        st.success("Audio file uploaded successfully!")
        st.audio(uploaded_audio, format=f'audio/{uploaded_audio.type.split("/")[-1]}')

elif st.session_state['current_page'] == 'My Audios':
    st.subheader("My Audios")
    st.info("This section will list all your saved audio files.")

elif st.session_state['current_page'] == 'Settings':
    st.subheader("Settings")
    st.info("This section will allow you to configure application settings.")