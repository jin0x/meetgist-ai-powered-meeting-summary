import streamlit as st
from typing import Dict, Any
from .meeting_generator import SyntheticMeetingGenerator

def render_synthetic_meeting_generator(
    generator: SyntheticMeetingGenerator,
    save_callback: callable
) -> None:
    """Render the synthetic meeting generator component"""
    st.header("Generate Synthetic Meeting")
    
    # Get topics from generator
    topics = generator.topics['topics']
    
    # Create selection widgets
    col1, col2 = st.columns(2)
    
    with col1:
        selected_topic = st.selectbox(
            "Select Meeting Type",
            options=list(topics.keys()),
            format_func=lambda x: topics[x]['title']
        )
        
        topic_data = topics[selected_topic]
        
        num_speakers = st.slider(
            "Number of Speakers",
            min_value=topic_data['min_speakers'],
            max_value=topic_data['max_speakers'],
            value=topic_data['min_speakers']
        )
    
    with col2:
        duration = st.slider(
            "Meeting Duration (minutes)",
            min_value=30,
            max_value=120,
            value=topic_data['typical_duration']
        )
    
    # Show topic context
    st.info(f"Context: {topic_data['context']}")
    
    # Generate button
    if st.button("Generate Synthetic Meeting"):
        with st.spinner("Generating synthetic meeting transcript..."):
            try:
                # Generate the meeting
                result = generator.generate_meeting(
                    selected_topic,
                    num_speakers=num_speakers,
                    duration_minutes=duration
                )
                
                # Save using the provided callback
                saved = save_callback(
                    title=result['metadata']['filename'],
                    content=result['text'],
                    source_type='generated'
                )
                
                if saved:
                    st.success("✅ Synthetic meeting generated and saved!")
                else:
                    st.error("Failed to save synthetic meeting.")
                    
            except Exception as e:
                st.error(f"Failed to generate meeting: {str(e)}")
                print(f"Error details: {str(e)}") 