import requests
import json
from typing import Dict, List, Optional

class NotionPitchExtractor:
    def __init__(self, integration_token: str):
        self.token = integration_token
        self.headers = {
            "Authorization": f"Bearer {integration_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.base_url = "https://api.notion.com/v1"
    
    def extract_client_data(self, database_id: str, client_name: str) -> Dict:
        """Extract all relevant data for a client from Notion"""
        
        client_page = self.find_client_page(database_id, client_name)
        if not client_page:
            return {"error": f"Client '{client_name}' not found"}
        
        client_data = self.parse_client_page(client_page)
        return client_data
    
    def find_client_page(self, database_id: str, client_name: str) -> Optional[Dict]:
        """Find client page in database"""
        
        query_url = f"{self.base_url}/databases/{database_id}/query"
        
        response = requests.post(query_url, headers=self.headers, json={})
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            for result in results:
                title = self.extract_title(result.get("properties", {}).get("Name", {}))
                if client_name.lower() in title.lower():
                    return result
        
        return None
    
    def parse_client_page(self, page: Dict) -> Dict:
        """Parse client page properties"""
        
        properties = page.get("properties", {})
        
        client_data = {
            "client_name": self.extract_title(properties.get("Name", {})),
            "status": self.extract_select(properties.get("Status", {})),
            "services": self.extract_multi_select(properties.get("Services", {})),
            "category": self.extract_select(properties.get("Category", {})),
            "qualification_call": self.extract_url(properties.get("Qualification Call", {})),
            "discovery_call": self.extract_url(properties.get("Discovery Call", {})),
            "discovery_notes": self.extract_url(properties.get("Discovery Notes", {})),
            "pitch_strategy": self.extract_url(properties.get("Pitch Strategy", {})),
            "pitch_deck": self.extract_url(properties.get("Pitch", {})),
            "so_owner": self.extract_rich_text(properties.get("SO", {})),
            "sales_owner": self.extract_rich_text(properties.get("Sales", {})),
        }
        
        return client_data
    
    def extract_title(self, prop: Dict) -> str:
        if prop.get("type") == "title":
            title_array = prop.get("title", [])
            return title_array[0].get("text", {}).get("content", "") if title_array else ""
        return ""
    
    def extract_rich_text(self, prop: Dict) -> str:
        if prop.get("type") == "rich_text":
            rich_text_array = prop.get("rich_text", [])
            return " ".join([rt.get("text", {}).get("content", "") for rt in rich_text_array])
        return ""
    
    def extract_select(self, prop: Dict) -> str:
        if prop.get("type") == "select":
            select_obj = prop.get("select")
            return select_obj.get("name", "") if select_obj else ""
        return ""
    
    def extract_multi_select(self, prop: Dict) -> List[str]:
        if prop.get("type") == "multi_select":
            multi_select_array = prop.get("multi_select", [])
            return [ms.get("name", "") for ms in multi_select_array]
        return []
    
    def extract_url(self, prop: Dict) -> str:
        if prop.get("type") == "url":
            return prop.get("url", "")
        return ""
