import streamlit as st
from pathlib import Path
from src.audio_transcriber import AudioTranscriber
from src.meeting_summarizer import MeetingSummarizer
from src.slack_notifier import SlackNotifier
from src.utils import save_uploaded_file, get_unique_filename
from src.db import DatabaseManager
from config import ASSEMBLYAI_API_KEY, IBM_API_KEY, IBM_PROJECT_ID
from src.synthetic.streamlit_component import render_synthetic_meeting_generator
from src.synthetic.meeting_generator import SyntheticMeetingGenerator

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

# Initialize summarizer in session state
if 'summarizer' not in st.session_state:
    st.session_state.summarizer = MeetingSummarizer(
        api_key=IBM_API_KEY,
        project_id=IBM_PROJECT_ID,
        space_id=None
    )

# Initialize slack notifier in session state
if 'slack_notifier' not in st.session_state:
    st.session_state.slack_notifier = SlackNotifier()

# Initialize synthetic meeting generator in session state
if 'synthetic_generator' not in st.session_state:
    st.session_state.synthetic_generator = SyntheticMeetingGenerator(
        api_key=IBM_API_KEY,
        project_id=IBM_PROJECT_ID
    )

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

    # Upload type selection
    upload_type = st.radio(
        "Select Input Type",
        ["Audio File", "Text Input", "Generate Synthetic Meeting"],
        horizontal=True
    )

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

    elif upload_type == "Text Input":
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

    else:  # Generate Synthetic Meeting
        render_synthetic_meeting_generator(
            generator=st.session_state.synthetic_generator,
            save_callback=st.session_state.db.save_transcript
        )

    # Show existing transcripts
    st.divider()
    st.subheader("Existing Transcripts")
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
            st.success("Summary exists!")

            st.header("Meeting Summary")
            st.write(existing_summary["summary_text"])

            if existing_summary["key_decisions"]:
                st.header("Key Decisions")
                for decision in existing_summary["key_decisions"]:
                    st.markdown(f"- {decision}")

            if existing_summary["action_items"]:
                st.header("Action Items")
                for action in existing_summary["action_items"]:
                    st.markdown(f"- {action}")

            # Option to regenerate
            if st.button("Regenerate Summary"):
                with st.spinner("Regenerating summary..."):
                    try:
                        # Get transcript content
                        transcript = st.session_state.db.get_transcript_by_id(selected_id)
                        if not transcript:
                            st.error("Failed to retrieve transcript.")
                            st.stop()

                        # Generate new summary
                        summary_result = st.session_state.summarizer.generate_summary(
                            transcript_data=transcript["content"],
                            transcript_id=selected_id
                        )

                        # Save to database
                        updated_summary = st.session_state.db.save_summary(
                            transcript_id=selected_id,
                            summary_text=summary_result["summary_text"],
                            key_decisions=summary_result["key_decisions"],
                            action_items=summary_result["action_items"]
                        )

                        if updated_summary:
                            st.success("Summary regenerated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to save regenerated summary.")

                    except Exception as e:
                        st.error(f"Failed to regenerate summary: {str(e)}")

        elif st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                try:
                    # Get transcript
                    transcript = st.session_state.db.get_transcript_by_id(selected_id)
                    if not transcript:
                        st.error("Failed to retrieve transcript.")
                        st.stop()

                    # Generate summary
                    summary_result = st.session_state.summarizer.generate_summary(
                        transcript_data=transcript["content"],
                        transcript_id=selected_id
                    )

                    # Save to database
                    saved_summary = st.session_state.db.save_summary(
                        transcript_id=selected_id,
                        summary_text=summary_result["summary_text"],
                        key_decisions=summary_result["key_decisions"],
                        action_items=summary_result["action_items"]
                    )

                    if saved_summary:
                        # Send to Slack
                        slack_success = st.session_state.slack_notifier.send_meeting_summary(
                            meeting_title=selected_title,
                            summary_data=saved_summary
                        )

                        # Save notification status
                        if slack_success:
                            st.session_state.db.save_notification(
                                transcript_id=selected_id,
                                channel="SLACK",
                                status="SENT"
                            )
                        else:
                            st.session_state.db.save_notification(
                                transcript_id=selected_id,
                                channel="SLACK",
                                status="FAILED"
                            )

                        # Show success message
                        st.success("✅ Summary generated and saved!")
                        if slack_success:
                            st.success("✅ Summary sent to Slack!")
                        else:
                            st.warning("⚠️ Failed to send summary to Slack")

                        st.rerun()
                    else:
                        st.error("Failed to save summary.")

                except Exception as e:
                    st.error(f"Failed to generate summary: {str(e)}")
                    print(f"Error details: {str(e)}")