from fastapi import APIRouter, Depends, Request, HTTPException
from app.db import get_database
from app.api.v1.endpoints.portfolio import get_admin_user
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger("portfolio-analytics")

@router.post("/track")
async def track_page_view(request: Request, db=Depends(get_database)):
    """
    Tracks visitor IPs and unique page views.
    Replicates Node.js flow in analyticsController.js.
    """
    try:
        # Get real client IP (Handles proxies like Vercel/Render)
        ip = request.headers.get("x-forwarded-for", "").split(",")[0] or \
             request.headers.get("x-real-ip") or \
             request.client.host

        user_agent = request.headers.get("user-agent", "Unknown Device")

        # Check if visitor already exists
        existing_visitor = await db["visitors"].find_one({"ip": ip})

        if not existing_visitor:
            # Create new visitor record
            await db["visitors"].insert_one({
                "ip": ip, 
                "device": user_agent, 
                "timestamp": datetime.utcnow()
            })
            
            # Increment overall view count
            result = await db["analytics"].find_one_and_update(
                {"id": "total_views"},
                {"$inc": {"count": 1}},
                upsert=True,
                return_document=True
            )
            return result.get("count", 0)

        # Still return current total if returning visitor
        stats = await db["analytics"].find_one({"id": "total_views"})
        return stats.get("count", 0) if stats else 0
        
    except Exception as e:
        logger.error(f"Error tracking visit: {e}")
        return {"error": "Failed to track visit"}

@router.get("")
@router.get("/count")
async def get_analytics(db=Depends(get_database)):
    """Retrieve total page views."""
    stats = await db["analytics"].find_one({"id": "total_views"})
    if stats:
        stats["_id"] = str(stats["_id"])
        return stats
    return {"count": 0}

@router.get("/visitors")
async def get_visitors_list(admin=Depends(get_admin_user), db=Depends(get_database)):
    """List visitor history (Protected)."""
    cursor = db["visitors"].find({}).sort("timestamp", -1).limit(500)
    visitors = []
    async for v in cursor:
        v["_id"] = str(v["_id"])
        visitors.append(v)
    return visitors

@router.post("/clear")
async def clear_all_visitors(admin=Depends(get_admin_user), db=Depends(get_database)):
    """Full data reset for analytics."""
    await db["visitors"].delete_many({})
    await db["analytics"].find_one_and_update({"id": "total_views"}, {"$set": {"count": 0}})
    return {"success": True, "message": "All visitor records cleared."}
