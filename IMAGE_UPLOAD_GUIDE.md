# Player Image Upload Guide

## Overview

The Cricket Auction system supports player images both for bulk upload and individual management.

## Method 1: Bulk Upload with CSV/Excel

### Step 1: Prepare Your Images

1. Create a folder with all player images
2. Name images using the player's `emp_id` (e.g., `EMP001.jpg`, `EMP002.png`)
3. Supported formats: JPG, PNG, WebP
4. Recommended size: 500x500px or larger (square images work best)

### Step 2: Update Your CSV/Excel File

Add an `image_filename` column to your player list:

**Example CSV:**

```csv
emp_id,name,type,image_filename
EMP001,Virat Kohli,Batsman,EMP001.jpg
EMP002,Jasprit Bumrah,Bowler,EMP002.png
EMP003,Hardik Pandya,All-Rounder,EMP003.jpg
```

**Example Excel:**
| emp_id | name | type | image_filename |
|--------|------|------|----------------|
| EMP001 | Virat Kohli | Batsman | EMP001.jpg |
| EMP002 | Jasprit Bumrah | Bowler | EMP002.png |
| EMP003 | Hardik Pandya | All-Rounder | EMP003.jpg |

### Step 3: Upload Images to Server

Copy all images to the backend's `player_images` folder:

```bash
# On server
cp /path/to/your/images/* /path/to/backend/player_images/
```

**For Windows:**

```cmd
copy C:\path\to\your\images\* D:\backend\player_images\
```

### Step 4: Upload Player Data

Upload your CSV/Excel file through the admin panel. The system will automatically link images based on the `image_filename` column.

## Method 2: Individual Image Upload (After Bulk Data Upload)

### From Tournament View Page:

1. Navigate to the tournament
2. Find the player in the list
3. Click the "📷 Image" button next to the player
4. Select and upload the image
5. Image is automatically saved with `emp_id.extension` format

### Features:

- ✅ Upload/Replace images anytime
- ✅ Preview before saving
- ✅ Automatic file naming (emp_id based)
- ✅ Validation (format, size)
- ✅ Max size: 5MB per image

## Image Storage Structure

```
backend/
└── player_images/
    ├── EMP001.jpg
    ├── EMP002.png
    ├── EMP003.jpg
    └── ...
```

## Image Display Locations

1. **Auction Panel** - Large circular display with player info
2. **Tournament View** - Thumbnail in player list (future enhancement)
3. **Team Rosters** - Player cards (future enhancement)

## Best Practices

### Image Specifications:

- **Format**: JPG, PNG, or WebP
- **Dimensions**: 500x500px minimum (square)
- **Size**: Under 5MB
- **Aspect Ratio**: 1:1 (square) recommended
- **Quality**: High resolution for clarity

### Naming Convention:

- Use `emp_id` as the base filename
- Example: If emp_id is "EMP001", name file "EMP001.jpg"
- Case-sensitive: Match exactly with your CSV data

### Bulk Upload Workflow:

```
1. Prepare images → Name with emp_id
2. Copy to player_images folder
3. Update CSV with image_filename column
4. Upload CSV through admin panel
5. Verify images appear in auction panel
```

## Troubleshooting

### Image Not Showing?

1. Check filename matches emp_id exactly
2. Verify file is in `player_images` folder
3. Check file extension is supported (jpg, png, webp)
4. Ensure file size is under 5MB
5. Try refreshing the page

### Upload Failed?

- Check file format (must be image)
- Verify file size (max 5MB)
- Ensure you have admin permissions
- Check server disk space

### Placeholder Image

If no image is uploaded or found, a default placeholder is shown with "No Image" text.

## API Endpoints

### Upload Player Image

```
POST /api/tournaments/{tournament_id}/players/{emp_id}/image
```

**Headers:**

- Authorization: Bearer {token}
- Content-Type: multipart/form-data

**Body:**

- file: (image file)

**Response:**

```json
{
  "message": "Image uploaded successfully",
  "filename": "EMP001.jpg"
}
```

### Access Image

```
GET /images/{filename}
```

Example: `http://localhost:8000/images/EMP001.jpg`

## Advanced: Automated Bulk Image Upload Script

Create a script to upload images programmatically:

```python
import requests
import os

API_URL = "http://localhost:8000/api"
TOKEN = "your-admin-token"
TOURNAMENT_ID = 1
IMAGES_FOLDER = "./player_images"

headers = {"Authorization": f"Bearer {TOKEN}"}

for filename in os.listdir(IMAGES_FOLDER):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        emp_id = os.path.splitext(filename)[0]  # Get emp_id from filename

        with open(os.path.join(IMAGES_FOLDER, filename), 'rb') as f:
            files = {'file': f}
            response = requests.post(
                f"{API_URL}/tournaments/{TOURNAMENT_ID}/players/{emp_id}/image",
                headers=headers,
                files=files
            )
            print(f"{emp_id}: {response.json()['message']}")
```

## Security Notes

- Images are stored on server filesystem
- Access controlled through API authentication
- File type validation prevents malicious uploads
- Size limits prevent server overload
- Original filenames are standardized for security

## Future Enhancements

- [ ] Image compression on upload
- [ ] Thumbnail generation
- [ ] Cloud storage integration (AWS S3, etc.)
- [ ] Bulk image upload through UI
- [ ] Image cropping tool
- [ ] Multiple image per player (gallery)
