import csv
import sqlite3
import os

# --- CORRECTED PATH LOGIC ---
# Get the directory of the current script (.../backend/data)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Get the backend directory by going up one level
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
# Get the project's root directory by going up one more level
ROOT_DIR = os.path.dirname(BACKEND_DIR)

# Construct all paths from the root directory
DB_PATH = os.path.join(ROOT_DIR, 'app.db')
SCHEMA_PATH = os.path.join(BACKEND_DIR, 'storage/schema.sql')
PROBLEMS_CSV_PATH = os.path.join(CURRENT_DIR, 'problems.csv')
ATTEMPTS_CSV_PATH = os.path.join(CURRENT_DIR, 'attempts.csv')
# --- END OF CORRECTIONS ---


# Delete the old database file if it exists
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# Connect to SQLite DB (it will be created if it doesn't exist)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Create tables from schema
print("Creating database schema...")
with open(SCHEMA_PATH) as f:
    cur.executescript(f.read())

# Load problems.csv
print("Loading problems...")
with open(PROBLEMS_CSV_PATH) as f:
    r = csv.DictReader(f)
    for row in r:
        # FIX: Removed the '1' from the beginning of the SQL statement
        cur.execute("INSERT OR REPLACE INTO problems (problem_id, title, difficulty, concepts) VALUES (?, ?, ?, ?)",
                    (row["problem_id"], row["title"], int(row["difficulty"]), row["concepts"]))

# Load attempts.csv
print("Loading attempts...")
with open(ATTEMPTS_CSV_PATH) as f:
    r = csv.DictReader(f)
    for row in r:
        cur.execute("INSERT INTO attempts(user_id, problem_id, ts, outcome, attempts, minutes) VALUES (?, ?, ?, ?, ?, ?)",
                    (row["user_id"], row["problem_id"], row["timestamp"], int(row["outcome"]), int(row["attempts"]), int(row["time_spent_minutes"] or 0)))

conn.commit()
conn.close()

print(f"✅ Database created and populated at '{DB_PATH}'")