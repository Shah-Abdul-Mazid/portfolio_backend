import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, Request, HTTPException, File, UploadFile, Body
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import logging
import jwt

# --- 1. CONFIGURATION ---
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("portfolio-fastapi")

app = FastAPI(title="Portfolio FastAPI")

# CORS for Vercel and Local Testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. DB CONNECTION ---
atlas_url = os.getenv("atlas_URL")
db_name = os.getenv("atlas_DB_NAME", "portfolio_data")
client = AsyncIOMotorClient(atlas_url)
db = client[db_name]

# Collections (Replicating Node Mongoose collections)
portfolio_coll = db["portfolio_content"]
messages_coll = db["messages"]
analytics_coll = db["analytics"]
admin_coll = db["admins"]

# --- 3. AUTH UTILS (Replicating authMiddleware.js) ---
JWT_SECRET = os.getenv("JWT_SECRET", "secret")

def verify_admin(request: Request):
    """Checks the Authorization header for a valid JWT token."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = auth_header.replace("Bearer ", "")
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- 4. CLOUDINARY ---
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# --- 5. ROUTES: HEALTH & ANALYTICS ---
@app.get("/api/health")
async def health():
    try:
        await client.admin.command('ping')
        m_status = "Connected"
    except:
        m_status = "Disconnected"
    return {"status": "online", "database": m_status, "engine": "FastAPI (Python)"}

@app.get("/api/analytics")
async def get_analytics():
    """Retrieve visitor counts, replicating analyticRoutes.js in Node."""
    doc = await analytics_coll.find_one({"_id": "visitor_count"})
    if not doc:
        # Create it if it doesn't exist
        await analytics_coll.insert_one({"_id": "visitor_count", "count": 0})
        return {"count": 0}
    return {"count": doc.get("count", 0)}

@app.post("/api/analytics")
async def increment_analytics():
    """Increment visitor counts on each visit."""
    result = await analytics_coll.find_one_and_update(
        {"_id": "visitor_count"},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=True
    )
    return {"success": True, "count": result.get("count", 0)}

# --- 6. ROUTES: PORTFOLIO (The core sync) ---
@app.get("/api/portfolio")
async def get_portfolio():
    doc = await portfolio_coll.find_one({})
    if doc:
        # We only return the 'data' field, same as our Node Controller
        return doc.get("data", {})
    return None

@app.post("/api/portfolio")
async def save_portfolio(data: dict = Body(...), auth = Depends(verify_admin)):
    """Saves updated portfolio data to MongoDB, protected by JWT."""
    # Matches savePortfolioData controller in Node
    result = await portfolio_coll.find_one_and_update(
        {},
        {"$set": {"data": data, "lastUpdated": datetime.utcnow()}},
        upsert=True,
        return_document=True
    )
    # File cleanup logic will be here in next step
    return {"success": True, "message": "Changes synced securely using FastAPI!"}

# --- 7. ROUTES: MESSAGES ---
@app.get("/api/messages")
async def get_messages(auth = Depends(verify_admin)):
    """Protected list of messages (Node.js port)"""
    # Fetch latest 50 messages
    cursor = messages_coll.find({}).sort("created_at", -1).limit(50)
    messages = []
    async for msg in cursor:
        msg["_id"] = str(msg["_id"]) # Convert id to string
        messages.append(msg)
    return messages

@app.post("/api/messages")
async def create_message(msg: dict = Body(...)):
    """Public message submission route."""
    msg["created_at"] = datetime.utcnow().isoformat()
    await messages_coll.insert_one(msg)
    return {"success": True, "message": "Your message was sent!"}

# --- 8. ROUTES: UPLOADS ---
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Cloudinary direct-buffer upload. Replicates uploadRoutes.js perfectly."""
    try:
        # FastAPI stream-to-cloudinary
        result = cloudinary.uploader.upload(
            file.file, 
            folder="portfolio_uploads",
            resource_type="auto"
        )
        return {"success": True, "url": result.get("secure_url")}
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- 9. ROUTES: ADMIN AUTH ---
@app.post("/api/admin/login")
async def login(credentials: dict = Body(...)):
    """Logs in an admin, matches bcrypt logic from adminController.js"""
    email = credentials.get("email")
    password = credentials.get("password")
    
    admin = await admin_coll.find_one({"email": email})
    if not admin or not pwd_context.verify(password, admin.get("password")):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = jwt.encode(
        {"id": str(admin["_id"]), "email": admin["email"], "role": admin.get("role")},
        JWT_SECRET,
        algorithm="HS256"
    )
    
    return {
        "success": True, 
        "token": token, 
        "admin": {"email": admin["email"], "role": admin.get("role")}
    }

@app.post("/api/admin/register")
async def register(data: dict = Body(...)):
    """Registers a new admin with hashed password."""
    email = data.get("email")
    password = data.get("password")
    
    if await admin_coll.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already exists")
        
    hashed = pwd_context.hash(password)
    await admin_coll.insert_one({
        "email": email, 
        "password": hashed, 
        "role": "admin",
        "created_at": datetime.utcnow()
    })
    return {"success": True, "message": "Admin created"}

@app.get("/api/admin/list")
async def list_admins(auth = Depends(verify_admin)):
    """Lists all admins (matching adminController.js)"""
    cursor = admin_coll.find({}, {"password": 0}).sort("created_at", -1)
    admins = []
    async for a in cursor:
        a["_id"] = str(a["_id"])
        admins.append(a)
    return {"success": True, "data": admins}

# --- 10. STARTUP ---
if __name__ == "__main__":
    import uvicorn
    # Same port as before
    uvicorn.run("main:app", host="0.0.0.0", port=3001, reload=True)
