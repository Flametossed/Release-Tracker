import httpx
import asyncio
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class IGDBAuthError(Exception):
    pass

class IGDBRateLimitError(Exception):
    pass

class IGDBClient:
    def __init__(self, client_id: str, client_secret: str, requests_per_second: float = 3.5):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.igdb.com/v4"
        self.token_url = "https://id.twitch.tv/oauth2/token"
        
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        # Rate limiting
        self.requests_per_second = requests_per_second
        self.last_request_time = 0.0
        self.request_interval = 1.0 / requests_per_second
        
        self._client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()
        
    async def _get_access_token(self) -> str:
        """Get or refresh the access token"""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
            
        logger.info("Fetching new IGDB access token")
        
        try:
            response = await self._client.post(
                self.token_url,
                params={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials"
                },
                headers={"Accept": "application/json"}
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # Refresh 5 minutes early
            
            logger.info("Successfully obtained IGDB access token")
            return self.access_token
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to get IGDB access token: {e}")
            raise IGDBAuthError(f"Authentication failed: {e}")
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.request_interval:
            sleep_time = self.request_interval - time_since_last_request
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    async def _make_request(self, endpoint: str, query: str) -> Dict[Any, Any]:
        """Make an authenticated request to IGDB API"""
        await self._rate_limit()
        
        token = await self._get_access_token()
        
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "text/plain"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = await self._client.post(url, content=query, headers=headers)
            
            if response.status_code == 429:
                raise IGDBRateLimitError("Rate limit exceeded")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"IGDB API request failed: {e}")
            raise
    
    async def get_upcoming_games(
        self, 
        days_ahead: int = 90, 
        limit: int = 100,
        platform_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """Fetch upcoming game releases"""
        
        # Calculate date range
        start_timestamp = int(datetime.now().timestamp())
        end_timestamp = int((datetime.now() + timedelta(days=days_ahead)).timestamp())
        
        # Build query
        query_parts = [
            "fields name,summary,rating,first_release_date,cover.url,release_dates.date,release_dates.human,release_dates.platform.name,release_dates.platform.abbreviation,platforms.name,platforms.abbreviation",
            f"where release_dates.date >= {start_timestamp} & release_dates.date < {end_timestamp}"
        ]
        
        if platform_ids:
            platform_filter = " | ".join(str(pid) for pid in platform_ids)
            query_parts.append(f"& release_dates.platform = ({platform_filter})")
        
        query_parts.extend([
            "sort release_dates.date asc",
            f"limit {limit}"
        ])
        
        query = "; ".join(query_parts) + ";"
        
        logger.info(f"Fetching upcoming games with query: {query}")
        
        try:
            response_data = await self._make_request("games", query)
            logger.info(f"Successfully fetched {len(response_data)} upcoming games")
            return response_data
            
        except Exception as e:
            logger.error(f"Failed to fetch upcoming games: {e}")
            raise
    
    async def search_games(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for games by name"""
        query = f'search "{search_term}"; fields name,summary,rating,first_release_date,cover.url,platforms.name; limit {limit};'
        
        try:
            response_data = await self._make_request("games", query)
            return response_data
        except Exception as e:
            logger.error(f"Failed to search games: {e}")
            raise
    
    async def get_platforms(self) -> List[Dict[str, Any]]:
        """Get all gaming platforms"""
        query = "fields name,abbreviation; where category = (1,5,6); sort name asc; limit 500;"
        
        try:
            response_data = await self._make_request("platforms", query)
            return response_data
        except Exception as e:
            logger.error(f"Failed to fetch platforms: {e}")
            raise