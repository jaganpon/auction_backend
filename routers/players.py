from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
import sqlite3
import os
from pathlib import Path
from database import get_db
from schemas import PlayerCreate, PlayerUpdate
from utils import verify_token, require_role, read_uploaded_file

router = APIRouter(tags=["Players"])

# Create images directory if it doesn't exist
IMAGES_DIR = Path("player_images")
IMAGES_DIR.mkdir(exist_ok=True)

@router.get("/api/tournaments/{tournament_id}/players")
async def get_players(
    tournament_id: int, 
    current_user: dict = Depends(verify_token)
):
    """Get all players for a tournament"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM players WHERE tournament_id = ?", 
        (tournament_id,)
    )
    players = cursor.fetchall()
    conn.close()
    
    return [dict(p) for p in players]

@router.post("/api/tournaments/{tournament_id}/players")
async def create_player(
    tournament_id: int,
    player_data: PlayerCreate,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Create a single player"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check tournament exists
    cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    try:
        cursor.execute(
            """INSERT INTO players (tournament_id, emp_id, name, type) 
               VALUES (?, ?, ?, ?)""",
            (tournament_id, player_data.emp_id, player_data.name, player_data.type)
        )
        player_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
        player = cursor.fetchone()
        conn.close()
        
        return dict(player)
    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        raise HTTPException(
            status_code=400, 
            detail="Player with this emp_id already exists in this tournament"
        )

@router.post("/api/tournaments/{tournament_id}/players/upload")
async def upload_players(
    tournament_id: int,
    file: UploadFile = File(...),
    mode: str = "replace",
    current_user: dict = Depends(require_role(["admin"]))
):
    """
    Upload players from CSV or Excel file
    Supports: .csv, .xlsx, .xls
    Required columns: emp_id, name, type
    """
    
    # Validate file type
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if tournament exists
    cursor.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    try:
        # Read file content
        contents = await file.read()
        
        # Parse file into DataFrame
        try:
            df = read_uploaded_file(contents, file.filename)
        except ValueError as e:
            conn.close()
            raise HTTPException(status_code=400, detail=str(e))
        
        # Check if empty
        if df.empty:
            conn.close()
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Check required columns
        required_columns = ['emp_id', 'name', 'type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            conn.close()
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns: {', '.join(missing_columns)}"
            )
        
        # Replace mode: delete existing players
        if mode == "replace":
            cursor.execute(
                "DELETE FROM players WHERE tournament_id = ?", 
                (tournament_id,)
            )
        
        added_count = 0
        skipped_count = 0
        errors = []
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Validate data
                emp_id = str(row['emp_id']).strip()
                name = str(row['name']).strip()
                player_type = str(row['type']).strip()
                image_filename = str(row.get('image_filename', '')).strip() if 'image_filename' in row else None
                
                # Validate required fields
                if not emp_id or emp_id.lower() in ['nan', 'none', '']:
                    raise ValueError("emp_id is required")
                if not name or name.lower() in ['nan', 'none', '']:
                    raise ValueError("name is required")
                if not player_type or player_type.lower() in ['nan', 'none', '']:
                    raise ValueError("type is required")
                
                # Insert player
                cursor.execute(
                    """INSERT INTO players (tournament_id, emp_id, name, type, image_filename) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (tournament_id, emp_id, name, player_type, image_filename)
                )
                added_count += 1
                
            except sqlite3.IntegrityError:
                skipped_count += 1
                errors.append(
                    f"Row {index + 2}: Duplicate emp_id '{row.get('emp_id', 'Unknown')}'"
                )
            except Exception as e:
                skipped_count += 1
                errors.append(f"Row {index + 2}: {str(e)}")
        
        conn.commit()
        conn.close()
        
        response = {
            "success": True,
            "message": "Players uploaded successfully",
            "details": {
                "file_name": file.filename,
                "file_type": file_extension,
                "mode": mode,
                "total_rows": len(df),
                "players_added": added_count,
                "players_skipped": skipped_count
            }
        }
        
        if errors:
            response["errors"] = errors[:10]
            if len(errors) > 10:
                response["errors"].append(f"... and {len(errors) - 10} more errors")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(
            status_code=400, 
            detail=f"Error processing file: {str(e)}"
        )

@router.put("/api/tournaments/{tournament_id}/players/{emp_id}")
async def update_player(
    tournament_id: int,
    emp_id: str,
    player_data: PlayerUpdate,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Update player details"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM players WHERE tournament_id = ? AND emp_id = ?", 
        (tournament_id, emp_id)
    )
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Player not found")
    
    updates = []
    values = []
    
    if player_data.name is not None:
        updates.append("name = ?")
        values.append(player_data.name)
    
    if player_data.type is not None:
        updates.append("type = ?")
        values.append(player_data.type)
    
    if updates:
        values.extend([tournament_id, emp_id])
        cursor.execute(
            f"UPDATE players SET {', '.join(updates)} WHERE tournament_id = ? AND emp_id = ?",
            values
        )
        conn.commit()
    
    conn.close()
    return {"message": "Player updated successfully"}

@router.delete("/api/tournaments/{tournament_id}/players/{emp_id}")
async def delete_player(
    tournament_id: int,
    emp_id: str,
    current_user: dict = Depends(require_role(["admin"]))
):
    """Delete player from tournament"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM players WHERE tournament_id = ? AND emp_id = ?", 
        (tournament_id, emp_id)
    )
    player = cursor.fetchone()
    
    if not player:
        conn.close()
        raise HTTPException(status_code=404, detail="Player not found")
    
    # If assigned, restore team budget
    if player["team_id"] and player["bid_amount"]:
        cursor.execute(
            "UPDATE teams SET remaining_budget = remaining_budget + ? WHERE id = ?",
            (player["bid_amount"], player["team_id"])
        )
    
    cursor.execute(
        "DELETE FROM players WHERE tournament_id = ? AND emp_id = ?", 
        (tournament_id, emp_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": "Player deleted successfully"}


@router.post("/api/players/{emp_id}/image")
async def upload_player_image(
    emp_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role(["admin"]))
):
    """Upload or update player image globally (across all tournaments)"""
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPG, PNG, and WebP images are allowed"
        )
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if player exists in ANY tournament with this emp_id (global player update)
    cursor.execute(
        "SELECT * FROM players WHERE emp_id = ?",
        (emp_id,)
    )
    players = cursor.fetchall()
    
    if not players:
        conn.close()
        raise HTTPException(status_code=404, detail="Player not found")
    
    try:
        # Create filename: emp_id.extension
        file_ext = file.filename.split('.')[-1].lower()
        new_filename = f"{emp_id}.{file_ext}"
        file_path = IMAGES_DIR / new_filename
        
        # Save file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Update ALL players with this emp_id across all tournaments
        cursor.execute(
            "UPDATE players SET image_filename = ? WHERE emp_id = ?",
            (new_filename, emp_id)
        )
        
        updated_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return {
            "message": "Image uploaded successfully",
            "filename": new_filename,
            "updated_players": updated_count
        }
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")