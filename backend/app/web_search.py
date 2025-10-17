"""
Fallback: Direct WolframAlpha Short Answers API.
Use this if MCP server setup doesn't work in time.
"""

import httpx
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()


class WolframSearchClient:
    """Simple WolframAlpha API client (non-MCP fallback)."""
    
    def __init__(self):
        self.app_id = os.getenv("WOLFRAM_APP_ID", "")
        self.base_url = "https://api.wolframalpha.com/v1/result"
    
    def search_web(self, query: str) -> Dict:
        """Query WolframAlpha Short Answers API."""
        if not self.app_id:
            return {"content": "", "source": "no_api_key", "success": False}
        
        try:
            url = f"{self.base_url}?i={query}&appid={self.app_id}"
            response = httpx.get(url, timeout=10)
            
            if response.status_code == 200:
                return {
                    "content": response.text,
                    "source": "wolfram_alpha_http",
                    "success": True
                }
            else:
                return {
                    "content": f"No answer (status {response.status_code})",
                    "source": "wolfram_alpha_http",
                    "success": False
                }
        except Exception as e:
            return {"content": str(e), "source": "error", "success": False}

def get_web_search_client():
    return WolframSearchClient()
