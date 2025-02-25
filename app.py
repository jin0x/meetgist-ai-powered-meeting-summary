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

    # Add custom CSS to hide the select section container
    # st.markdown("""
    #     <style>
    #     div[data-testid="stSelectbox"] {
    #         display: none;
    #     }
    #     </style>
    # """, unsafe_allow_html=True)

    tabs = ["Instructions", "Transcript Management", "Generate Summary"]
    icons = ["📚", "🎙️", "✨"]

    selected_tab = st.radio(
        label="Navigation Options",  # This won't be visible but helps with accessibility
        options=tabs,
        format_func=lambda x: f"{icons[tabs.index(x)]} {x}",
        index=tabs.index(st.session_state.current_tab),
        key="nav_radio",
        label_visibility="collapsed"  # This hides the label
    )

    st.session_state.current_tab = selected_tab

    st.markdown("---")
    with st.expander("ℹ️ Quick Help"):
        st.markdown("""
        **Navigation Guide:**
        1. Start with Instructions
        2. Move to Transcript Management
        3. Generate Summary when ready

        Interested for the demo? Contact john.leskas@gmail.com
        """)

# Main content area based on selected tab
if selected_tab == "Instructions":
    st.title("💬 Welcome to MeetGist")
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

elif selected_tab == "Transcript Management":
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

    if upload_type == "Audio File":
        col1, col2 = st.columns([2, 1])
        with col1:
            uploaded_file = st.file_uploader(
                "📁 Upload Audio File",
                type=["wav", "mp3"],
                help="Supported formats: WAV, MP3"
            )
        with col2:
            meeting_title = st.text_input(
                "📝 Meeting Title",
                placeholder="e.g., Team Sync - Feb 2024"
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
                placeholder="e.g., Product Review"
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

    else:  # Generate Synthetic Meeting
        # Use the streamlit component for synthetic meeting generation
        try:
            render_synthetic_meeting_generator(
                generator=st.session_state.synthetic_generator,
                save_callback=lambda title, content, source_type: st.session_state.db.save_transcript(
                    title=title,
                    content=content,
                    source_type=source_type
                )
            )
        except Exception as e:
            st.error(f"❌ Failed to generate synthetic meeting: {str(e)}")
            st.error("Please check your IBM API credentials and try again.")

    # Display existing transcripts
    st.markdown("---")
    st.subheader("📚 Existing Transcripts")

    transcripts = st.session_state.db.get_all_transcripts()
    if transcripts:
        for transcript in transcripts:
            with st.expander(f"📄 {transcript['meeting_title']}"):
                st.write(f"Created: {transcript['created_at'].split('T')[0]}")
                st.write(f"Type: {transcript['source_type'].title()}")
                if st.button("View Summary", key=f"summary_{transcript['id']}"):
                    st.session_state.current_tab = "Generate Summary"
                    st.rerun()
    else:
        st.info("🔍 No transcripts available yet")

elif selected_tab == "Generate Summary":
    st.title("✨ Generate Summary")
    st.markdown("---")

    try:
        transcripts = st.session_state.db.get_all_transcripts()

        if not transcripts:
            st.warning("⚠️ No transcripts available")
            if st.button("➕ Add New Transcript"):
                st.session_state.current_tab = "Transcript Management"
                st.rerun()
        else:
            # Create dropdown for transcript selection
            selected_title = st.selectbox(
                "📋 Select a transcript to summarize",
                options=[t["meeting_title"] for t in transcripts],
                key="transcript_selector"
            )

            # Find the selected transcript
            selected_transcript = next(t for t in transcripts if t["meeting_title"] == selected_title)
            selected_id = selected_transcript["id"]

            # Check for existing summary
            existing_summary = st.session_state.db.get_summary_by_transcript_id(selected_id)

            if existing_summary:
                # Display existing summary without generate button
                st.success("✅ Summary available!")
                st.markdown("### 📝 Overview")
                st.write(existing_summary["summary_text"])

                if existing_summary.get("key_decisions"):
                    st.markdown("### 🎯 Key Decisions")
                    for decision in existing_summary["key_decisions"]:
                        st.markdown(f"- {decision}")

                if existing_summary.get("action_items"):
                    st.markdown("### ✅ Action Items")
                    for action in existing_summary["action_items"]:
                        st.markdown(f"- {action}")

                # Option to regenerate at the bottom
                if st.button("🔄 Regenerate Summary", type="secondary", use_container_width=True):
                    with st.spinner("🔄 Regenerating summary..."):
                        try:
                            transcript = st.session_state.db.get_transcript_by_id(selected_id)
                            if transcript:
                                summary_result = st.session_state.summarizer.generate_summary(
                                    transcript_data=transcript["content"],
                                    transcript_id=selected_id
                                )

                                saved_summary = st.session_state.db.save_summary(
                                    transcript_id=selected_id,
                                    summary_text=summary_result["summary_text"],
                                    key_decisions=summary_result["key_decisions"],
                                    action_items=summary_result["action_items"]
                                )

                                if saved_summary:
                                    st.success("✅ Summary regenerated successfully!")
                                    st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            else:
                # Show generate button only when no summary exists
                st.info("ℹ️ No summary available for this transcript")
                if st.button("✨ Generate Summary", type="primary", use_container_width=True):
                    with st.spinner("🔄 Generating summary..."):
                        try:
                            transcript = st.session_state.db.get_transcript_by_id(selected_id)
                            if transcript:
                                summary_result = st.session_state.summarizer.generate_summary(
                                    transcript_data=transcript["content"],
                                    transcript_id=selected_id
                                )

                                saved_summary = st.session_state.db.save_summary(
                                    transcript_id=selected_id,
                                    summary_text=summary_result["summary_text"],
                                    key_decisions=summary_result["key_decisions"],
                                    action_items=summary_result["action_items"]
                                )

                                if saved_summary:
                                    st.success("✅ Summary generated successfully!")
                                    st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")

    except Exception as e:
        st.error(f"❌ Database error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Made with ❤️ by Radiant Minds | Interested for the demo? Contact john.leskas@gmail.com
    </div>
    """,
    unsafe_allow_html=True
)