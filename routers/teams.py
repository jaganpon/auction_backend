from fastapi import APIRouter, HTTPException, Depends
import sqlite3
from database import get_db
from schemas import TeamUpdate, PlayerCreate
from utils import require_role

router = APIRouter(
    prefix="/api/tournaments/{tournament_id}/teams",
    tags=["Teams"]
)

@router.post("/")
async def create_team(
    tournament_id: int,
    team_data: dict,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Create a new team in tournament"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check tournament exists
    cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    try:
        cursor.execute(
            """INSERT INTO teams (tournament_id, name, total_budget, remaining_budget) 
               VALUES (?, ?, ?, ?)""",
            (tournament_id, team_data['name'], team_data['budget'], team_data['budget'])
        )
        team_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
        team = cursor.fetchone()
        conn.close()
        
        return {
            "id": team["id"],
            "name": team["name"],
            "totalBudget": team["total_budget"],
            "remainingBudget": team["remaining_budget"]
        }
    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=400, detail="Team name already exists in this tournament")

@router.put("/{team_id}")
async def update_team(
    tournament_id: int,
    team_id: int,
    team_data: TeamUpdate,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Update team name/budget"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM teams WHERE id = ? AND tournament_id = ?", 
        (team_id, tournament_id)
    )
    team = cursor.fetchone()
    
    if not team:
        conn.close()
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Update name
    cursor.execute(
        "UPDATE teams SET name = ? WHERE id = ?", 
        (team_data.name, team_id)
    )
    
    # If budget changed, update both total and remaining
    if team_data.total_budget is not None:
        spent = team["total_budget"] - team["remaining_budget"]
        new_remaining = team_data.total_budget - spent
        cursor.execute(
            "UPDATE teams SET total_budget = ?, remaining_budget = ? WHERE id = ?",
            (team_data.total_budget, new_remaining, team_id)
        )
    
    conn.commit()
    conn.close()
    
    return {"message": "Team updated successfully"}

@router.delete("/{team_id}")
async def delete_team(
    tournament_id: int,
    team_id: int,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Delete team"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM teams WHERE id = ? AND tournament_id = ?", 
        (team_id, tournament_id)
    )
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Unassign all players from this team
    cursor.execute(
        """UPDATE players 
           SET team_id = NULL, is_assigned = 0, bid_amount = 0 
           WHERE team_id = ?""",
        (team_id,)
    )
    
    cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
    
    conn.commit()
    conn.close()
    
    return {"message": "Team deleted successfully"}

@router.post("/{team_id}/players")
async def add_player_to_team(
    tournament_id: int,
    team_id: int,
    player: PlayerCreate,
    bid_amount: float,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Manually add player to team"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT remaining_budget FROM teams WHERE id = ? AND tournament_id = ?", 
        (team_id, tournament_id)
    )
    team = cursor.fetchone()
    
    if not team:
        conn.close()
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team["remaining_budget"] < bid_amount:
        conn.close()
        raise HTTPException(status_code=400, detail="Insufficient budget")
    
    try:
        cursor.execute(
            """INSERT INTO players 
               (tournament_id, team_id, emp_id, name, type, bid_amount, is_assigned) 
               VALUES (?, ?, ?, ?, ?, ?, 1)""",
            (tournament_id, team_id, player.emp_id, player.name, 
             player.type, bid_amount)
        )
        
        cursor.execute(
            "UPDATE teams SET remaining_budget = remaining_budget - ? WHERE id = ?",
            (bid_amount, team_id)
        )
        
        conn.commit()
        conn.close()
        
        return {"message": "Player added successfully"}
    
    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        raise HTTPException(
            status_code=400, 
            detail="Player with this emp_id already exists in tournament"
        )

@router.delete("/{team_id}/players/{emp_id}")
async def remove_player_from_team(
    tournament_id: int,
    team_id: int,
    emp_id: str,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Remove player from team"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT * FROM players 
           WHERE tournament_id = ? AND team_id = ? AND emp_id = ?""",
        (tournament_id, team_id, emp_id)
    )
    player = cursor.fetchone()
    
    if not player:
        conn.close()
        raise HTTPException(status_code=404, detail="Player not found")
    
    cursor.execute(
        "UPDATE teams SET remaining_budget = remaining_budget + ? WHERE id = ?",
        (player["bid_amount"], team_id)
    )
    
    cursor.execute(
        """DELETE FROM players 
           WHERE tournament_id = ? AND team_id = ? AND emp_id = ?""",
        (tournament_id, team_id, emp_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": "Player removed successfully"}


@router.post("/{team_id}/captain")
async def set_team_captain(
    tournament_id: int,
    team_id: int,
    data: dict,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Set captain and/or vice-captain for a team"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if team exists
    cursor.execute(
        "SELECT * FROM teams WHERE id = ? AND tournament_id = ?",
        (team_id, tournament_id)
    )
    team = cursor.fetchone()
    
    if not team:
        conn.close()
        raise HTTPException(status_code=404, detail="Team not found")
    
    captain_id = data.get('captain_id')
    vice_captain_id = data.get('vice_captain_id')
    
    # Verify players are in this team
    if captain_id:
        cursor.execute(
            "SELECT * FROM players WHERE emp_id = ? AND team_id = ?",
            (captain_id, team_id)
        )
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Captain must be a member of this team")
    
    if vice_captain_id:
        cursor.execute(
            "SELECT * FROM players WHERE emp_id = ? AND team_id = ?",
            (vice_captain_id, team_id)
        )
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Vice-captain must be a member of this team")
    
    # Update team
    cursor.execute(
        "UPDATE teams SET captain_id = ?, vice_captain_id = ? WHERE id = ?",
        (captain_id, vice_captain_id, team_id)
    )
    
    conn.commit()
    conn.close()
    
    return {
        "message": "Captain and vice-captain updated successfully",
        "captain_id": captain_id,
        "vice_captain_id": vice_captain_id
    }