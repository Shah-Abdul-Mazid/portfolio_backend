from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import connect_to_mongo, close_mongo_connection
from app.api.v1.endpoints import portfolio, admin, others
from app.config import settings
import cloudinary

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
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

# --- 4. API ROUTING (Professional Modular Structure) ---
# Portfolio Core
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
# Collections (Mapped EXACTLY to your MongoDB Screenshot)
portfolio_coll = db["portfolio_content"]
messages_coll = db["messages"]
analytics_coll = db["analytics"]
admin_coll = db["admin_db"]
visitors_coll = db["visitors"]
app.include_router(others.analytics_router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(others.messages_router, prefix="/api/messages", tags=["Messages"])
app.include_router(others.upload_router, prefix="/api/upload", tags=["Uploads"])

# AI Agent Placeholders (as requested)
@app.get("/api/v1/health")
async def health():
    return {"status": "online", "engine": "FastAPI Professional Structure"}

@app.get("/")
async def root():
    return {"message": "Welcome to the Portfolio & AI Agent Backend API"}

if __name__ == "__main__":
    import uvicorn
    # Use port 3001 to maintain local environment stability
    uvicorn.run("app.main:app", host="0.0.0.0", port=3001, reload=True)
