import json
import uuid
import requests
from typing import Dict, Any, List
from datetime import datetime

class MeetingSummarizer:
    def __init__(self, api_key: str, project_id: str, space_id: str = None):
        """Initialize the summarizer with IBM watsonx.ai credentials"""
        self.api_key = api_key
        self.project_id = project_id
        self.space_id = space_id

        # Get IAM token first
        self.iam_token = self._get_iam_token()

        self.base_url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.iam_token}"
        }

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
        response.raise_for_status()

        return response.json()["access_token"]

    def generate_summary(self, transcript_data: Dict[str, Any], transcript_id: str = None) -> Dict[str, Any]:
        """Generate meeting summary using watsonx.ai"""
        try:
            print("\nProcessing transcript data...")

            # Get the full text from transcript
            transcript_text = self._prepare_transcript_text(transcript_data)
            print(f"\nTranscript length: {len(transcript_text)} characters")

            # Generate main summary
            summary_text = self._generate_text(self._create_summary_prompt(transcript_text))

            # Generate and format key decisions as JSONB array
            decisions_text = self._generate_text(self._create_decisions_prompt(transcript_text))
            decisions_list = self._convert_bullet_points_to_array(decisions_text)

            # Generate and format action items as JSONB array
            actions_text = self._generate_text(self._create_actions_prompt(transcript_text))
            actions_list = self._convert_bullet_points_to_array(actions_text)

            # Create the summary in database-compatible format
            summary = {
                'transcript_id': transcript_id,
                'summary_text': summary_text,
                'key_decisions': decisions_list,
                'action_items': actions_list
            }

            print("\nGenerated Summary:")
            print(json.dumps(summary, indent=2))

            return summary

        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            raise

    def _convert_bullet_points_to_array(self, text: str) -> List[str]:
        """Convert bullet point text to array of strings"""
        # Split by common bullet point indicators
        lines = text.split('\n')
        items = []

        for line in lines:
            # Remove common bullet point markers and whitespace
            line = line.strip()
            line = line.lstrip('•').lstrip('-').lstrip('*').strip()
            if line:  # Only add non-empty lines
                items.append(line)

        return items

    def _generate_text(self, prompt: str) -> str:
        """Generate text using the API"""
        payload = {
            "input": prompt,
            "parameters": {
                "decoding_method": "greedy",
                "max_new_tokens": 500,
                "min_new_tokens": 50,
                "repetition_penalty": 1,
                "temperature": 0.7
            },
            "model_id": "ibm/granite-3-8b-instruct",
            "project_id": self.project_id
        }

        response = requests.post(
            self.base_url,
            headers=self.headers,
            json=payload
        )

        if response.status_code != 200:
            raise Exception("API request failed: " + str(response.text))

        response_data = response.json()
        return response_data.get('results', [{'generated_text': ''}])[0].get('generated_text', '').strip()

    def _create_summary_prompt(self, transcript_text: str) -> str:
        """Create prompt for main summary"""
        return f"""Please provide a concise summary of the following meeting transcript:

Transcript:
{transcript_text}

Focus on the main points discussed and provide a clear, organized summary."""

    def _create_decisions_prompt(self, transcript_text: str) -> str:
        """Create prompt for key decisions"""
        return f"""From the following meeting transcript, extract only the key decisions made during the meeting.
Format each decision as a bullet point starting with '- '.

Transcript:
{transcript_text}

Key Decisions:"""

    def _create_actions_prompt(self, transcript_text: str) -> str:
        """Create prompt for action items"""
        return f"""From the following meeting transcript, extract only the specific action items and next steps assigned.
Format each action item as a bullet point starting with '- ', including who is responsible (if mentioned) and any deadlines.

Transcript:
{transcript_text}

Action Items:"""

    def _prepare_transcript_text(self, transcript_data: Dict[str, Any]) -> str:
        """Convert transcript data to formatted text for processing"""
        try:
            # Handle structured content (from our formatter)
            if isinstance(transcript_data, dict) and 'content' in transcript_data:
                return transcript_data['content']

            # Handle segment-based transcripts
            elif isinstance(transcript_data, dict) and 'segments' in transcript_data:
                full_text = []
                for segment in transcript_data['segments']:
                    speaker = segment.get('speaker', 'Unknown Speaker')
                    text = segment.get('text', '')
                    full_text.append(f"{speaker}: {text}")
                return "\n".join(full_text)

            # Handle plain text
            elif isinstance(transcript_data, dict) and 'text' in transcript_data:
                return transcript_data['text']

            # Handle string input
            elif isinstance(transcript_data, str):
                return transcript_data

            else:
                print("Warning: Unexpected transcript format")
                return str(transcript_data)

        except Exception as e:
            print(f"Error in prepare_transcript_text: {e}")
            return str(transcript_data)