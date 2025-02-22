import streamlit as st
from pathlib import Path
from datetime import datetime
from src.transcriber import LemurTranscriber
from src.utils import save_uploaded_file, get_unique_filename
from config import ASSEMBLYAI_API_KEY

# Page configuration (MUST BE THE FIRST STREAMLIT COMMAND)
st.set_page_config(page_title="Meeting Summary & Decision Tracker", layout="wide")

# Custom CSS for styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    local_css("styles.css")
except FileNotFoundError:
    st.warning("styles.css not found. Using default styling.")

# Initialize session state
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Instructions"

if 'transcriber' not in st.session_state:
    st.session_state.transcriber = LemurTranscriber(ASSEMBLYAI_API_KEY)

if 'transcripts' not in st.session_state:
    st.session_state.transcripts = []

# Sidebar for navigation
st.sidebar.title("Navigation")
tabs = ["Instructions", "Transcript Management", "Generate Summary"]
tab = st.sidebar.radio("Go to", tabs, index=tabs.index(st.session_state.current_tab))

# Instructions Tab
if tab == "Instructions":
    st.session_state.current_tab = "Instructions"
    st.title("Welcome to the Meeting Summary & Decision Tracker")
    st.write("""
    This application helps you manage meeting transcripts, generate summaries, and track decisions.
    Please follow the instructions below to get started.
    """)

    st.header("Instructions")
    st.write("""
    1. **Transcript Management Tab:** Upload audio files or text transcripts for processing.
    2. **Generate Summary Tab:** Select a processed transcript to generate summary and key points.
    """)

    if st.button("Get Started"):
        st.session_state.current_tab = "Transcript Management"
        st.rerun()

# Transcript Management Tab
elif tab == "Transcript Management":
    st.session_state.current_tab = "Transcript Management"
    st.title("Transcript Management")

    # Upload Section
    st.header("Upload Transcript")
    upload_type = st.radio("Choose Upload Type", ["Audio File", "Text Transcript"])

    if upload_type == "Audio File":
        col1, col2 = st.columns([2, 1])
        with col1:
            uploaded_file = st.file_uploader(
                "Upload Audio File (WAV/MP3)",
                type=["wav", "mp3"],
                help="Upload an audio file for transcription"
            )

        with col2:
            meeting_title = st.text_input(
                "Meeting Title",
                placeholder="Enter a title for this meeting",
                help="This will help identify the transcript later"
            )

        if uploaded_file and meeting_title and st.button("Transcribe Audio"):
            with st.spinner("Processing audio file..."):
                try:
                    # Save uploaded file
                    file_path, error = save_uploaded_file(uploaded_file)
                    if error:
                        st.error(f"Error saving file: {error}")
                        st.stop()

                    # Create transcripts directory if it doesn't exist
                    transcripts_dir = Path("transcripts")
                    transcripts_dir.mkdir(exist_ok=True)

                    # Generate output path using meeting title
                    safe_title = "".join(c if c.isalnum() else "_" for c in meeting_title)
                    output_path = get_unique_filename(f"transcripts/{safe_title}.json")

                    # Transcribe
                    result = st.session_state.transcriber.transcribe(
                        audio_path=file_path,
                        output_path=output_path
                    )

                    # Add to transcripts list
                    transcript_info = {
                        "title": meeting_title,
                        "source_type": "Audio",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "file_path": output_path,
                        "content": result
                    }
                    st.session_state.transcripts.append(transcript_info)

                    # Show success and preview
                    st.success("✅ Transcription completed successfully!")

                    with st.expander("Show Preview"):
                        st.subheader("Transcript Preview:")
                        for segment in result["segments"][:3]:
                            st.markdown(f"**{segment['speaker']}** ({segment['start']:.1f}s - {segment['end']:.1f}s):")
                            st.markdown(f"> {segment['text']}")

                        st.info("Note: This is just a preview. Full transcript available in Generate Summary tab.")

                except Exception as e:
                    st.error(f"Transcription failed: {str(e)}")
                    st.error("Please try again or contact support if the problem persists.")
                finally:
                    # Clean up uploaded file
                    if file_path and Path(file_path).exists():
                        Path(file_path).unlink()

    elif upload_type == "Text Transcript":
        text_transcript = st.text_area(
            "Paste Text Transcript",
            placeholder="Paste your text transcript here...",
            height=300
        )
        if st.button("Process Text") and text_transcript:
            st.info("Text transcript processing will be implemented in future updates.")

    # List of Saved Transcripts
    if st.session_state.transcripts:
        st.header("Saved Transcripts")
        transcript_data = {
            "Meeting Title": [],
            "Source Type": [],
            "Timestamp": []
        }

        for transcript in st.session_state.transcripts:
            transcript_data["Meeting Title"].append(transcript["title"])
            transcript_data["Source Type"].append(transcript["source_type"])
            transcript_data["Timestamp"].append(transcript["timestamp"])

        st.table(transcript_data)
    else:
        st.info("No transcripts available yet. Upload an audio file or text to get started!")

# Generate Summary Tab
elif tab == "Generate Summary":
    st.session_state.current_tab = "Generate Summary"
    st.title("Generate Summary")

    if not st.session_state.transcripts:
        st.warning("No transcripts available. Please upload and process a transcript first.")
        if st.button("Go to Transcript Management"):
            st.session_state.current_tab = "Transcript Management"
            st.rerun()
    else:
        # Transcript Selection
        st.header("Select Transcript")
        transcript_titles = [t["title"] for t in st.session_state.transcripts]
        selected_transcript = st.selectbox("Choose a transcript", transcript_titles)

        # Find selected transcript data
        transcript_data = next(
            (t for t in st.session_state.transcripts if t["title"] == selected_transcript),
            None
        )

        if transcript_data and st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                # TODO: Implement actual summary generation
                st.success("Summary generated successfully!")

                # Display Transcript Content
                st.header("Full Transcript")
                with st.expander("Show Full Transcript"):
                    for segment in transcript_data["content"]["segments"]:
                        st.markdown(f"**{segment['speaker']}** ({segment['start']:.1f}s - {segment['end']:.1f}s):")
                        st.markdown(f"> {segment['text']}")

                # Display metadata
                st.header("Meeting Information")
                st.write(f"- **Total Speakers:** {transcript_data['content']['metadata']['total_speakers']}")
                st.write(f"- **Processing Date:** {transcript_data['content']['metadata']['processed_at']}")
                st.write(f"- **Original Filename:** {transcript_data['content']['metadata']['filename']}")

                # Placeholder for future features
                st.header("Key Decisions")
                st.info("Key decisions extraction coming soon!")

                st.header("Action Items")
                st.info("Action items extraction coming soon!")