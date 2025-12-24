import sqlite3

DATABASE_PATH = "cricket_auction.db"

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tournaments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT NOT NULL
        )
    """)
    
    # Teams table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            total_budget REAL NOT NULL,
            remaining_budget REAL NOT NULL,
            captain_id TEXT,
            vice_captain_id TEXT,
            FOREIGN KEY (tournament_id) REFERENCES tournaments (id) ON DELETE CASCADE,
            UNIQUE(tournament_id, name)
        )
    """)
    
    # Players table - Check if image_filename column exists, add if not
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            team_id INTEGER,
            emp_id TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            bid_amount REAL DEFAULT 0,
            is_assigned BOOLEAN DEFAULT 0,
            image_filename TEXT,
            FOREIGN KEY (tournament_id) REFERENCES tournaments (id) ON DELETE CASCADE,
            FOREIGN KEY (team_id) REFERENCES teams (id) ON DELETE SET NULL,
            UNIQUE(tournament_id, emp_id)
        )
    """)
    
    # Check if image_filename column exists, if not add it
    try:
        cursor.execute("SELECT image_filename FROM players LIMIT 1")
    except sqlite3.OperationalError:
        # Column doesn't exist, add it
        cursor.execute("ALTER TABLE players ADD COLUMN image_filename TEXT")
        print("✅ Added image_filename column to players table")
    
    # Check if captain columns exist in teams, if not add them
    try:
        cursor.execute("SELECT captain_id FROM teams LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE teams ADD COLUMN captain_id TEXT")
        cursor.execute("ALTER TABLE teams ADD COLUMN vice_captain_id TEXT")
        print("✅ Added captain columns to teams table")
    
    # Insert default users if not exists
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
            ("admin", "admin@123", "admin")
        )
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
            ("auctioneer", "auction@123", "auctioneer")
        )
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
            ("guest", "guest123", "guest")
        )
    except sqlite3.IntegrityError:
        pass
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")