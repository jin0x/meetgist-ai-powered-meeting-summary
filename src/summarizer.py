import json
import uuid
import requests
from typing import Dict, Any
from datetime import datetime

class MeetingSummarizer:
    def __init__(self, api_key: str, project_id: str, space_id: str):
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

    def generate_summary(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate meeting summary using watsonx.ai"""
        try:
            # First, let's print what we're working with
            print("\nProcessing transcript data...")
            
            # Get the full text from transcript
            transcript_text = self._prepare_transcript_text(transcript_data)
            print(f"\nTranscript length: {len(transcript_text)} characters")
            print("First 200 characters of transcript:", transcript_text[:200])
            
            # First, get the main summary
            summary_prompt = self._create_summary_prompt(transcript_text)
            summary_text = self._generate_text(summary_prompt)
            
            # Then, get key decisions
            decisions_prompt = self._create_decisions_prompt(transcript_text)
            decisions_text = self._generate_text(decisions_prompt)
            
            # Finally, get action items
            actions_prompt = self._create_actions_prompt(transcript_text)
            actions_text = self._generate_text(actions_prompt)
            
            # Create the complete summary
            summary = {
                'id': str(uuid.uuid4()),
                'summary_text': summary_text,
                'key_decisions': decisions_text,
                'action_items': actions_text,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Print the summary for verification
            print("\nGenerated Summary:")
            print(json.dumps(summary, indent=2))
            
            return summary
            
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            raise

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
Format each decision as a bullet point.

Transcript:
{transcript_text}

Key Decisions:"""

    def _create_actions_prompt(self, transcript_text: str) -> str:
        """Create prompt for action items"""
        return f"""From the following meeting transcript, extract only the specific action items and next steps assigned.
Format each action item as a bullet point, including who is responsible (if mentioned) and any deadlines.

Transcript:
{transcript_text}

Action Items:"""

    def _prepare_transcript_text(self, transcript_data: Dict[str, Any]) -> str:
        """Convert transcript data to formatted text for processing"""
        try:
            # Handle both possible transcript formats
            if 'segments' in transcript_data:
                # Format for segment-based transcript
                full_text = []
                for segment in transcript_data['segments']:
                    speaker = segment.get('speaker', 'Unknown Speaker')
                    text = segment.get('text', '')
                    full_text.append(f"{speaker}: {text}")
                return "\n".join(full_text)
            elif 'text' in transcript_data:
                # Return raw text if that's all we have
                return transcript_data['text']
            else:
                print("Warning: Unexpected transcript format")
                return str(transcript_data)
                
        except Exception as e:
            print(f"Error in prepare_transcript_text: {e}")
            return str(transcript_data)

    def _process_response(self, response_text: str) -> Dict[str, Any]:
        """Process API response into structured summary"""
        summary = {
            'id': str(uuid.uuid4()),
            'summary_text': '',
            'key_decisions': '',
            'action_items': '',
            'created_at': datetime.utcnow().isoformat()
        }

        # Split the response into sections
        sections = response_text.split('\n\n')
        for section in sections:
            if section.startswith('SUMMARY:'):
                summary['summary_text'] = section.replace('SUMMARY:', '').strip()
            elif section.startswith('KEY DECISIONS:'):
                summary['key_decisions'] = section.replace('KEY DECISIONS:', '').strip()
            elif section.startswith('ACTION ITEMS:'):
                summary['action_items'] = section.replace('ACTION ITEMS:', '').strip()

        return summary 