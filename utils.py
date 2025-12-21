import pandas as pd
import io
import os
from typing import Dict
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

security = HTTPBearer()

# ==================== FILE PROCESSING ====================

def read_uploaded_file(file_content: bytes, filename: str) -> pd.DataFrame:
    """
    Read uploaded file and return pandas DataFrame
    Supports: CSV, XLSX, XLS
    """
    file_extension = os.path.splitext(filename)[1].lower()
    
    try:
        if file_extension == '.csv':
            # Try different encodings for CSV
            try:
                df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(file_content), encoding='latin-1')
                
        elif file_extension == '.xlsx':
            # Modern Excel format
            df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
            
        elif file_extension == '.xls':
            # Legacy Excel format
            df = pd.read_excel(io.BytesIO(file_content), engine='xlrd')
            
        else:
            raise ValueError(
                f"Unsupported file format: {file_extension}. "
                f"Supported formats: .csv, .xlsx, .xls"
            )
        
        return df
        
    except Exception as e:
        raise ValueError(f"Error reading {file_extension} file: {str(e)}")

# ==================== AUTH UTILITIES ====================

def create_access_token(data: dict) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise HTTPException(
                status_code=401, 
                detail="Invalid authentication credentials"
            )
        return {"username": username, "role": role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

def require_role(allowed_roles: list):
    """Dependency to check user role"""
    def role_checker(current_user: dict = Depends(verify_token)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker
