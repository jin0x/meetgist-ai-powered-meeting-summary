import yaml
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import requests

class SyntheticMeetingGenerator:
    def __init__(self, api_key: str, project_id: str):
        """Initialize the synthetic meeting generator with IBM Granite credentials"""
        self.api_key = api_key
        self.project_id = project_id
        self.topics = self._load_topics()
        # Get initial IAM token
        self.iam_token = self._get_iam_token()

    def _get_iam_token(self) -> str:
        """Get IAM token using API key"""
        iam_url = "https://iam.cloud.ibm.com/identity/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key
        }

        response = requests.post(iam_url, headers=headers, data=data)
        if response.status_code != 200:
            raise Exception(f"Failed to get IAM token: {response.text}")

        return response.json()["access_token"]

    def _load_topics(self) -> Dict[str, Any]:
        """Load meeting topics from YAML file"""
        topics_path = Path(__file__).parent / "meeting_topics.yaml"
        with open(topics_path, 'r') as f:
            return yaml.safe_load(f)

    def generate_meeting(
        self,
        topic_key: str,
        num_speakers: Optional[int] = None,
        duration_minutes: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a synthetic meeting transcript"""
        topic_data = self.topics['topics'][topic_key]

        # Set number of speakers if not specified
        if num_speakers is None:
            num_speakers = random.randint(
                topic_data['min_speakers'],
                topic_data['max_speakers']
            )

        # Set duration if not specified
        if duration_minutes is None:
            duration_minutes = topic_data['typical_duration']

        # Generate the meeting content using IBM Granite
        meeting_content = self._generate_meeting_content(
            topic_data['context'],
            num_speakers,
            duration_minutes
        )

        # Format the meeting transcript
        return self._format_transcript(
            meeting_content,
            topic_data['title'],
            num_speakers,
            duration_minutes
        )

    def _generate_meeting_content(
        self,
        context: str,
        num_speakers: int,
        duration_minutes: int
    ) -> List[Dict[str, Any]]:
        """Generate meeting content using IBM Granite"""
        prompt = self._create_meeting_prompt(context, num_speakers, duration_minutes)

        # IBM Granite API call with proper authentication
        response = requests.post(
            "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.iam_token}"
            },
            json={
                "model_id": "google/flan-ul2",
                "input": prompt,
                "parameters": {
                    "decoding_method": "greedy",
                    "max_new_tokens": 1500,
                    "min_new_tokens": 500,
                    "temperature": 0.7
                },
                "project_id": self.project_id
            }
        )

        if response.status_code == 401:
            # Token might be expired, refresh and retry
            self.iam_token = self._get_iam_token()
            return self._generate_meeting_content(context, num_speakers, duration_minutes)
        elif response.status_code != 200:
            raise Exception(f"API request failed: {response.text}")

        # Process the generated text into segments
        generated_text = response.json()['results'][0]['generated_text']
        segments = self._parse_generated_text(generated_text, duration_minutes)

        return segments

    def _parse_generated_text(self, text: str, duration_minutes: int) -> List[Dict[str, Any]]:
        """Parse generated text into transcript segments"""
        lines = text.split('\n')
        segments = []
        current_time = 0
        time_increment = (duration_minutes * 60) / len(lines)  # Distribute time evenly

        for line in lines:
            if not line.strip():
                continue

            # Extract speaker and text
            if ':' in line:
                speaker, text = line.split(':', 1)
                speaker = speaker.strip()
                text = text.strip()

                if speaker and text:
                    segments.append({
                        "text": text,
                        "start": current_time,
                        "end": current_time + time_increment,
                        "speaker": speaker
                    })
                    current_time += time_increment

        return segments

    def _format_transcript(
        self,
        segments: List[Dict[str, Any]],
        meeting_title: str,
        num_speakers: int,
        duration_minutes: int
    ) -> Dict[str, Any]:
        """Format the generated content into the required transcript structure"""
        return {
            "metadata": {
                "processed_at": datetime.now().isoformat(),
                "filename": f"{meeting_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "total_speakers": num_speakers,
                "source_type": "synthetic"
            },
            "segments": segments,
            "text": "\n".join(seg["text"] for seg in segments)
        }

    def _create_meeting_prompt(
        self,
        context: str,
        num_speakers: int,
        duration_minutes: int
    ) -> str:
        """Create the prompt for IBM Granite"""
        return f"""Generate a realistic meeting transcript for the following context:

Context: {context}

Requirements:
- Number of speakers: {num_speakers}
- Meeting duration: {duration_minutes} minutes
- Format: Natural conversation
- Include: Opening, main discussion, conclusions
- Use speaker designations like "Speaker A:", "Speaker B:", etc.

Generate the meeting transcript with timestamps and speaker turns."""
