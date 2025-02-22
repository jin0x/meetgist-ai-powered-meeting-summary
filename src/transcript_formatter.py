from typing import Dict, Union, Optional, Any
import json
import re
from datetime import datetime
from pathlib import Path

class TranscriptFormatter:
    def __init__(self):
        self.speaker_patterns = [
            r'^([A-Za-z\s]+):\s',  # "John Smith: Hello"
            r'^([A-Z][a-z]+):\s',  # "John: Hello"
            r'\[([^\]]+)\]',       # "[John Smith] Hello"
            r'\(([^)]+)\)',        # "(John Smith) Hello"
        ]

    def format_transcript(
        self,
        content: Union[str, Dict],
        source_type: str,
        structured: bool = False,
        meeting_title: Optional[str] = None
    ) -> Union[str, Dict[str, Any]]:
        """
        Format transcript content with option for structured or plain text output.

        Args:
            content: Raw transcript content (text or AssemblyAI JSON)
            source_type: Type of source ('audio', 'text', 'generated')
            structured: Whether to return structured JSON output
            meeting_title: Title of the meeting (for metadata)

        Returns:
            Either formatted plain text or structured JSON output
        """
        formatted_text = self._format_content(content, source_type)

        if not structured:
            return formatted_text

        # Create structured output
        total_speakers = len(set(re.findall(r'Speaker [A-Z]:', formatted_text)))

        return {
            "metadata": {
                "processed_at": datetime.now().isoformat(),
                "filename": meeting_title if meeting_title else "Unknown",
                "total_speakers": total_speakers,
                "source_type": source_type
            },
            "content": formatted_text
        }

    def _format_content(self, content: Union[str, Dict], source_type: str) -> str:
        """Internal method to format content based on source type."""
        if source_type == 'audio':
            return self._format_audio_transcript(content)
        else:
            return self._format_text_transcript(content)

    def _format_audio_transcript(self, content: Union[str, Dict]) -> str:
        """Format AssemblyAI transcript content to standardized format."""
        try:
            # Parse JSON if content is string
            if isinstance(content, str):
                content = json.loads(content)

            # Format segments
            formatted_lines = []
            for segment in content.get('segments', []):
                speaker = segment.get('speaker', 'Unknown Speaker')
                text = segment.get('text', '').strip()
                if text:
                    formatted_lines.append(f"{speaker}: {text}")

            return "\n\n".join(formatted_lines)

        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            print(f"Error formatting audio transcript: {e}")
            return "Error: Could not format audio transcript"

    def _format_text_transcript(self, content: str) -> str:
        """Format text transcript with speaker detection."""
        if not content:
            return ""

        lines = content.split('\n')
        formatted_lines = []
        current_speaker = "Speaker A"
        speaker_counter = ord('A')
        speakers_map = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect speaker
            speaker_name = None
            for pattern in self.speaker_patterns:
                match = re.match(pattern, line)
                if match:
                    speaker_name = match.group(1).strip()
                    line = re.sub(pattern, '', line).strip()
                    break

            if speaker_name:
                if speaker_name not in speakers_map:
                    speakers_map[speaker_name] = f"Speaker {chr(speaker_counter)}"
                    speaker_counter += 1
                current_speaker = speakers_map[speaker_name]

            formatted_lines.append(f"{current_speaker}: {line}")

        return "\n\n".join(formatted_lines)