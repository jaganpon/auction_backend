#!/usr/bin/env python3
"""
Create sample Excel file for cricket auction player upload
"""

import pandas as pd

# Sample player data
players = [
    {"emp_id": "E001", "name": "Virat Kohli", "type": "Batsman"},
    {"emp_id": "E002", "name": "Rohit Sharma", "type": "Batsman"},
    {"emp_id": "E003", "name": "Jasprit Bumrah", "type": "Bowler"},
    {"emp_id": "E004", "name": "Mohammed Shami", "type": "Bowler"},
    {"emp_id": "E005", "name": "MS Dhoni", "type": "Wicket-keeper"},
    {"emp_id": "E006", "name": "Rishabh Pant", "type": "Wicket-keeper"},
    {"emp_id": "E007", "name": "Hardik Pandya", "type": "All-rounder"},
    {"emp_id": "E008", "name": "Ravindra Jadeja", "type": "All-rounder"},
    {"emp_id": "E009", "name": "KL Rahul", "type": "Batsman"},
    {"emp_id": "E010", "name": "Shikhar Dhawan", "type": "Batsman"},
    {"emp_id": "E011", "name": "Yuzvendra Chahal", "type": "Bowler"},
    {"emp_id": "E012", "name": "Kuldeep Yadav", "type": "Bowler"},
    {"emp_id": "E013", "name": "Dinesh Karthik", "type": "Wicket-keeper"},
    {"emp_id": "E014", "name": "Ravichandran Ashwin", "type": "All-rounder"},
    {"emp_id": "E015", "name": "Shreyas Iyer", "type": "Batsman"},
    {"emp_id": "E016", "name": "Shubman Gill", "type": "Batsman"},
    {"emp_id": "E017", "name": "Mohammed Siraj", "type": "Bowler"},
    {"emp_id": "E018", "name": "Bhuvneshwar Kumar", "type": "Bowler"},
    {"emp_id": "E019", "name": "Sanju Samson", "type": "Wicket-keeper"},
    {"emp_id": "E020", "name": "Washington Sundar", "type": "All-rounder"},
    {"emp_id": "E021", "name": "Axar Patel", "type": "All-rounder"},
    {"emp_id": "E022", "name": "Suryakumar Yadav", "type": "Batsman"},
    {"emp_id": "E023", "name": "Ishan Kishan", "type": "Wicket-keeper"},
    {"emp_id": "E024", "name": "Deepak Chahar", "type": "Bowler"},
    {"emp_id": "E025", "name": "Shardul Thakur", "type": "All-rounder"},
    {"emp_id": "E026", "name": "Prithvi Shaw", "type": "Batsman"},
    {"emp_id": "E027", "name": "Ruturaj Gaikwad", "type": "Batsman"},
    {"emp_id": "E028", "name": "Avesh Khan", "type": "Bowler"},
    {"emp_id": "E029", "name": "Rahul Tewatia", "type": "All-rounder"},
    {"emp_id": "E030", "name": "Venkatesh Iyer", "type": "All-rounder"},
]

# Create DataFrame
df = pd.DataFrame(players)

# Save to Excel
output_file = "sample_players.xlsx"
df.to_excel(output_file, index=False, engine='openpyxl')

print(f"✅ Created {output_file} with {len(players)} players")
print("\nColumns:")
for col in df.columns:
    print(f"  - {col}")
print("\nFile ready for upload!")
print(f"\nPreview:")
print(df.head(5))