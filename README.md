# Cricket Auction Backend API

A FastAPI-based REST API for managing cricket player auctions with SQLite database.

## 🚀 Features

- **RESTful API** with automatic documentation
- **JWT Authentication** with role-based access control
- **File Upload Support** - CSV, XLSX, XLS formats
- **SQLite Database** - Lightweight and portable
- **CORS Enabled** - Works with any frontend
- **Auto-generated API Docs** - Swagger UI and ReDoc

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

## 🛠️ Installation

1. **Navigate to backend directory**

   ```bash
   cd cricket-auction-backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**

   ```bash
   # Option 1: Using Python
   python main.py

   # Option 2: Using uvicorn directly
   uvicorn main:app --reload
   ```

   Server will start at `http://localhost:8000`

## 📦 Dependencies

```
fastapi==0.109.0           # Web framework
uvicorn[standard]==0.27.0  # ASGI server
python-multipart==0.0.6    # File upload support
pydantic==2.5.3            # Data validation
PyJWT==2.8.0               # JWT tokens
python-jose[cryptography]  # JWT encoding/decoding
pandas==2.1.4              # Data processing
openpyxl==3.1.2           # Excel .xlsx support
xlrd==2.0.1               # Excel .xls support
```

## 🏗️ Project Structure

```
cricket-auction-backend/
├── main.py                 # Main FastAPI application
├── database.py            # Database setup and connection
├── schemas.py             # Pydantic models
├── utils.py               # Utility functions (auth, file handling)
├── requirements.txt       # Python dependencies
├── cricket_auction.db     # SQLite database (auto-created)
├── create_sample_csv.py   # Helper script for sample data
└── routers/               # API route modules
    ├── __init__.py
    ├── auth.py           # Authentication endpoints
    ├── tournaments.py    # Tournament management
    ├── teams.py          # Team management
    ├── players.py        # Player management
    └── auction.py        # Auction operations
```

## 🗄️ Database Schema

### Users Table

```sql
id              INTEGER PRIMARY KEY
username        TEXT UNIQUE
password        TEXT
role            TEXT (admin/auctioneer/guest)
created_at      TIMESTAMP
```

### Tournaments Table

```sql
id              INTEGER PRIMARY KEY
name            TEXT
created_at      TIMESTAMP
created_by      TEXT
```

### Teams Table

```sql
id              INTEGER PRIMARY KEY
tournament_id   INTEGER FOREIGN KEY
name            TEXT
total_budget    REAL
remaining_budget REAL
```

### Players Table

```sql
id              INTEGER PRIMARY KEY
tournament_id   INTEGER FOREIGN KEY
team_id         INTEGER FOREIGN KEY (nullable)
emp_id          TEXT UNIQUE
name            TEXT
type            TEXT
bid_amount      REAL DEFAULT 0
is_assigned     BOOLEAN DEFAULT 0
```

## 🔐 Authentication

### JWT Token-based Authentication

- **Token Expiry**: 24 hours (1440 minutes)
- **Algorithm**: HS256
- **Secret Key**: Configure in `utils.py`

### Default Users

| Username   | Password   | Role       |
| ---------- | ---------- | ---------- |
| admin      | admin123   | admin      |
| auctioneer | auction123 | auctioneer |
| guest      | guest123   | guest      |

### Login Request

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Response

```json
{
  "username": "admin",
  "role": "admin",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Using Token in Requests

```bash
curl -X GET http://localhost:8000/api/tournaments \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📡 API Endpoints

### Authentication

```
POST   /api/auth/login          # User login
GET    /api/auth/verify         # Verify token
POST   /api/auth/logout         # Logout
```

### Tournaments

```
GET    /api/tournaments                    # List all tournaments
POST   /api/tournaments                    # Create tournament
GET    /api/tournaments/{id}               # Get tournament details
PUT    /api/tournaments/{id}               # Update tournament
DELETE /api/tournaments/{id}               # Delete tournament
```

### Teams

```
PUT    /api/tournaments/{id}/teams/{team_id}              # Update team
DELETE /api/tournaments/{id}/teams/{team_id}              # Delete team
POST   /api/tournaments/{id}/teams/{team_id}/players      # Add player to team
DELETE /api/tournaments/{id}/teams/{team_id}/players/{emp_id}  # Remove player
```

### Players

```
GET    /api/tournaments/{id}/players        # Get all players
POST   /api/tournaments/{id}/players/upload # Upload players (CSV/Excel)
PUT    /api/tournaments/{id}/players/{emp_id}  # Update player
DELETE /api/tournaments/{id}/players/{emp_id}  # Delete player
```

### Auction

```
POST   /api/auction/assign                      # Assign player to team
GET    /api/tournaments/{id}/auction/status     # Get auction status
```

## 📤 File Upload

### Supported Formats

- CSV (`.csv`)
- Excel Modern (`.xlsx`)
- Excel Legacy (`.xls`)

### Required Columns

```
emp_id    - Unique identifier
name      - Player name
type      - Player type/category
```

### Upload Request

```bash
curl -X POST "http://localhost:8000/api/tournaments/1/players/upload?mode=replace" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@players.csv"
```

### Upload Modes

- **replace**: Delete existing players and upload new ones
- **append**: Add to existing players (skip duplicates)

## 🔒 Role-Based Access Control

### Admin Role

- ✅ All operations
- ✅ Create/edit/delete tournaments
- ✅ Manage teams and players
- ✅ Conduct auctions

### Auctioneer Role

- ✅ Conduct auctions
- ✅ Assign players
- ✅ View data
- ❌ Cannot modify tournament structure

### Guest Role

- ✅ View tournaments
- ✅ View players and teams
- ❌ Cannot make any changes

## 📚 API Documentation

### Swagger UI

Visit `http://localhost:8000/docs` for interactive API documentation

### ReDoc

Visit `http://localhost:8000/redoc` for alternative documentation

## 🧪 Testing

### Create Sample Data

```bash
python create_sample_csv.py
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/

# API health
curl http://localhost:8000/api/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

## ⚙️ Configuration

### Change Database Location

Edit `database.py`:

```python
DATABASE_PATH = "path/to/your/database.db"
```

### Change JWT Secret

Edit `utils.py`:

```python
SECRET_KEY = "your-secret-key-here"
```

### Change Token Expiry

Edit `utils.py`:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours
```

### Change Server Port

```bash
uvicorn main:app --reload --port 8080
```

### CORS Configuration

Edit `main.py`:

```python
allow_origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    "https://yourdomain.com"
]
```

## 🐛 Troubleshooting

### Issue: "Module not found"

**Solution**: Activate virtual environment and reinstall dependencies

```bash
pip install -r requirements.txt
```

### Issue: "Database locked"

**Solution**: Close any other connections to the database file

### Issue: "File upload fails"

**Solution**:

- Check file format (CSV, XLSX, XLS)
- Verify required columns exist
- Check file size limits

### Issue: "Token expired"

**Solution**: Login again to get a new token

## 🔧 Development

### Add New Endpoint

1. Create route function in appropriate router file
2. Add to router with decorator: `@router.get("/path")`
3. Import and include router in `main.py`

### Add New Table

1. Add CREATE TABLE statement in `database.py`
2. Update `init_db()` function
3. Delete old `cricket_auction.db` to recreate

## 📊 Database Management

### View Database

```bash
# Using sqlite3 command line
sqlite3 cricket_auction.db

# List tables
.tables

# View table structure
.schema players

# Query data
SELECT * FROM players;

# Exit
.quit
```

### Backup Database

```bash
cp cricket_auction.db cricket_auction_backup.db
```

### Reset Database

```bash
rm cricket_auction.db
python main.py  # Will recreate database
```

## 🚀 Deployment

### Production Checklist

- [ ] Change JWT secret key
- [ ] Use environment variables for sensitive data
- [ ] Set up HTTPS
- [ ] Configure CORS for production domain
- [ ] Set up proper logging
- [ ] Use production database (PostgreSQL recommended)
- [ ] Set up monitoring and error tracking

### Run in Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📝 Logging

Logs are automatically generated by uvicorn. To customize:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## 📞 Support

For issues:

- Check API documentation at `/docs`
- Review error messages in console
- Check database integrity

## 🔄 Updates

Regular maintenance tasks:

- Update dependencies: `pip install --upgrade -r requirements.txt`
- Backup database regularly
- Monitor disk space
- Review security advisories
