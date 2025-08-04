from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Platform(BaseModel):
    id: int
    name: str
    abbreviation: Optional[str] = None
    
class ReleaseDate(BaseModel):
    id: int
    date: Optional[datetime] = None
    human: Optional[str] = None
    platform: Optional[Platform] = None
    region: Optional[int] = None
    
    @validator('date', pre=True)
    def parse_timestamp(cls, v):
        if isinstance(v, int):
            return datetime.fromtimestamp(v)
        return v

class GameCover(BaseModel):
    id: int
    url: Optional[str] = None
    
    def get_cover_url(self, size: str = "cover_big") -> Optional[str]:
        if self.url:
            return f"https:{self.url.replace('t_thumb', f't_{size}')}"
        return None

class Game(BaseModel):
    id: int
    name: str
    summary: Optional[str] = None
    rating: Optional[float] = None
    first_release_date: Optional[datetime] = None
    release_dates: List[ReleaseDate] = []
    platforms: List[Platform] = []
    cover: Optional[GameCover] = None
    
    @validator('first_release_date', pre=True)
    def parse_first_release_timestamp(cls, v):
        if isinstance(v, int):
            return datetime.fromtimestamp(v)
        return v

class GameResponse(BaseModel):
    games: List[Game]
    total_count: Optional[int] = None
    page: int = 1
    per_page: int = 50

# Database models
class GameDB(BaseModel):
    game_id: int = Field(..., alias="_id")
    name: str
    summary: Optional[str] = None
    rating: Optional[float] = None
    first_release_date: Optional[datetime] = None
    release_dates: List[ReleaseDate] = []
    platforms: List[Platform] = []
    cover: Optional[GameCover] = None
    last_updated: datetime = Field(default_factory=datetime.now)
    
    class Config:
        allow_population_by_field_name = True