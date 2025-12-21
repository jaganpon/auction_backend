from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from schemas import PlayerAssign
from utils import require_role

router = APIRouter(prefix="/api", tags=["Auction"])

@router.post("/auction/assign")
async def assign_player_in_auction(
    assignment: PlayerAssign,
    current_user: dict = Depends(require_role(["admin", "auctioneer"]))
):
    """Assign player to team during auction"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT remaining_budget FROM teams WHERE id = ? AND tournament_id = ?",
        (assignment.team_id, assignment.tournament_id)
    )
    team = cursor.fetchone()
    
    if not team:
        conn.close()
        raise HTTPException(status_code=404, detail="Team not found")
    
    if team["remaining_budget"] < assignment.bid_amount:
        conn.close()
        raise HTTPException(status_code=400, detail="Insufficient budget")
    
    cursor.execute(
        """UPDATE players 
           SET team_id = ?, bid_amount = ?, is_assigned = 1 
           WHERE tournament_id = ? AND emp_id = ? AND is_assigned = 0""",
        (assignment.team_id, assignment.bid_amount, 
         assignment.tournament_id, assignment.emp_id)
    )
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(
            status_code=400, 
            detail="Player not found or already assigned"
        )
    
    cursor.execute(
        "UPDATE teams SET remaining_budget = remaining_budget - ? WHERE id = ?",
        (assignment.bid_amount, assignment.team_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": "Player assigned successfully"}

@router.get("/tournaments/{tournament_id}/auction/status")
async def get_auction_status(
    tournament_id: int,
    current_user: dict = Depends(require_role(["admin", "auctioneer"]))
):
    """Get auction status for tournament"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT COUNT(*) as total FROM players WHERE tournament_id = ?",
        (tournament_id,)
    )
    total = cursor.fetchone()["total"]
    
    cursor.execute(
        """SELECT COUNT(*) as assigned 
           FROM players 
           WHERE tournament_id = ? AND is_assigned = 1""",
        (tournament_id,)
    )
    assigned = cursor.fetchone()["assigned"]
    
    conn.close()
    
    return {
        "total_players": total,
        "assigned_players": assigned,
        "remaining_players": total - assigned,
        "is_complete": total == assigned
    }
