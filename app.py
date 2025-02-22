import streamlit as st

# Page configuration (MUST BE THE FIRST STREAMLIT COMMAND)
st.set_page_config(page_title="Meeting Summary & Decision Tracker", layout="wide")

# Custom CSS for styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("styles.css")

# Initialize session state for tab navigation
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Instructions"

# Sidebar for navigation
st.sidebar.title("Navigation")
tabs = ["Instructions", "Transcript Management", "Generate Summary"]
tab = st.sidebar.radio("Go to", tabs, index=tabs.index(st.session_state.current_tab))

# Instructions Tab
if tab == "Instructions":
    st.session_state.current_tab = "Instructions"  # Update session state
    st.title("Welcome to the Meeting Summary & Decision Tracker")
    st.write("""
    This application helps you manage meeting transcripts, generate summaries, and track decisions. 
    Please follow the instructions below to get started.
    """)
    
    st.header("Instructions")
    st.write("""
    1. **Transcript Management Tab:** Upload audio or text transcripts, or generate a simulated meeting transcript.
    2. **Generate Summary Tab:** Select a saved transcript to generate a summary, key decisions, and action items.
    """)
    
    if st.button("Get Started"):
        st.session_state.current_tab = "Transcript Management"  # Update session state
        st.rerun()  # Rerun the app to reflect the change

# Transcript Management Tab
elif tab == "Transcript Management":
    st.session_state.current_tab = "Transcript Management"  # Update session state
    st.title("Transcript Management")
    
    # Upload Section
    st.header("Upload Transcript")
    upload_type = st.radio("Choose Upload Type", ["Audio File", "Text Transcript"])
    
    if upload_type == "Audio File":
        st.file_uploader("Upload Audio File (WAV/MP3)", type=["wav", "mp3"], key="audio_upload")
        if st.button("Upload Audio"):
            st.success("Audio file uploaded successfully! (Placeholder)")
    
    elif upload_type == "Text Transcript":
        text_transcript = st.text_area("Paste Text Transcript", placeholder="Paste your text transcript here...")
        if st.button("Upload Text"):
            st.success("Text transcript uploaded successfully! (Placeholder)")
    
    # Meeting Generator Section
    st.header("Generate Meeting")
    meeting_topic = st.text_input("Enter Meeting Topic or Agenda", placeholder="Enter a topic or agenda...")
    if st.button("Generate Meeting"):
        st.success("Meeting transcript generated successfully! (Placeholder)")
    
    # List of Saved Transcripts
    st.header("Saved Transcripts")
    st.write("Here is a list of saved transcripts: (Placeholder)")
    st.table({
        "Meeting Title": ["Team Sync", "Project Kickoff"],
        "Source Type": ["Audio", "Text"],
        "Timestamp": ["2023-10-01 10:00", "2023-10-02 14:30"]
    })

# Generate Summary Tab
elif tab == "Generate Summary":
    st.session_state.current_tab = "Generate Summary"  # Update session state
    st.title("Generate Summary")
    
    # Transcript Selection
    st.header("Select Transcript")
    transcript_options = ["Team Sync", "Project Kickoff"]
    selected_transcript = st.selectbox("Choose a transcript", transcript_options)
    
    if st.button("Generate Summary"):
        st.success("Summary generated successfully! (Placeholder)")
        
        # Display Summary
        st.header("Meeting Summary")
        st.write("This is a placeholder for the meeting summary. (Placeholder)")
        
        # Display Key Decisions
        st.header("Key Decisions")
        st.write("- Decision 1 (Placeholder)")
        st.write("- Decision 2 (Placeholder)")
        
        # Display Action Items
        st.header("Action Items")
        st.write("- Action 1 (Placeholder)")
        st.write("- Action 2 (Placeholder)")
        
        # Slack Notification
        if st.checkbox("Send Slack Notification"):
            st.success("Slack notification sent successfully! (Placeholder)")