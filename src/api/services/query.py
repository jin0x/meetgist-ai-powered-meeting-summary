from typing import List, Dict, Any
from ...core.db import DatabaseManager
from fastapi import Depends

class QueryService:
    def __init__(self):
        self.db = DatabaseManager()

    async def get_all_summaries(self) -> List[Dict[str, Any]]:
        """Get all summaries with basic metadata"""
        try:
            response = self.db.supabase.table('summaries')\
                .select("id, created_at, transcripts(meeting_title)")\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching summaries: {e}")
            return []

    async def get_all_transcripts(self) -> List[Dict[str, Any]]:
        """Get all transcripts titles"""
        try:
            response = self.db.supabase.table('transcripts')\
                .select("meeting_title, created_at")\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching meetings: {e}")
            return []

def get_query_service() -> QueryService:
    """Dependency injection for QueryService"""
    return QueryService()