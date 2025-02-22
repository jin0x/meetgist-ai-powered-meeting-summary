import os
from datetime import datetime
from src.transcriber import LemurTranscriber
from config import ASSEMBLYAI_API_KEY

def get_unique_filename(base_path):
    # Get the directory and base filename
    directory = os.path.dirname(base_path) or '.'
    base_name, ext = os.path.splitext(os.path.basename(base_path))
    
    # Add timestamp to make it unique
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{base_name}_{timestamp}{ext}"
    
    return os.path.join(directory, new_filename)

def main():
    print("Starting transcription process...")
    
    # Initialize the transcriber
    transcriber = LemurTranscriber(ASSEMBLYAI_API_KEY)
    
    # Audio file path
    audio_file_path = "D:\\Planning Meeting 2025-01-23.mp3"
    print(f"Processing audio file: {audio_file_path}")
    
    try:
        # Verify file exists
        if not os.path.exists(audio_file_path):
            print(f"Error: Audio file not found at {audio_file_path}")
            return
        
        # Generate unique output filename
        output_path = get_unique_filename("transcript.json")
        print(f"Output will be saved to: {output_path}")
            
        # Transcribe the audio
        result = transcriber.transcribe(
            audio_path=audio_file_path,
            output_path=output_path
        )
        
        # Print preview
        print("\nTranscription preview:")
        segments = result["segments"][:3]  # First 3 segments
        for segment in segments:
            print(f"\n{segment['speaker']} ({segment['start']:.1f}s - {segment['end']:.1f}s):")
            print(f"  {segment['text']}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 