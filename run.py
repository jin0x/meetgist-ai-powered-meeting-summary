import os
from src.transcriber import LemurTranscriber
from config import ASSEMBLYAI_API_KEY

def main():
    print("Starting transcription process...")
    
    # Initialize the transcriber
    transcriber = LemurTranscriber(ASSEMBLYAI_API_KEY)
    
    # Audio file path
    audio_file_path = "D:\\02-consolidated.wav"  # Update this path
    print(f"Processing audio file: {audio_file_path}")
    
    try:
        # Verify file exists
        if not os.path.exists(audio_file_path):
            print(f"Error: Audio file not found at {audio_file_path}")
            return
            
        # Transcribe the audio
        result = transcriber.transcribe(
            audio_path=audio_file_path,
            output_path="transcript.json"
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