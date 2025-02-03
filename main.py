import streamlit as st
import whisper
import tempfile
import os
import subprocess
from datetime import datetime

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
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>AudioScribe</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Convert your audio to text with AI-powered transcription</p>", unsafe_allow_html=True)

# Initialize session state for transcription
if 'transcription_result' not in st.session_state:
    st.session_state.transcription_result = None

# File upload with hidden label
uploaded_file = st.file_uploader("Upload Audio File", type=["mp3", "wav", "m4a", "ogg"], label_visibility="collapsed")

if uploaded_file is None:
    st.markdown("""
        <div class='help-text'>
        📎 Drag and drop your audio file here<br>
        🎵 Supports MP3, WAV, M4A, and OGG formats<br>
        ⚡ Fast, accurate AI transcription
        </div>
    """, unsafe_allow_html=True)

if uploaded_file is not None:
    try:
        # Check if ffmpeg is installed
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            st.error("""
                ⚠️ FFmpeg is not installed. This is required for audio processing.
                
                If you're running locally, install FFmpeg:
                - Ubuntu/Debian: `sudo apt-get install ffmpeg`
                - MacOS: `brew install ffmpeg`
                - Windows: Download from https://ffmpeg.org/download.html
                
                If you're using Streamlit Cloud, make sure you have a `packages.txt` file with `ffmpeg` listed.
            """)
            st.stop()

        # Audio player
        st.markdown("<div class='section-header'>Preview Audio</div>", unsafe_allow_html=True)
        st.audio(uploaded_file)
        
        # Only transcribe if we don't have the result in session state
        if st.session_state.transcription_result is None:
            with st.spinner("🎯 Transcribing your audio..."):
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                try:
                    # Load model and transcribe
                    model = whisper.load_model("base")
                    st.session_state.transcription_result = model.transcribe(tmp_file_path)
                    
                except Exception as e:
                    st.error(f"""
                        An error occurred during transcription: {str(e)}
                        
                        This might be due to:
                        1. Invalid audio format
                        2. Corrupted audio file
                        3. Insufficient system resources
                        
                        Please try with a different audio file or contact support.
                    """)
                    st.session_state.transcription_result = None
                finally:
                    # Clean up temporary file
                    if 'tmp_file_path' in locals():
                        os.unlink(tmp_file_path)
        
        # If we have a transcription result, show it
        if st.session_state.transcription_result is not None:
            # Success message and transcription
            st.markdown("<div class='success-box'>✨ Transcription completed!</div>", unsafe_allow_html=True)
            st.text_area("Transcription Result", value=st.session_state.transcription_result["text"], height=150, label_visibility="collapsed")
            
            # Download button
            st.download_button(
                label="💾 Download Transcription",
                data=st.session_state.transcription_result["text"],
                file_name=f"transcription_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
else:
    # Reset transcription result when no file is uploaded
    st.session_state.transcription_result = None

# Footer
st.markdown("""
    ---
    <div style='text-align: center; color: #666;'>
        Made with ❤️ using Streamlit and Whisper AI
    </div>
    """, unsafe_allow_html=True)