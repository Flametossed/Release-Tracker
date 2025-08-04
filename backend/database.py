from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
from config import settings
from models import Game, Platform, GameDB

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = AsyncIOMotorClient(settings.mongo_url)
        db.database = db.client.get_database()
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("Closed MongoDB connection")

async def create_indexes():
    """Create database indexes for performance"""
    try:
        games_collection = db.database.games
        platforms_collection = db.database.platforms
        
        # Games indexes
        await games_collection.create_index("name")
        await games_collection.create_index("first_release_date")
        await games_collection.create_index("platforms.id")
        await games_collection.create_index("last_updated")
        
        # Platforms indexes
        await platforms_collection.create_index("name")
        
        logger.info("Created database indexes")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")

async def save_games(games: List[Game]) -> int:
    """Save games to database"""
    try:
        games_collection = db.database.games
        saved_count = 0
        
        for game in games:
            game_doc = {
                "_id": game.id,
                "name": game.name,
                "summary": game.summary,
                "rating": game.rating,
                "first_release_date": game.first_release_date,
                "release_dates": [rd.dict() for rd in game.release_dates],
                "platforms": [p.dict() for p in game.platforms],
                "cover": game.cover.dict() if game.cover else None,
                "last_updated": datetime.now()
            }
            
            await games_collection.replace_one(
                {"_id": game.id},
                game_doc,
                upsert=True
            )
            saved_count += 1
        
        logger.info(f"Saved {saved_count} games to database")
        return saved_count
        
    except Exception as e:
        logger.error(f"Failed to save games: {e}")
        raise

async def get_upcoming_games_from_db(
    days_ahead: int = 90,
    platform_ids: Optional[List[int]] = None,
    limit: int = 100
) -> List[Game]:
    """Get upcoming games from database"""
    try:
        games_collection = db.database.games
        
        # Build filter
        filter_query = {
            "first_release_date": {
                "$gte": datetime.now(),
                "$lte": datetime.now() + timedelta(days=days_ahead)
            }
        }
        
        if platform_ids:
            filter_query["platforms.id"] = {"$in": platform_ids}
        
        # Query database
        cursor = games_collection.find(filter_query).sort("first_release_date", 1).limit(limit)
        games_data = await cursor.to_list(length=limit)
        
        # Convert to Game objects
        games = []
        for game_data in games_data:
            game_data["id"] = game_data.pop("_id")
            games.append(Game(**game_data))
        
        return games
        
    except Exception as e:
        logger.error(f"Failed to get upcoming games from database: {e}")
        return []

async def save_platforms(platforms: List[Platform]) -> int:
    """Save platforms to database"""
    try:
        platforms_collection = db.database.platforms
        saved_count = 0
        
        for platform in platforms:
            platform_doc = {
                "_id": platform.id,
                "name": platform.name,
                "abbreviation": platform.abbreviation,
                "last_updated": datetime.now()
            }
            
            await platforms_collection.replace_one(
                {"_id": platform.id},
                platform_doc,
                upsert=True
            )
            saved_count += 1
        
        logger.info(f"Saved {saved_count} platforms to database")
        return saved_count
        
    except Exception as e:
        logger.error(f"Failed to save platforms: {e}")
        raise

async def get_platforms_from_db() -> List[Platform]:
    """Get all platforms from database"""
    try:
        platforms_collection = db.database.platforms
        
        cursor = platforms_collection.find({}).sort("name", 1)
        platforms_data = await cursor.to_list(length=None)
        
        platforms = []
        for platform_data in platforms_data:
            platform_data["id"] = platform_data.pop("_id")
            platforms.append(Platform(**platform_data))
        
        return platforms
        
    except Exception as e:
        logger.error(f"Failed to get platforms from database: {e}")
        return []