import os
import requests
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AnythingLLMClient:
    """Client for interacting with AnythingLLM API"""
    
    def __init__(self):
        self.api_url = os.getenv('ANYTHINGLLM_API_URL', 'http://localhost:3001/api')
        self.api_key = os.getenv('ANYTHINGLLM_API_KEY')
        self.workspace_slug = os.getenv('ANYTHINGLLM_WORKSPACE_SLUG', 'scientific-papers')
        
        if not self.api_key:
            raise ValueError("ANYTHINGLLM_API_KEY environment variable is required")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def chat_with_workspace(self, message: str, mode: str = "chat") -> Dict[str, Any]:
        """
        Send a chat message to the workspace with RAG capabilities
        
        Args:
            message: The message/query to send
            mode: Chat mode - "chat" for RAG-enabled, "query" for simple query
            
        Returns:
            Dictionary containing the response and sources
        """
        url = f"{self.api_url}/v1/workspace/{self.workspace_slug}/chat"
        
        payload = {
            "message": message,
            "mode": mode
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error in chat request: {e}")
            return {"textResponse": "Error occurred during chat", "sources": []}
    
    def search_documents(self, query: str, limit: int = 8) -> List[Dict[str, Any]]:
        """
        Search for documents in the workspace
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of document chunks with metadata
        """
        # Use chat mode to get sources, then extract them
        response = self.chat_with_workspace(
            f"Find papers related to: {query}. Please provide detailed information about relevant papers.",
            mode="chat"
        )
        
        sources = response.get("sources", [])
        
        # Limit the number of sources returned
        return sources[:limit]
    
    def upload_document(self, file_path: str, filename: Optional[str] = None) -> bool:
        """
        Upload a document to the workspace
        
        Args:
            file_path: Path to the file to upload
            filename: Optional custom filename
            
        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        url = f"{self.api_url}/v1/workspace/{self.workspace_slug}/upload"
        
        if not filename:
            filename = os.path.basename(file_path)
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (filename, f, 'text/plain')}
                headers = {'Authorization': f'Bearer {self.api_key}'}
                
                response = requests.post(url, headers=headers, files=files)
                response.raise_for_status()
                return True
        except requests.exceptions.RequestException as e:
            print(f"Error uploading file {file_path}: {e}")
            return False
    
    def get_workspace_info(self) -> Dict[str, Any]:
        """Get information about the workspace"""
        url = f"{self.api_url}/v1/workspace/{self.workspace_slug}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting workspace info: {e}")
            return {}
    
    def create_workspace(self, name: str = "Scientific Papers") -> bool:
        """
        Create a new workspace
        
        Args:
            name: Name for the workspace
            
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.api_url}/v1/workspace/new"
        
        payload = {
            "name": name,
            "slug": self.workspace_slug
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error creating workspace: {e}")
            return False