import os
import json
from datetime import datetime
from src.summarizer import MeetingSummarizer
from config import IBM_API_KEY, IBM_PROJECT_ID

def get_unique_filename(base_name: str) -> str:
    """Generate a unique filename with timestamp"""
    name, ext = os.path.splitext(base_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{timestamp}{ext}"

def main():
    print("Starting summary generation process...")
    
    # Initialize the summarizer
    summarizer = MeetingSummarizer(
        api_key=IBM_API_KEY,
        project_id=IBM_PROJECT_ID,
        space_id=None
    )
    
    # Get transcript file path from user input
    transcript_path = input("Enter the path to your transcript JSON file: ")
    print(f"Processing transcript file: {transcript_path}")
    
    try:
        # Verify file exists
        if not os.path.exists(transcript_path):
            print(f"Error: Transcript file not found at {transcript_path}")
            return
        
        # Read the transcript file
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_data = json.load(f)
        
        # Generate unique output filename
        summary_output = get_unique_filename("summary.json")
        
        print("\nGenerating summary...")
        # Generate summary
        summary_result = summarizer.generate_summary(transcript_data)
        
        # Save summary to file
        with open(summary_output, 'w', encoding='utf-8') as f:
            json.dump(summary_result, f, indent=2, ensure_ascii=False)
        print("✓ Summary generated successfully")
        
        # Print preview
        print("\nSummary Preview:")
        print("-" * 50)
        print(f"Summary Text: {summary_result['summary_text'][:200]}...")
        print("\nKey Decisions:")
        print(summary_result['key_decisions'])
        print("\nAction Items:")
        print(summary_result['action_items'])
        
        print(f"\nFull summary saved to: {summary_output}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 