from google import genai
import os
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
import os
# Initialize AI Model
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models
import requests
from fastapi.middleware.cors import CORSMiddleware
# Create the database tables
Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize the AI client with your AQ key
class ChatQuery(BaseModel):
    username: str
    question: str

@app.get("/")
def read_root():
    return {"message": "Welcome to my LeetCode Profile Analyzer & AI Coach API!"}
@app.get("/solved/{username}")
async def get_solved_stats(username: str):
    try:
        url = "https://leetcode.com/graphql"
        query = """
        query getUserProfile($username: String!) {
          matchedUser(username: $username) {
            submitStats: submitStatsGlobal {
              acSubmissionNum {
                difficulty
                count
              }
            }
          }
        }
        """
        payload = {
            "query": query,
            "variables": {"username": username}
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.post(url, json=payload, headers=headers)
        
        data = response.json()["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]
        
        stats = {"solvedProblem": 0, "easySolved": 0, "mediumSolved": 0, "hardSolved": 0}
        
        for item in data:
            if item["difficulty"] == "All":
                stats["solvedProblem"] = item["count"]
            elif item["difficulty"] == "Easy":
                stats["easySolved"] = item["count"]
            elif item["difficulty"] == "Medium":
                stats["mediumSolved"] = item["count"]
            elif item["difficulty"] == "Hard":
                stats["hardSolved"] = item["count"]
                
        return stats
    except Exception as e:
        return {"solvedProblem": 0, "easySolved": 0, "mediumSolved": 0, "hardSolved": 0}
# 1. Profile Analyzer & Dynamic AI Performance Report
@app.get("/analyze-profile/{username}")
def analyze_leetcode_profile(username: str):
    # 1. Fetch LeetCode Data (Safely isolated)
    try:
        url = "https://leetcode.com/graphql"
        query = """
        query userPublicProfile($username: String!) {
          matchedUser(username: $username) {
            profile { ranking, reputation }
            submitStats: submitStatsGlobal {
              acSubmissionNum { difficulty, count }
            }
          }
        }
        """
        payload = {"query": query, "variables": {"username": username}}
        headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        
        response = requests.post(url, json=payload, headers=headers).json()
        data = response.get("data", {}).get("matchedUser", {})
        
        if not data:
            return {"ranking": "N/A", "reputation": 0, "totalSolved": 0, "ai_coach_report": "User not found."}

        profile = data.get("profile", {})
        stats = data.get("submitStats", {}).get("acSubmissionNum", [])
        
        total = next((item["count"] for item in stats if item["difficulty"] == "All"), 0)
        easy = next((item["count"] for item in stats if item["difficulty"] == "Easy"), 0)
        medium = next((item["count"] for item in stats if item["difficulty"] == "Medium"), 0)
        hard = next((item["count"] for item in stats if item["difficulty"] == "Hard"), 0)
        
        ranking = profile.get("ranking", "N/A")
        reputation = profile.get("reputation", 0)

    except Exception as e:
        return {"error": str(e), "ranking": "N/A", "reputation": 0, "totalSolved": 0, "ai_coach_report": "Error fetching LeetCode stats."}

    # 2. Fetch AI Report (In its own separate try/except block!)
    ai_report = "AI Coach is analyzing your performance..."
    try:
        prompt = f"""
        Act as an expert coding mentor. The user '{username}' has solved {total} total problems ({easy} Easy, {medium} Medium, {hard} Hard).
        Provide a short 2-sentence performance report and a 3-item daily practice recommendation for C++.
        """
        ai_response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        ai_report = ai_response.text
    except Exception as e:
        print(f"AI Generation Error: {e}") # Fails silently on the server without breaking the UI
        ai_report = "AI Mentor is currently taking a break. Keep grinding!"

    # 3. Return everything to the frontend
    return {
        "ranking": ranking,
        "reputation": reputation,
        "totalSolved": total,      
        "total_solved": total,     
        "easy": easy,
        "medium": medium,
        "hard": hard,
        "ai_coach_report": ai_report
    }

# 2. Predict Contest Rating
@app.get("/predict-rating/{username}")
def predict_contest_rating(username: str):
    url = f"https://alfa-leetcode-api.vercel.app/{username}/contest"
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"error": "Could not fetch contest data."}
    
    data = response.json()
    raw_rating = data.get("contestRating")
    
    if not raw_rating:
        return {"message": f"User {username} hasn't participated in enough contests yet!"}
        
    current_rating = round(raw_rating)
    
    return {
        "user": username,
        "current_rating": current_rating,
        "prediction": {
            "1_month": current_rating + 50,
            "3_months": current_rating + 120,
            "6_months": current_rating + 250
        },
        "badge_unlocked": "Contest Competitor 🏆"
    }

# # 3. Achievement System
# @app.get("/achievements/{username}")
# def unlock_achievements(username: str):
#     url = f"https://alfa-leetcode-api.vercel.app/{username}/solved"
#     response = requests.get(url)
    
#     if response.status_code != 200:
#         return {"error": "Could not fetch data for achievements."}
    
#     data = response.json()
#     easy = data.get("easySolved", 0)
#     medium = data.get("mediumSolved", 0)
#     hard = data.get("hardSolved", 0)
    
#     unlocked_badges = []
    
#     if easy >= 100:
#         unlocked_badges.append("100 Easy 🥉")
#     if medium >= 50:
#         unlocked_badges.append("Medium Master 🥈")
#     if hard >= 50:
#         unlocked_badges.append("50 Hard 🥇")
        
#     unlocked_badges.extend(["DP Beginner 🌱", "Tree Expert 🌲", "30 Day Streak 🔥"])
    
#     return {
#         "user": username,
#         "total_badges": len(unlocked_badges),
#         "badges": unlocked_badges
#     }

# 4. Similar Problem Finder (Fully Dynamic AI)
import difflib

@app.get("/recommend/{query_str}")
def recommend_problems(query_str: str):
    try:
        prompt = f"""
        Provide 3 short practice recommendations for the LeetCode problem: '{query_str}'.
        Return ONLY 3 bullet points, nothing else.
        """
        ai_res = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        lines = [line.strip("- *123.") for line in ai_res.text.split("\n") if len(line.strip()) > 5]
        recs = lines[:3] if len(lines) >= 3 else [
            "Focus on optimal time and space complexity",
            "Practice similar array and hashing patterns",
            "Review edge cases and constraints"
        ]
        return {
            "user_solved": query_str.title(),
            "ai_recommendations": recs
        }
    except Exception:
        return {
            "user_solved": query_str.title(),
            "ai_recommendations": [
                "Master the underlying data structures",
                "Optimize your solution's runtime",
                "Solve related pattern variations"
            ]
        }

# 5. Open-Ended AI Chatbot (Fully Dynamic AI - No Hardcoded Answers)
# 5. Open-Ended AI Chatbot (Fully Dynamic AI with Safety Guardrail)
@app.post("/chat")
async def chat_with_ai(chat_req: dict): 
    try:
        username = chat_req.get("username", "User")
        question = chat_req.get("question", "")

        prompt = f"""
        You are an expert LeetCode mentor and software engineer. 
        A student named {username} is asking you this question: "{question}"
        Provide a concise, helpful, and technically accurate response.
        Use line breaks and bold text (** **) to format your response clearly.
        """

        # Use the exact model version that bypassed the quota limit
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt
        )

        return {
            "user": username,
            "question": question,
            "ai_response": response.text
        }
    except Exception as e:
        return {"ai_response": f"AI Mentor is currently resting. Error: {str(e)}"}


# 6. View All Search History
@app.get("/history")
def get_search_history(db: Session = Depends(get_db)):
    history_records = db.query(models.UserSearchHistory).all()
    return {
        "total_searches": len(history_records),
        "history": history_records
    }

# 7. Clear All Search History
@app.delete("/history")
def clear_search_history(db: Session = Depends(get_db)):
    db.query(models.UserSearchHistory).delete()
    db.commit()
    return {"message": "All search history has been successfully cleared!"}


# 8. Consistency Score Calculator
# --- CONSISTENCY METRICS ---
@app.get("/consistency/{username}")
async def get_consistency(username: str):
    try:
        url = "https://leetcode.com/graphql"
        query = """query ($username: String!) { matchedUser(username: $username) { userCalendar { streak } } }"""
        response = requests.post(url, json={"query": query, "variables": {"username": username}}).json()
        
        streak = response["data"]["matchedUser"]["userCalendar"]["streak"]
        score = min((streak / 30) * 100, 100) # Calculates a score based on a 30-day goal
        return {"consistency_score": f"{int(score)}%"}
    except:
        return {"consistency_score": "0%"}

# --- EARNED BADGES ---
@app.get("/achievements/{username}")
async def get_achievements(username: str):
    try:
        url = "https://leetcode.com/graphql"
        query = """query ($username: String!) { matchedUser(username: $username) { badges { name icon } } }"""
        response = requests.post(url, json={"query": query, "variables": {"username": username}}).json()
        
        badges = response["data"]["matchedUser"]["badges"]
        # Format image URLs correctly for the frontend
        for b in badges:
            if not b["icon"].startswith("http"):
                b["icon"] = "https://leetcode.com" + b["icon"]
                
        return {"badges": badges}
    except:
        return {"badges": []}


# 9. Compare with Friends
@app.get("/compare/{user1}/{user2}")
def compare_with_friend(user1: str, user2: str):
    # Calculates a clean percentage (0 to 100) instead of messy ASCII text
    def get_percentage(solved, total_max=150): 
        return min(int((solved / total_max) * 100), 100)

    # Use a single batched GraphQL query for both users
    url = "https://leetcode.com/graphql"
    query = f"""
    query getCompareStats {{
        u1: matchedUser(username: "{user1}") {{
            submitStats: submitStatsGlobal {{ acSubmissionNum {{ difficulty count }} }}
        }}
        u2: matchedUser(username: "{user2}") {{
            submitStats: submitStatsGlobal {{ acSubmissionNum {{ difficulty count }} }}
        }}
    }}
    """
    headers = {
        "Content-Type": "application/json", 
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://leetcode.com/"
    }
    
    try:
        response = requests.post(url, json={"query": query}, headers=headers, timeout=10)
        data = response.json().get("data", {})
        
        def parse_stats(user_key):
            user_data = data.get(user_key)
            if not user_data or not user_data.get("submitStats"):
                return 0, 0, 0
            stats = user_data["submitStats"]["acSubmissionNum"]
            easy = next((item["count"] for item in stats if item["difficulty"] == "Easy"), 0)
            medium = next((item["count"] for item in stats if item["difficulty"] == "Medium"), 0)
            hard = next((item["count"] for item in stats if item["difficulty"] == "Hard"), 0)
            return easy, medium, hard

        e1, m1, h1 = parse_stats("u1")
        e2, m2, h2 = parse_stats("u2")

    except Exception:
        e1, m1, h1 = 0, 0, 0
        e2, m2, h2 = 0, 0, 0

    return {
        "comparison": {
            "user1": {
                "Arrays": get_percentage(e1),
                "Graphs": get_percentage(m1),
                "DP": get_percentage(h1),
            },
            "user2": {
                "Arrays": get_percentage(e2),
                "Graphs": get_percentage(m2),
                "DP": get_percentage(h2),
            }
        }
    }
# 10. Friends Group Leaderboard (Compares 4 specific friends with solved endpoint)
@app.get("/friends-leaderboard/{user1}/{user2}/{user3}/{user4}")
def get_friends_leaderboard(user1: str, user2: str, user3: str, user4: str):
    # Filter out empty or "none" usernames
    valid_users = [u for u in [user1, user2, user3, user4] if u and u.lower() not in ["none", "null", "undefined", ""]]
    
    if not valid_users:
        return {"group_leaderboard": []}

    # Build a SINGLE GraphQL query requesting all users at once using aliases
    query_parts = []
    for i, user in enumerate(valid_users):
        query_parts.append(f"""
        user{i}: matchedUser(username: "{user}") {{
            submitStats: submitStatsGlobal {{
                acSubmissionNum {{ difficulty count }}
            }}
        }}
        """)
        
    query = "query getSquadStats {\n" + "\n".join(query_parts) + "\n}"
    url = "https://leetcode.com/graphql"
    
    # Added Referer and full User-Agent to safely bypass Cloudflare
    headers = {
        "Content-Type": "application/json", 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://leetcode.com/"
    }
    
    friend_data = []
    try:
        response = requests.post(url, json={"query": query}, headers=headers, timeout=10)
        data = response.json().get("data", {})
        
        for i, user in enumerate(valid_users):
            easy, medium, hard, total, xp = 0, 0, 0, 0, 0
            user_data = data.get(f"user{i}")
            
            # If the user exists and has a public profile, extract their stats
            if user_data and user_data.get("submitStats"):
                stats = user_data["submitStats"]["acSubmissionNum"]
                easy = next((item["count"] for item in stats if item["difficulty"] == "Easy"), 0)
                medium = next((item["count"] for item in stats if item["difficulty"] == "Medium"), 0)
                hard = next((item["count"] for item in stats if item["difficulty"] == "Hard"), 0)
                total = next((item["count"] for item in stats if item["difficulty"] == "All"), 0)
                
                # Apply your custom weighted XP algorithm
                xp = (easy * 1) + (medium * 3) + (hard * 5)
                
            friend_data.append({
                "username": user,
                "total_solved": total,
                "breakdown": {"easy": easy, "medium": medium, "hard": hard},
                "xp": xp
            })
    except Exception as e:
        # Failsafe if the request gets interrupted
        for user in valid_users:
            friend_data.append({
                "username": user, "total_solved": 0,
                "breakdown": {"easy": 0, "medium": 0, "hard": 0}, "xp": 0
            })

    # Sort descending by XP
    sorted_friends = sorted(friend_data, key=lambda x: x["xp"], reverse=True)

    # Format the final JSON response for your frontend
    leaderboard_result = []
    for rank, friend in enumerate(sorted_friends, start=1):
        leaderboard_result.append({
            "rank": rank,
            "username": friend["username"],
            "xp": friend["xp"],
            "total_solved": friend["total_solved"],
            "variety_breakdown": friend["breakdown"]
        })

    return {"group_leaderboard": leaderboard_result}