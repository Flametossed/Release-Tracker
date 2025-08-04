from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from config import settings
from models import Game, Platform, GameResponse
from igdb_client import IGDBClient, IGDBAuthError, IGDBRateLimitError
from database import connect_to_mongo, close_mongo_connection, save_games, get_upcoming_games_from_db, save_platforms, get_platforms_from_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
igdb_client: Optional[IGDBClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global igdb_client
    
    # Startup
    logger.info("Starting up Game Release Tracker API")
    
    # Connect to database
    await connect_to_mongo()
    
    # Initialize IGDB client
    igdb_client = IGDBClient(
        settings.igdb_client_id,
        settings.igdb_client_secret,
        settings.requests_per_second
    )
    
    # Test API connection
    try:
        await igdb_client._get_access_token()
        logger.info("IGDB API connection successful")
    except Exception as e:
        logger.error(f"Failed to connect to IGDB API: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Game Release Tracker API")
    if igdb_client:
        await igdb_client._client.aclose()
    await close_mongo_connection()

app = FastAPI(
    title=settings.app_name,
    description="API for tracking upcoming video game releases using IGDB data",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_igdb_client() -> IGDBClient:
    """Dependency to get IGDB client"""
    if not igdb_client:
        raise HTTPException(status_code=503, detail="IGDB client not initialized")
    return igdb_client

@app.get("/api/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Game Release Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "upcoming_games": "/api/games/upcoming",
            "search_games": "/api/games/search",
            "platforms": "/api/platforms",
            "sync_data": "/api/sync"
        }
    }

@app.get("/api/games/upcoming", response_model=GameResponse, tags=["Games"])
async def get_upcoming_games(
    days_ahead: int = Query(90, ge=1, le=365, description="Number of days to look ahead for releases"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of games to return"),
    platform_ids: Optional[str] = Query(None, description="Comma-separated platform IDs to filter by"),
    force_refresh: bool = Query(False, description="Force refresh from IGDB API"),
    client: IGDBClient = Depends(get_igdb_client)
):
    """Get upcoming video game releases"""
    
    # Parse platform IDs
    platform_filter = None
    if platform_ids:
        try:
            platform_filter = [int(pid.strip()) for pid in platform_ids.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid platform IDs format")
    
    try:
        if force_refresh:
            # Fetch fresh data from IGDB
            logger.info("Force refresh requested - fetching from IGDB")
            games_data = await client.get_upcoming_games(
                days_ahead=days_ahead,
                limit=limit,
                platform_ids=platform_filter
            )
            
            # Convert to Game objects
            games = []
            for game_data in games_data:
                try:
                    games.append(Game(**game_data))
                except Exception as e:
                    logger.warning(f"Failed to parse game data: {e}")
                    continue
            
            # Save to database
            if games:
                await save_games(games)
        else:
            # Try to get from database first
            games = await get_upcoming_games_from_db(
                days_ahead=days_ahead,
                platform_ids=platform_filter,
                limit=limit
            )
            
            # If no data in database, fetch from IGDB
            if not games:
                logger.info("No data in database - fetching from IGDB")
                games_data = await client.get_upcoming_games(
                    days_ahead=days_ahead,
                    limit=limit,
                    platform_ids=platform_filter
                )
                
                # Convert to Game objects
                for game_data in games_data:
                    try:
                        games.append(Game(**game_data))
                    except Exception as e:
                        logger.warning(f"Failed to parse game data: {e}")
                        continue
                
                # Save to database
                if games:
                    await save_games(games)
        
        # Sort games by release date and platform
        sorted_games = sorted(games, key=lambda g: (
            g.first_release_date or datetime.max,
            g.name
        ))
        
        response = GameResponse(
            games=sorted_games,
            total_count=len(sorted_games),
            per_page=limit
        )
        
        return response
        
    except IGDBRateLimitError:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    except IGDBAuthError:
        raise HTTPException(status_code=503, detail="Authentication failed with IGDB API")
    except Exception as e:
        logger.error(f"Error fetching upcoming games: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/games/search", response_model=GameResponse, tags=["Games"])
async def search_games(
    q: str = Query(..., min_length=2, description="Search query for game names"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    client: IGDBClient = Depends(get_igdb_client)
):
    """Search for games by name"""
    
    try:
        games_data = await client.search_games(q, limit)
        
        # Convert to Game objects
        games = []
        for game_data in games_data:
            try:
                games.append(Game(**game_data))
            except Exception as e:
                logger.warning(f"Failed to parse game data: {e}")
                continue
        
        response = GameResponse(
            games=games,
            total_count=len(games),
            per_page=limit
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error searching games: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/platforms", response_model=List[Platform], tags=["Platforms"])
async def get_platforms(
    force_refresh: bool = Query(False, description="Force refresh from IGDB API"),
    client: IGDBClient = Depends(get_igdb_client)
):
    """Get all gaming platforms"""
    
    try:
        if force_refresh:
            # Fetch fresh data from IGDB
            logger.info("Force refresh requested - fetching platforms from IGDB")
            platforms_data = await client.get_platforms()
            
            # Convert to Platform objects
            platforms = []
            for platform_data in platforms_data:
                try:
                    platforms.append(Platform(**platform_data))
                except Exception as e:
                    logger.warning(f"Failed to parse platform data: {e}")
                    continue
            
            # Save to database
            if platforms:
                await save_platforms(platforms)
        else:
            # Try to get from database first
            platforms = await get_platforms_from_db()
            
            # If no data in database, fetch from IGDB
            if not platforms:
                logger.info("No platforms in database - fetching from IGDB")
                platforms_data = await client.get_platforms()
                
                # Convert to Platform objects
                for platform_data in platforms_data:
                    try:
                        platforms.append(Platform(**platform_data))
                    except Exception as e:
                        logger.warning(f"Failed to parse platform data: {e}")
                        continue
                
                # Save to database
                if platforms:
                    await save_platforms(platforms)
        
        return platforms
        
    except Exception as e:
        logger.error(f"Error fetching platforms: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/sync", tags=["Data"])
async def sync_data(
    background_tasks: BackgroundTasks,
    client: IGDBClient = Depends(get_igdb_client)
):
    """Sync data from IGDB API in the background"""
    
    async def sync_task():
        try:
            logger.info("Starting background data sync")
            
            # Sync platforms first
            platforms_data = await client.get_platforms()
            platforms = []
            for platform_data in platforms_data:
                try:
                    platforms.append(Platform(**platform_data))
                except Exception as e:
                    logger.warning(f"Failed to parse platform data: {e}")
                    continue
            
            if platforms:
                await save_platforms(platforms)
            
            # Sync upcoming games
            games_data = await client.get_upcoming_games(days_ahead=180, limit=500)
            games = []
            for game_data in games_data:
                try:
                    games.append(Game(**game_data))
                except Exception as e:
                    logger.warning(f"Failed to parse game data: {e}")
                    continue
            
            if games:
                await save_games(games)
            
            logger.info(f"Background sync completed - synced {len(platforms)} platforms and {len(games)} games")
            
        except Exception as e:
            logger.error(f"Background sync failed: {e}")
    
    background_tasks.add_task(sync_task)
    
    return {
        "message": "Data sync started in background",
        "status": "running"
    }

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Test IGDB connection
        if igdb_client:
            await igdb_client._get_access_token()
        
        return {
            "status": "healthy",
            "igdb_api": "connected",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=settings.debug)