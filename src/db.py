from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )

    def get_all_transcripts(self) -> List[Dict[str, Any]]:
        """Retrieve all transcripts from the database."""
        try:
            response = self.supabase.table('transcripts').select("*").execute()
            return response.data
        except Exception as e:
            print(f"Error fetching transcripts: {e}")
            return []

    def get_transcript_by_id(self, transcript_id: str) -> Dict[str, Any]:
        """Retrieve a specific transcript by ID."""
        try:
            response = self.supabase.table('transcripts').select("*").eq('id', transcript_id).single().execute()
            return response.data
        except Exception as e:
            print(f"Error fetching transcript: {e}")
            return None

    def save_transcript(self, title: str, content: str, source_type: str) -> Dict[str, Any]:
        """Save a new transcript to the database."""
        try:
            response = self.supabase.table('transcripts').insert({
                "meeting_title": title,
                "content": content,
                "source_type": source_type
            }).execute()
            return response.data[0]
        except Exception as e:
            print(f"Error saving transcript: {e}")
            return None

    def get_summary_by_transcript_id(self, transcript_id: str) -> Dict[str, Any]:
        """Retrieve summary for a specific transcript."""
        try:
            response = self.supabase.table('summaries').select("*").eq('transcript_id', transcript_id).single().execute()
            return response.data
        except Exception as e:
            print(f"Error fetching summary: {e}")
            return None

    def save_summary(self, transcript_id: str, summary_text: str,
                    key_decisions: str = None, action_items: str = None) -> Dict[str, Any]:
        """Save a new summary to the database."""
        try:
            response = self.supabase.table('summaries').insert({
                "transcript_id": transcript_id,
                "summary_text": summary_text,
                "key_decisions": key_decisions,
                "action_items": action_items
            }).execute()
            return response.data[0]
        except Exception as e:
            print(f"Error saving summary: {e}")
            return None