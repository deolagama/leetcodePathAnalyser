import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # --- 1. ADD THIS IMPORT ---

# Use the import path that works for your environment
from backend.models.heuristic_estimator import get_user_skills, recommend_problems_for_user

DB_PATH = "app.db"
app = FastAPI()

# --- 2. ADD THIS ENTIRE BLOCK ---
# This configures CORS to allow your frontend to make requests
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)
# --- END OF NEW BLOCK ---

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/skills/{user_id}")
def get_skills_route(user_id: str):
    """
    Endpoint to get the estimated skills for a given user.
    """
    try:
        conn = get_db_connection()
        skills = get_user_skills(conn, user_id)
        conn.close()
        return {"user_id": user_id, "skills": skills}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommend/{user_id}")
def get_recommendations_route(user_id: str, k: int = 5):
    """
    Endpoint to recommend the next k problems for a user.
    """
    try:
        conn = get_db_connection()
        recommendations = recommend_problems_for_user(conn, user_id, k)
        conn.close()
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))