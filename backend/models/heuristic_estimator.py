import json
from datetime import datetime
import math

DIFFICULTY_WEIGHTS = {1: 1.0, 2: 1.5, 3: 2.0} # Easy, Medium, Hard
RECENCY_HALF_LIFE_DAYS = 30 # Skills decay to half-strength in 30 days

def get_user_skills(conn, user_id: str):
    """
    Calculates user skills based on a weighted average of successful attempts,
    with a decay factor for older attempts.
    """
    cur = conn.cursor()
    
    query = """
    SELECT p.concepts, a.outcome, a.ts
    FROM attempts a
    JOIN problems p ON a.problem_id = p.problem_id
    WHERE a.user_id = ?
    """
    
    cur.execute(query, (user_id,))
    attempts = cur.fetchall()
    
    if not attempts:
        return {}

    # Store total weighted score and total weight for each concept
    concept_scores = {}
    concept_weights = {}

    for attempt in attempts:
        concepts = json.loads(attempt["concepts"])
        outcome = attempt["outcome"] # 1 for pass, 0 for fail
        timestamp = datetime.fromisoformat(attempt["ts"])
        days_ago = (datetime.now() - timestamp).days

        # Apply exponential decay based on recency
        recency_weight = math.exp(-0.693 * days_ago / RECENCY_HALF_LIFE_DAYS)
        
        # We don't use difficulty here yet for simplicity, but you can add it
        # weight = DIFFICULTY_WEIGHTS.get(attempt["difficulty"], 1.0) * recency_weight

        for concept in concepts:
            # Initialize if first time seeing concept
            if concept not in concept_scores:
                concept_scores[concept] = 0.0
                concept_weights[concept] = 0.0

            # Add weighted outcome to the score
            concept_scores[concept] += outcome * recency_weight
            # Add the weight to the total weight
            concept_weights[concept] += recency_weight

    # Calculate the final skill ratio for each concept
    final_skills = {}
    for concept, total_score in concept_scores.items():
        total_weight = concept_weights[concept]
        if total_weight > 0:
            final_skills[concept] = round(total_score / total_weight, 3)
    
    return final_skills


def recommend_problems_for_user(conn, user_id: str, k: int):
    """
    Recommends k problems by prioritizing those that target the user's weakest concepts.
    """
    user_skills = get_user_skills(conn, user_id)
    if not user_skills:
        return [] # Cannot recommend if user has no skills data

    cur = conn.cursor()

    # Get all problems the user has NOT attempted
    query = """
    SELECT p.problem_id, p.title, p.difficulty, p.concepts
    FROM problems p
    WHERE p.problem_id NOT IN (SELECT DISTINCT problem_id FROM attempts WHERE user_id = ?)
    """
    cur.execute(query, (user_id,))
    candidate_problems = cur.fetchall()

    scored_problems = []
    for problem in candidate_problems:
        concepts = json.loads(problem["concepts"])
        
        # Score a problem based on the average "skill gap" for its concepts
        # A lower skill score means a higher gap (1 - skill)
        if not concepts:
            continue

        total_gap = 0
        for concept in concepts:
            skill_score = user_skills.get(concept, 0.5) # Default to 0.5 for unseen concepts
            total_gap += (1 - skill_score)
        
        avg_gap = total_gap / len(concepts)
        
        # Add a small bonus for easier problems to start with
        difficulty_bonus = {1: 0.1, 2: 0.05, 3: 0.0}.get(problem["difficulty"], 0)
        
        final_score = avg_gap + difficulty_bonus
        
        scored_problems.append({
            "problem_id": problem["problem_id"],
            "title": problem["title"],
            "reason": f"Targets weak concepts like {concepts[0]}. Skill gap score: {final_score:.2f}",
            "score": final_score
        })

    # Sort problems by the final score in descending order (highest gap first)
    scored_problems.sort(key=lambda x: x["score"], reverse=True)

    return scored_problems[:k]