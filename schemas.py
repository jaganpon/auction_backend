from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# ==================== AUTH SCHEMAS ====================

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    role: str
    token: str

# ==================== TOURNAMENT SCHEMAS ====================

class TournamentCreate(BaseModel):
    name: str
    teams: List[Dict[str, Any]]

class TournamentUpdate(BaseModel):
    name: str

# ==================== TEAM SCHEMAS ====================

class TeamUpdate(BaseModel):
    name: str
    total_budget: Optional[float] = None

# ==================== PLAYER SCHEMAS ====================

class PlayerCreate(BaseModel):
    emp_id: str
    name: str
    type: str

class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None

class PlayerAssign(BaseModel):
    tournament_id: int
    team_id: int
    emp_id: str
    bid_amount: float
