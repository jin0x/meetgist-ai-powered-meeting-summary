import os
import json
from typing import Dict, Any, Optional
import assemblyai as aai
from .transcript_formatter import TranscriptFormatter

class AudioTranscriber:
    def __init__(self, assemblyai_key: str):
        if not assemblyai_key:
            raise ValueError("AssemblyAI API key is missing!")

        # Configure AssemblyAI
        aai.settings.api_key = assemblyai_key

        # Configure transcription settings
        self.config = aai.TranscriptionConfig(
            speech_model=aai.SpeechModel.best,
            speaker_labels=True,
            language_detection=True
        )

        self.transcriber = aai.Transcriber(config=self.config)
        self.formatter = TranscriptFormatter()

    def transcribe(
        self,
        audio_path: str,
        meeting_title: str,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file and return formatted result.

        Args:
            audio_path: Path to audio file
            meeting_title: Title of the meeting
            output_path: Optional path to save JSON output

        Returns:
            Dictionary containing formatted transcript and metadata
        """
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            print(f"Starting transcription of: {audio_path}")
            transcript = self.transcriber.transcribe(audio_path)

            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"Transcription failed: {transcript.error}")

            # Convert AssemblyAI transcript to our format
            raw_result = {
                "segments": [
                    {
                        "text": u.text,
                        "start": u.start / 1000,  # Convert to seconds
                        "end": u.end / 1000,
                        "speaker": f"Speaker {u.speaker}"
                    }
                    for u in transcript.utterances
                ],
                "text": transcript.text
            }

            # Format the transcript
            # Get both structured (for file) and plain (for DB) versions
            formatted_structured = self.formatter.format_transcript(
                content=raw_result,
                source_type='audio',
                structured=True,
                meeting_title=meeting_title
            )

            formatted_plain = self.formatter.format_transcript(
                content=raw_result,
                source_type='audio',
                structured=False
            )

            # Save to file if output path provided
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(formatted_structured, f, indent=2, ensure_ascii=False)
                print(f"\nTranscript saved to {output_path}")

            # Return both formats for database storage and further use
            return {
                "structured": formatted_structured,
                "plain": formatted_plain,
                "source_type": "audio"
            }

        except Exception as e:
            print(f"\nError in transcription: {str(e)}")
            raise