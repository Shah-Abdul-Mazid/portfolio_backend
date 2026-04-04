from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db = MongoDB()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.ATLAS_URL)
    db.db = db.client[settings.DB_NAME]

async def close_mongo_connection():
    db.client.close()

def get_database():
    """Returns the MongoDB database instance."""
    return db.db
