from fastapi import APIRouter, HTTPException, Depends, status
import sqlite3
from database import get_db
from schemas import TournamentCreate, TournamentUpdate
from utils import verify_token, require_role

router = APIRouter(prefix="/api/tournaments", tags=["Tournaments"])

@router.get("/")
async def get_tournaments(current_user: dict = Depends(verify_token)):
    """Get all tournaments with teams and players"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tournaments ORDER BY created_at DESC")
    tournaments = cursor.fetchall()
    
    result = []
    for tournament in tournaments:
        # Get teams for this tournament
        cursor.execute(
            "SELECT * FROM teams WHERE tournament_id = ?", 
            (tournament["id"],)
        )
        teams = cursor.fetchall()
        
        teams_data = []
        for team in teams:
            # Get players for this team
            cursor.execute(
                "SELECT * FROM players WHERE tournament_id = ? AND team_id = ?", 
                (tournament["id"], team["id"])
            )
            players = cursor.fetchall()
            
            teams_data.append({
                "id": team["id"],
                "name": team["name"],
                "totalBudget": team["total_budget"],
                "remainingBudget": team["remaining_budget"],
                "initialValue": team["total_budget"],
                "currentValue": team["remaining_budget"],
                "players": [dict(p) for p in players]
            })
        
        # Get all players for tournament
        cursor.execute(
            "SELECT * FROM players WHERE tournament_id = ?", 
            (tournament["id"],)
        )
        all_players = cursor.fetchall()
        
        result.append({
            "id": tournament["id"],
            "name": tournament["name"],
            "teams": teams_data,
            "players": [dict(p) for p in all_players],
            "createdAt": tournament["created_at"]
        })
    
    conn.close()
    return result

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_tournament(
    tournament: TournamentCreate,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Create new tournament with teams"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Insert tournament
        cursor.execute(
            "INSERT INTO tournaments (name, created_by) VALUES (?, ?)",
            (tournament.name, current_user["username"])
        )
        tournament_id = cursor.lastrowid
        
        # Insert teams
        for team in tournament.teams:
            cursor.execute(
                """INSERT INTO teams 
                   (tournament_id, name, total_budget, remaining_budget) 
                   VALUES (?, ?, ?, ?)""",
                (tournament_id, team["name"], team["budget"], team["budget"])
            )
        
        conn.commit()
        
        # Fetch created tournament
        cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
        created_tournament = cursor.fetchone()
        
        cursor.execute("SELECT * FROM teams WHERE tournament_id = ?", (tournament_id,))
        teams = cursor.fetchall()
        
        conn.close()
        
        return {
            "id": created_tournament["id"],
            "name": created_tournament["name"],
            "teams": [
                {
                    "id": t["id"],
                    "name": t["name"],
                    "totalBudget": t["total_budget"],
                    "remainingBudget": t["remaining_budget"],
                    "players": []
                } for t in teams
            ],
            "players": [],
            "createdAt": created_tournament["created_at"]
        }
    
    except sqlite3.IntegrityError as e:
        conn.rollback()
        conn.close()
        raise HTTPException(
            status_code=400, 
            detail=f"Tournament creation failed: {str(e)}"
        )

@router.get("/{tournament_id}")
async def get_tournament(
    tournament_id: int, 
    current_user: dict = Depends(verify_token)
):
    """Get specific tournament details"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
    tournament = cursor.fetchone()
    
    if not tournament:
        conn.close()
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    cursor.execute("SELECT * FROM teams WHERE tournament_id = ?", (tournament_id,))
    teams = cursor.fetchall()
    
    teams_data = []
    for team in teams:
        cursor.execute(
            "SELECT * FROM players WHERE tournament_id = ? AND team_id = ?", 
            (tournament_id, team["id"])
        )
        players = cursor.fetchall()
        
        teams_data.append({
            "id": team["id"],
            "name": team["name"],
            "totalBudget": team["total_budget"],
            "remainingBudget": team["remaining_budget"],
            "players": [dict(p) for p in players]
        })
    
    conn.close()
    
    return {
        "id": tournament["id"],
        "name": tournament["name"],
        "teams": teams_data,
        "createdAt": tournament["created_at"]
    }

@router.put("/{tournament_id}")
async def update_tournament(
    tournament_id: int,
    tournament_data: TournamentUpdate,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Update tournament name"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    cursor.execute(
        "UPDATE tournaments SET name = ? WHERE id = ?",
        (tournament_data.name, tournament_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": "Tournament updated successfully"}

@router.delete("/{tournament_id}")
async def delete_tournament(
    tournament_id: int,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Delete tournament"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    cursor.execute("DELETE FROM tournaments WHERE id = ?", (tournament_id,))
    
    conn.commit()
    conn.close()
    
    return {"message": "Tournament deleted successfully"}
