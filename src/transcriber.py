import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import assemblyai as aai

class LemurTranscriber:
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

    def transcribe(self, audio_path: str, output_path: str = None) -> Dict[str, Any]:
        """Transcribe audio file using Lemur"""
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            print(f"Starting transcription of: {audio_path}")
            transcript = self.transcriber.transcribe(audio_path)

            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"Transcription failed: {transcript.error}")

            # Format the result
            result = {
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "filename": Path(audio_path).name,
                    "total_speakers": len(set(u.speaker for u in transcript.utterances))
                },
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

            if output_path:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\nTranscript saved to {output_path}")

            return result

        except Exception as e:
            print(f"\nError in transcription: {str(e)}")
            raise
