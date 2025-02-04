import streamlit as st
import whisper
import tempfile
import os
import subprocess
from datetime import datetime
from audio_recorder_streamlit import audio_recorder

# Page configuration
st.set_page_config(
    page_title="AudioScribe",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Container width */
    .block-container {
        padding: 1rem 2rem !important;
        max-width: 700px !important;
        margin: 0 auto !important;
    }
    
    /* Header styles */
    .main-header {
        font-size: 2.4rem !important;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
        line-height: 1.2;
        text-align: center;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 1.5rem;
        font-weight: 500;
        text-align: center;
    }
    
    /* Upload area */
    .uploadfile {
        border: 2px dashed #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        background-color: #f8fafc !important;
        margin-bottom: 1rem !important;
    }
    
    .uploadfile:hover {
        border-color: #0ea5e9 !important;
        cursor: pointer;
    }
    
    /* Audio section */
    .stAudio {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .stAudio > div {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
    }
    
    /* Success message */
    .success-box {
        padding: 0.6rem;
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 6px;
        color: #166534;
        font-weight: 500;
        margin: 0.75rem 0;
        text-align: center;
    }
    
    /* Section header */
    .section-header {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #0f172a !important;
        margin: 0.75rem 0 0.5rem 0 !important;
    }
    
    /* Text area */
    .stTextArea > div {
        margin-top: 0 !important;
    }
    
    .stTextArea > div > div {
        font-size: 1rem !important;
        line-height: 1.5 !important;
        color: #1e293b !important;
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
    }
    
    /* Button styles */
    .stButton > button {
        margin-top: 0.5rem !important;
        height: 2.5rem !important;
        padding: 0 1.25rem !important;
        background-color: #0ea5e9 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #0284c7 !important;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.2) !important;
    }
    
    /* Help text */
    .help-text {
        font-size: 0.95rem;
        color: #64748b;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    /* Recording button */
    .record-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.75rem 1.5rem;
        background-color: #ef4444;
        color: white;
        border-radius: 9999px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        margin: 1rem 0;
        border: none;
    }
    
    .record-button:hover {
        background-color: #dc2626;
    }
    
    .record-button.recording {
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
        }
    }
    
    /* Audio player */
    .audio-player {
        width: 100%;
        margin: 1rem 0;
        padding: 0.5rem;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>AudioScribe 🎙️</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Convert speech to text using OpenAI's Whisper</p>", unsafe_allow_html=True)

# Initialize the Whisper model
@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

# Create tabs for different input methods
tab1, tab2 = st.tabs(["Upload Audio", "Record Audio"])

with tab1:
    st.markdown("### Upload your audio file")
    uploaded_file = st.file_uploader("Choose an audio file", type=['wav', 'mp3', 'm4a', 'ogg'])
    
    if uploaded_file is not None:
        try:
            # Check if ffmpeg is installed
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            except subprocess.CalledProcessError:
                st.error("FFmpeg is not installed. Please install FFmpeg to process audio files.")
                st.stop()
            
            # Display audio player for preview
            st.markdown("### Preview Audio")
            st.audio(uploaded_file, format=f'audio/{uploaded_file.name.split(".")[-1]}')
            
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            with st.spinner("Transcribing... This might take a moment."):
                # Transcribe the audio
                result = model.transcribe(tmp_file_path)
                
                # Display results
                st.markdown("### Transcription Result")
                st.write(result["text"])
                
                # Add download buttons for the transcription and audio
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download Transcription",
                        data=result["text"],
                        file_name=f"transcription_{timestamp}.txt",
                        mime="text/plain"
                    )
                with col2:
                    st.download_button(
                        label="Download Audio",
                        data=uploaded_file.getvalue(),
                        file_name=uploaded_file.name,
                        mime=f"audio/{uploaded_file.name.split('.')[-1]}"
                    )
            
            # Clean up the temporary file
            os.unlink(tmp_file_path)
            
        except Exception as e:
            st.error(f"An error occurred while processing the audio: {str(e)}")
            st.info("Please try uploading again. Make sure the file is a valid audio file.")

with tab2:
    st.markdown("### Record Audio")
    st.markdown("""
        <div style='text-align: center;'>
            <p style='color: #475569; margin-bottom: 1rem;'>
                Click the button below to start/stop recording your audio
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Center the recording interface
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Audio recorder with custom styling
        audio_bytes = audio_recorder(
            pause_threshold=60.0,  # Increased pause threshold to avoid early stopping
            recording_color="#ef4444",
            neutral_color="#475569",
            icon_name="microphone",
            icon_size="2x"
        )
    
    if audio_bytes:
        try:
            # Create a temporary file for the recorded audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            # Display audio player
            st.markdown("### Preview Recording")
            st.audio(audio_bytes, format="audio/wav")
            
            with st.spinner("Transcribing... This might take a moment."):
                # Transcribe the recorded audio
                result = model.transcribe(tmp_file_path)
                
                # Display results
                st.markdown("### Transcription Result")
                st.write(result["text"])
                
                # Add download button for the transcription
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download Transcription",
                        data=result["text"],
                        file_name=f"transcription_{timestamp}.txt",
                        mime="text/plain"
                    )
                with col2:
                    # Add button to download the audio
                    st.download_button(
                        label="Download Recording",
                        data=audio_bytes,
                        file_name=f"recording_{timestamp}.wav",
                        mime="audio/wav"
                    )
            
            # Clean up the temporary file
            os.unlink(tmp_file_path)
            
        except Exception as e:
            st.error(f"An error occurred while processing the audio: {str(e)}")
            st.info("Please try recording again. Make sure to speak clearly and avoid background noise.")

# Add footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #64748b; padding: 1rem;'>
        Made with ❤️ using OpenAI's Whisper
    </div>
    """, 
    unsafe_allow_html=True
)