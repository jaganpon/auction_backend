from fastapi import APIRouter, HTTPException, Depends
from database import get_db
from schemas import UserLogin, UserResponse
from utils import create_access_token, verify_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=UserResponse)
async def login(user_login: UserLogin):
    """User login endpoint"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?", 
        (user_login.username, user_login.password)
    )
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="Invalid username or password"
        )
    
    token = create_access_token({
        "sub": user["username"], 
        "role": user["role"]
    })
    
    return {
        "username": user["username"],
        "role": user["role"],
        "token": token
    }

@router.get("/verify")
async def verify(current_user: dict = Depends(verify_token)):
    """Verify token validity"""
    return {"valid": True, "user": current_user}

@router.post("/logout")
async def logout():
    """Logout endpoint"""
    return {"message": "Logged out successfully"}
