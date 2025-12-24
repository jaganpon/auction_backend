from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from database import init_db, get_db, DATABASE_PATH

# Import routers
from routers import auth, players, tournaments, teams, auction

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Cricket Auction API",
    version="2.0.0",
    description="Backend API for Cricket Auction Management"
)

# Create player_images directory if it doesn't exist
IMAGES_DIR = Path("player_images")
IMAGES_DIR.mkdir(exist_ok=True)

# Mount static files for player images
app.mount("/images", StaticFiles(directory="player_images"), name="images")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(auth.router)
app.include_router(tournaments.router)
app.include_router(teams.router)
app.include_router(players.router)  # No prefix - routes defined in players.py
app.include_router(auction.router)

# ==================== HEALTH CHECK ====================

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "online",
        "message": "Cricket Auction API",
        "version": "2.0.0",
        "database": DATABASE_PATH
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tournaments")
        tournament_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "tournaments": tournament_count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)