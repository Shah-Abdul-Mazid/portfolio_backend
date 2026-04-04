from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import connect_to_mongo, close_mongo_connection
from app.api.v1.endpoints import portfolio, admin, analytics, messages, upload, agent
from app.config import settings
import cloudinary
import asyncio

app = FastAPI(title=settings.PROJECT_NAME)

# --- 1. CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. DB EVENTS ---
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# --- 3. CLOUDINARY CONFIG ---
if settings.CLOUDINARY_URL:
    # Use the combined URL automatically
    cloudinary.config(cloudinary_url=settings.CLOUDINARY_URL, secure=True)
    print("🚀 [FastAPI] Cloudinary Configured via CLOUDINARY_URL!")
elif settings.is_cloudinary_configured:
    # Use individual keys
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
    print("🚀 [FastAPI] Cloudinary Configured via Individual Keys!")
else:
    print("⚠️  [FastAPI] Cloudinary is NOT configured. Uploads will fail!")

# --- 4. API ROUTING (Professional Modular Structure) ---
# Each piece of your portfolio is now in its own dedicated file
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Auth"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(messages.router, prefix="/api/messages", tags=["Messages"])
app.include_router(upload.router, prefix="/api/upload", tags=["Uploads"])
app.include_router(agent.router, prefix="/api/agent", tags=["AI Agent"])

# --- 5. CORE ENDPOINTS ---
@app.get("/api/v1/health")
@app.get("/api/health")
async def health():
    # Attempt a simple ping to verify MongoDB
    try:
        from app.db import get_database
        db_inst = get_database()
        if db_inst is not None:
             # Basic command with timeout to verify connection
             await asyncio.wait_for(db_inst.command("ping"), timeout=2.0)
             db_status = "Connected"
        else:
             db_status = "Disconnected"
    except Exception:
        db_status = "Error"

    # Cloudinary check (simple validation of config)
    try:
        if settings.is_cloudinary_configured:
            cloudinary_status = "Configured"
        else:
            cloudinary_status = "Missing Config"
    except Exception:
        cloudinary_status = "Error"

    return {
        "status": "online",
        "database": db_status,
        "cloudinary": cloudinary_status,
        "engine": "FastAPI Professional Migration Complete"
    }

@app.get("/version")
async def get_version():
    return {
        "version": "1.1.0-MODULAR",
        "engine": "FastAPI Professional Migration",
        "status": "Production-Hardened"
    }

@app.get("/")
async def root():
    return {"message": "Welcome to the Portfolio & AI Agent Backend API"}

if __name__ == "__main__":
    import uvicorn
    # Same port as Node for zero-change frontend compatibility
    uvicorn.run("app.main:app", host="0.0.0.0", port=3001, reload=True)
