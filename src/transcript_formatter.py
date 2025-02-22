import re
from typing import List, Dict, Union, Optional
import json

class TranscriptFormatter:
    def __init__(self):
        # Common speaker patterns in text
        self.speaker_patterns = [
            r'^([A-Za-z\s]+):\s',  # "John Smith: Hello"
            r'^([A-Z][a-z]+):\s',  # "John: Hello"
            r'\[([^\]]+)\]',       # "[John Smith] Hello"
            r'\(([^)]+)\)',        # "(John Smith) Hello"
        ]

    def format_transcript(self, content: Union[str, Dict], source_type: str) -> str:
        """
        Format transcript content based on source type.

        Args:
            content: Either raw text or AssemblyAI JSON response
            source_type: 'audio' or 'text'

        Returns:
            Formatted text with speaker labels
        """
        if source_type == 'audio':
            return self._format_audio_transcript(content)
        else:
            return self._format_text_transcript(content)

    def _format_audio_transcript(self, content: Union[str, Dict]) -> str:
        """Format AssemblyAI transcript content."""
        try:
            # If content is string (from DB), parse it
            if isinstance(content, str):
                content = json.loads(content)

            # Extract segments
            segments = content.get('segments', [])

            # Format each segment
            formatted_lines = []
            for segment in segments:
                speaker = segment.get('speaker', 'Unknown Speaker')
                text = segment.get('text', '').strip()
                if text:  # Only add non-empty segments
                    formatted_lines.append(f"{speaker}: {text}")

            return "\n\n".join(formatted_lines)

        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            print(f"Error formatting audio transcript: {e}")
            return "Error: Could not format audio transcript"

    def _format_text_transcript(self, content: str) -> str:
        """Format raw text transcript with speaker detection."""
        if not content:
            return ""

        lines = content.split('\n')
        formatted_lines = []
        current_speaker = "Speaker A"
        speaker_counter = ord('A')  # Start with 'A'
        speakers_map = {}  # Map detected names to speaker labels

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to detect speaker
            speaker_name = None
            for pattern in self.speaker_patterns:
                match = re.match(pattern, line)
                if match:
                    speaker_name = match.group(1).strip()
                    # Remove speaker pattern from line
                    line = re.sub(pattern, '', line).strip()
                    break

            if speaker_name:
                # Use existing speaker label or create new one
                if speaker_name not in speakers_map:
                    speakers_map[speaker_name] = f"Speaker {chr(speaker_counter)}"
                    speaker_counter += 1
                current_speaker = speakers_map[speaker_name]

            formatted_lines.append(f"{current_speaker}: {line}")

        return "\n\n".join(formatted_lines)

    def _detect_speaker_change(self, line: str) -> Optional[str]:
        """
        Detect if line indicates a new speaker.
        Returns speaker name if found, None otherwise.
        """
        # Additional speaker detection logic can be added here
        # For example, checking for patterns like "Mr. Smith speaks:" or "[John]"
        return None