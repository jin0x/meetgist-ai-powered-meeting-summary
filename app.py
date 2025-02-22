import streamlit as st
import json
from pathlib import Path
from src.audio_transcriber import AudioTranscriber
from src.transcript_formatter import TranscriptFormatter
from src.utils import save_uploaded_file, get_unique_filename
from src.db import DatabaseManager
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
    st.session_state.transcriber = AudioTranscriber(ASSEMBLYAI_API_KEY)

# Initialize database manager in session state
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

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

                    # Transcribe with file output
                    result = st.session_state.transcriber.transcribe(
                        audio_path=file_path,
                        meeting_title=meeting_title,
                        output_path=output_path
                    )

                    # Save to database
                    saved_transcript = st.session_state.db.save_transcript(
                        title=meeting_title,
                        content=result["plain"],  # Use the plain text version for DB
                        source_type=result["source_type"]
                    )

                    if saved_transcript:
                        st.success("✅ Transcription completed and saved to both database and file!")

                        with st.expander("Show Preview"):
                            st.subheader("Transcript Preview:")
                            # Show first few lines of the formatted text
                            preview_text = result["plain"].split("\n\n")[:3]
                            for line in preview_text:
                                st.markdown(f"> {line}")

                            st.info(f"""
                            Transcript saved in two locations:
                            - Database (for application use)
                            - JSON file at: {output_path} (for backup/external use)
                            """)
                    else:
                        st.error("Failed to save transcript to database.")
                        st.warning(f"However, the transcript was saved to file at: {output_path}")

                except Exception as e:
                    st.error(f"Transcription failed: {str(e)}")
                    st.error("Please try again or contact support if the problem persists.")
                finally:
                    # Clean up uploaded file
                    if file_path and Path(file_path).exists():
                        Path(file_path).unlink()

    elif upload_type == "Text Transcript":
        col1, col2 = st.columns([2, 1])
        with col1:
            text_transcript = st.text_area(
                "Paste Text Transcript",
                placeholder="Paste your text transcript here...",
                height=300
            )
        with col2:
            meeting_title = st.text_input(
                "Meeting Title",
                placeholder="Enter a title for this meeting",
                help="This will help identify the transcript later"
            )

        if meeting_title and text_transcript and st.button("Process Text"):
            try:
                # Save to database
                saved_transcript = st.session_state.db.save_transcript(
                    title=meeting_title,
                    content=text_transcript,
                    source_type='text'
                )

                if saved_transcript:
                    st.success("✅ Text transcript saved successfully!")
                else:
                    st.error("Failed to save transcript to database.")

            except Exception as e:
                st.error(f"Failed to process transcript: {str(e)}")

    # List of Saved Transcripts
    st.header("Saved Transcripts")
    transcripts = st.session_state.db.get_all_transcripts()

    if transcripts:
        transcript_data = {
            "Meeting Title": [],
            "Source Type": [],
            "Created At": []
        }

        for transcript in transcripts:
            transcript_data["Meeting Title"].append(transcript["meeting_title"])
            transcript_data["Source Type"].append(transcript["source_type"])
            transcript_data["Created At"].append(
                transcript["created_at"].split("T")[0]  # Show only date part
            )

        st.table(transcript_data)
    else:
        st.info("No transcripts available yet. Upload an audio file or text to get started!")

# Generate Summary Tab
elif tab == "Generate Summary":
    st.session_state.current_tab = "Generate Summary"
    st.title("Generate Summary")

    # Get all transcripts from database
    transcripts = st.session_state.db.get_all_transcripts()

    if not transcripts:
        st.warning("No transcripts available. Please upload and process a transcript first.")
        if st.button("Go to Transcript Management"):
            st.session_state.current_tab = "Transcript Management"
            st.rerun()
    else:
        # Transcript Selection
        st.header("Select Transcript")
        transcript_options = {t["meeting_title"]: t["id"] for t in transcripts}
        selected_title = st.selectbox("Choose a transcript", list(transcript_options.keys()))
        selected_id = transcript_options[selected_title]

        # Check if summary exists
        existing_summary = st.session_state.db.get_summary_by_transcript_id(selected_id)

        if existing_summary:
            st.success("Summary already exists!")

            st.header("Meeting Summary")
            st.write(existing_summary["summary_text"])

            if existing_summary["key_decisions"]:
                st.header("Key Decisions")
                st.write(existing_summary["key_decisions"])

            if existing_summary["action_items"]:
                st.header("Action Items")
                st.write(existing_summary["action_items"])

            # Option to regenerate
            if st.button("Regenerate Summary"):
                st.info("Summary regeneration will be implemented in future updates.")

        elif st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                # Get full transcript
                transcript = st.session_state.db.get_transcript_by_id(selected_id)
                if transcript:
                    try:
                        transcript_content = json.loads(transcript["content"])
                        # Extract full text for summary generation
                        full_text = transcript_content["text"] if "text" in transcript_content else transcript_content

                        # TODO: Implement actual summary generation
                        # For now, just save a placeholder summary
                        summary = st.session_state.db.save_summary(
                            transcript_id=selected_id,
                            summary_text=f"Summary will be implemented soon. Full text: {full_text[:100]}...",
                            key_decisions="Key decisions will be extracted in future updates.",
                            action_items="Action items will be extracted in future updates."
                        )

                        if summary:
                            st.success("Summary generated and saved!")
                            st.rerun()  # Refresh to show the new summary
                        else:
                            st.error("Failed to save summary.")
                    except json.JSONDecodeError:
                        # Handle plain text transcripts
                        summary = st.session_state.db.save_summary(
                            transcript_id=selected_id,
                            summary_text=f"Summary will be implemented soon. Preview: {transcript['content'][:100]}...",
                            key_decisions="Key decisions will be extracted in future updates.",
                            action_items="Action items will be extracted in future updates."
                        )

                        if summary:
                            st.success("Summary generated and saved!")
                            st.rerun()
                        else:
                            st.error("Failed to save summary.")
                else:
                    st.error("Failed to retrieve transcript from database.")