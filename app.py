import streamlit as st
from pathlib import Path
from src.core.audio_transcriber import AudioTranscriber
from src.core.meeting_summarizer import MeetingSummarizer
from src.core.utils import save_uploaded_file, get_unique_filename
from src.core.db import DatabaseManager
from src.api.integrations.slack.notifier import SlackNotifier
from config import ASSEMBLYAI_API_KEY, IBM_API_KEY, IBM_PROJECT_ID
from src.synthetic.streamlit_component import render_synthetic_meeting_generator
from src.synthetic.meeting_generator import SyntheticMeetingGenerator

# Enhanced page configuration
st.set_page_config(
    page_title="MeetGist - Meeting Summary & Decision Tracker",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    local_css("styles.css")
except FileNotFoundError:
    st.warning("⚠️ styles.css not found. Using default styling.")

# Initialize session state
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Instructions"

# Initialize components with improved error handling
if 'initialization_error' not in st.session_state:
    st.session_state.initialization_error = None

try:
    with st.spinner("📥 Initializing application components..."):
        if 'transcriber' not in st.session_state:
            st.session_state.transcriber = AudioTranscriber(ASSEMBLYAI_API_KEY)

        if 'db' not in st.session_state:
            st.session_state.db = DatabaseManager()

        if 'summarizer' not in st.session_state:
            st.session_state.summarizer = MeetingSummarizer(
                api_key=IBM_API_KEY,
                project_id=IBM_PROJECT_ID,
                space_id=None
            )

        if 'slack_notifier' not in st.session_state:
            st.session_state.slack_notifier = SlackNotifier()

        if 'synthetic_generator' not in st.session_state:
            st.session_state.synthetic_generator = SyntheticMeetingGenerator(
                api_key=IBM_API_KEY,
                project_id=IBM_PROJECT_ID
            )
except Exception as e:
    st.session_state.initialization_error = str(e)

# Display initialization error if any
if st.session_state.initialization_error:
    st.error(f"🚨 Application initialization failed: {st.session_state.initialization_error}")
    st.stop()

# Enhanced sidebar navigation
with st.sidebar:
    st.title("📋 Navigation")
    st.markdown("---")

    tabs = ["Instructions", "Transcript Management", "Generate Summary"]
    icons = ["📚", "🎙️", "✨"]

    tab = st.radio(
        "Select Section",
        tabs,
        format_func=lambda x: f"{icons[tabs.index(x)]} {x}",
        index=tabs.index(st.session_state.current_tab)
    )

    st.session_state.current_tab = tab

    st.markdown("---")
    with st.expander("ℹ️ Quick Help"):
        st.markdown("""
        **Navigation Guide:**
        1. Start with Instructions
        2. Move to Transcript Management
        3. Generate Summary when ready

        Need help? Contact support@meetgist.com
        """)

# Instructions Tab
if tab == "Instructions":
    st.session_state.current_tab = "Instructions"

    st.title("🎯 Welcome to MeetGist")
    st.markdown("---")

    st.markdown("""
    > Transform your meetings into actionable insights with our powerful toolset.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎯 Key Features")
        st.markdown("""
        - **Audio Transcription:** Convert recordings to text
        - **Text Processing:** Handle existing transcripts
        - **Smart Summaries:** Extract key points
        - **Decision Tracking:** Never miss action items
        """)

    with col2:
        st.markdown("### 🚀 Getting Started")
        st.markdown("""
        1. **Upload Content:** Audio files or text transcripts
        2. **Process Data:** Automatic transcription and formatting
        3. **Generate Insights:** Summaries and key points
        4. **Share Results:** Integration with Slack
        """)

    st.markdown("---")
    if st.button("🎯 Begin Your Journey", use_container_width=True):
        st.session_state.current_tab = "Transcript Management"
        st.rerun()

# Transcript Management Tab
elif tab == "Transcript Management":
    st.session_state.current_tab = "Transcript Management"

    st.title("🎙️ Transcript Management")
    st.markdown("---")

    # Input type selection with enhanced UI
    upload_type = st.radio(
        "Choose Your Input Method",
        ["Audio File", "Text Input", "Generate Synthetic Meeting"],
        horizontal=True,
        format_func=lambda x: {
            "Audio File": "🎵 Audio File",
            "Text Input": "📝 Text Input",
            "Generate Synthetic Meeting": "🤖 Synthetic Meeting"
        }[x]
    )

    # Context-aware helper text
    help_texts = {
        "Audio File": "Upload audio recordings (WAV/MP3) for automatic transcription",
        "Text Input": "Paste existing meeting transcript text",
        "Generate Synthetic Meeting": "Create a test meeting transcript"
    }
    st.info(f"ℹ️ {help_texts[upload_type]}")

    # Audio File Upload Section
    if upload_type == "Audio File":
        col1, col2 = st.columns([2, 1])

        with col1:
            uploaded_file = st.file_uploader(
                "📁 Upload Audio File",
                type=["wav", "mp3"],
                help="Supported formats: WAV, MP3"
            )
            if uploaded_file:
                st.success(f"✅ File uploaded: {uploaded_file.name}")

        with col2:
            meeting_title = st.text_input(
                "📝 Meeting Title",
                placeholder="e.g., Team Sync - Feb 2025",
                help="A descriptive name for your meeting"
            )

        if uploaded_file and meeting_title:
            if st.button("🚀 Start Transcription", use_container_width=True):
                with st.spinner("🔄 Processing audio file..."):
                    try:
                        # Save uploaded file
                        file_path, error = save_uploaded_file(uploaded_file)
                        if error:
                            st.error(f"❌ Error saving file: {error}")
                            st.stop()

                        # Create transcripts directory
                        transcripts_dir = Path("transcripts")
                        transcripts_dir.mkdir(exist_ok=True)

                        # Generate output path
                        safe_title = "".join(c if c.isalnum() else "_" for c in meeting_title)
                        output_path = get_unique_filename(f"transcripts/{safe_title}.json")

                        # Progress indicators
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        # Transcription process
                        status_text.text("🎯 Starting transcription...")
                        progress_bar.progress(25)

                        result = st.session_state.transcriber.transcribe(
                            audio_path=file_path,
                            meeting_title=meeting_title,
                            output_path=output_path
                        )

                        progress_bar.progress(75)
                        status_text.text("💾 Saving to database...")

                        # Save to database
                        saved_transcript = st.session_state.db.save_transcript(
                            title=meeting_title,
                            content=result["plain"],
                            source_type=result["source_type"]
                        )

                        progress_bar.progress(100)
                        status_text.empty()

                        if saved_transcript:
                            st.success("✅ Transcription completed successfully!")

                            with st.expander("📋 View Transcript Details"):
                                st.subheader("Preview:")
                                preview_text = result["plain"].split("\n\n")[:3]
                                for line in preview_text:
                                    st.markdown(f"> {line}")

                                st.info("""
                                📂 **Storage Location:**
                                - Database (for application use)
                                - Backup JSON file: {output_path}
                                """)
                        else:
                            st.error("❌ Failed to save transcript to database")
                            st.warning(f"💾 Backup saved to: {output_path}")

                    except Exception as e:
                        st.error(f"❌ Transcription failed: {str(e)}")
                        st.error("Please try again or contact support if the issue persists.")

                    finally:
                        # Clean up
                        if file_path and Path(file_path).exists():
                            Path(file_path).unlink()

    # Text Input Section
    elif upload_type == "Text Input":
        col1, col2 = st.columns([2, 1])

        with col1:
            text_transcript = st.text_area(
                "📝 Paste Text Transcript",
                placeholder="Paste your meeting transcript here...",
                height=300,
                help="Copy and paste your existing transcript"
            )

        with col2:
            meeting_title = st.text_input(
                "📌 Meeting Title",
                placeholder="e.g., Product Review",
                help="A descriptive name for your meeting"
            )

        if meeting_title and text_transcript:
            if st.button("💾 Save Transcript", use_container_width=True):
                with st.spinner("🔄 Processing text..."):
                    try:
                        saved_transcript = st.session_state.db.save_transcript(
                            title=meeting_title,
                            content=text_transcript,
                            source_type='text'
                        )

                        if saved_transcript:
                            st.success("✅ Text transcript saved successfully!")
                        else:
                            st.error("❌ Failed to save transcript")

                    except Exception as e:
                        st.error(f"❌ Processing failed: {str(e)}")

        # Synthetic Meeting Generation
        else:
            render_synthetic_meeting_generator(
                generator=st.session_state.synthetic_generator,
                save_callback=st.session_state.db.save_transcript
            )

        # Display existing transcripts
        st.markdown("---")
        st.subheader("📚 Existing Transcripts")

        transcripts = st.session_state.db.get_all_transcripts()

        if transcripts:
            transcript_data = {
                "Meeting Title": [],
                "Source Type": [],
                "Created At": []
            }

            for transcript in transcripts:
                transcript_data["Meeting Title"].append(transcript["meeting_title"])
                transcript_data["Source Type"].append(
                    {"audio": "🎵", "text": "📝", "generated": "🤖"}
                    .get(transcript["source_type"], "") + " " +
                    transcript["source_type"].title()
                )
                transcript_data["Created At"].append(
                    transcript["created_at"].split("T")[0]
                )

            st.table(transcript_data)
        else:
            st.info("🔍 No transcripts available yet. Start by uploading an audio file or text!")

    # Generate Summary Tab
    elif tab == "Generate Summary":
        st.session_state.current_tab = "Generate Summary"

        st.title("✨ Generate Summary")
        st.markdown("---")

        # Get all transcripts
        transcripts = st.session_state.db.get_all_transcripts()

        if not transcripts:
            st.warning("⚠️ No transcripts available for summarization")
            if st.button("📝 Add New Transcript"):
                st.session_state.current_tab = "Transcript Management"
                st.rerun()
        else:
            st.subheader("📋 Select Transcript")

            # Enhanced transcript selection
            transcript_options = {t["meeting_title"]: t["id"] for t in transcripts}
            selected_title = st.selectbox(
                "Choose a transcript to summarize",
                list(transcript_options.keys()),
                format_func=lambda x: f"📄 {x}"
            )
            selected_id = transcript_options[selected_title]

            # Check for existing summary
            existing_summary = st.session_state.db.get_summary_by_transcript_id(selected_id)

            if existing_summary:
                st.success("✅ Summary available!")

                with st.expander("📊 Meeting Summary", expanded=True):
                    st.markdown("### 📝 Overview")
                    st.write(existing_summary["summary_text"])

                    if existing_summary["key_decisions"]:
                        st.markdown("### 🎯 Key Decisions")
                        for decision in existing_summary["key_decisions"]:
                            st.markdown(f"- {decision}")

                    if existing_summary["action_items"]:
                        st.markdown("### ✅ Action Items")
                        for action in existing_summary["action_items"]:
                            st.markdown(f"- {action}")

                if st.button("🔄 Regenerate Summary"):
                    with st.spinner("🔄 Regenerating summary..."):
                        try:
                            transcript = st.session_state.db.get_transcript_by_id(selected_id)
                            if not transcript:
                                st.error("❌ Failed to retrieve transcript")
                                st.stop()

                            summary_result = st.session_state.summarizer.generate_summary(
                                transcript_data=transcript["content"],
                                transcript_id=selected_id
                            )

                            updated_summary = st.session_state.db.save_summary(
                                transcript_id=selected_id,
                                summary_text=summary_result["summary_text"],
                                key_decisions=summary_result["key_decisions"],
                                action_items=summary_result["action_items"]
                            )


                            if updated_summary:
                                st.success("✅ Summary regenerated successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to save regenerated summary")

                        except Exception as e:
                            st.error(f"❌ Failed to regenerate summary: {str(e)}")

            elif st.button("✨ Generate Summary", use_container_width=True):
                with st.spinner("🔄 Generating summary..."):
                    try:
                        # Progress tracking
                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        # Get transcript
                        status_text.text("📄 Retrieving transcript...")
                        progress_bar.progress(20)

                        transcript = st.session_state.db.get_transcript_by_id(selected_id)
                        if not transcript:
                            st.error("❌ Failed to retrieve transcript")
                            st.stop()

                        # Generate summary
                        status_text.text("🤖 Analyzing content...")
                        progress_bar.progress(40)

                        summary_result = st.session_state.summarizer.generate_summary(
                            transcript_data=transcript["content"],
                            transcript_id=selected_id
                        )

                        status_text.text("💾 Saving summary...")
                        progress_bar.progress(70)

                        # Save to database
                        saved_summary = st.session_state.db.save_summary(
                            transcript_id=selected_id,
                            summary_text=summary_result["summary_text"],
                            key_decisions=summary_result["key_decisions"],
                            action_items=summary_result["action_items"]
                        )

                        if saved_summary:
                            progress_bar.progress(85)
                            status_text.text("📤 Sending to Slack...")

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
                                progress_bar.progress(100)
                                status_text.empty()

                                st.success("✨ Summary generated and saved!")
                                st.success("📤 Summary sent to Slack!")
                            else:
                                st.session_state.db.save_notification(
                                    transcript_id=selected_id,
                                    channel="SLACK",
                                    status="FAILED"
                                )
                                progress_bar.progress(100)
                                status_text.empty()

                                st.success("✨ Summary generated and saved!")
                                st.warning("⚠️ Failed to send summary to Slack")

                            # Display the new summary
                            with st.expander("📊 Generated Summary", expanded=True):
                                st.markdown("### 📝 Overview")
                                st.write(saved_summary["summary_text"])

                                if saved_summary["key_decisions"]:
                                    st.markdown("### 🎯 Key Decisions")
                                    for decision in saved_summary["key_decisions"]:
                                        st.markdown(f"- {decision}")

                                if saved_summary["action_items"]:
                                    st.markdown("### ✅ Action Items")
                                    for action in saved_summary["action_items"]:
                                        st.markdown(f"- {action}")

                            # Optional feedback
                            with st.expander("📝 Provide Feedback", expanded=False):
                                st.markdown("""
                                How was the summary quality? Help us improve!
                                """)
                                feedback = st.radio(
                                    "Rate the summary:",
                                    ["👍 Good", "👎 Needs Improvement"],
                                    horizontal=True
                                )
                                if feedback:
                                    st.success("Thank you for your feedback!")

                        else:
                            st.error("❌ Failed to save summary")

                    except Exception as e:
                        st.error(f"❌ Failed to generate summary: {str(e)}")
                        print(f"Error details: {str(e)}")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Made with ❤️ by MeetGist Team | Need help? Contact support@meetgist.com</p>
        </div>
        """,
        unsafe_allow_html=True
    )