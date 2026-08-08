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
    try:
        # 1. Fetch real stats directly from LeetCode GraphQL
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
        
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()["data"]["matchedUser"]
        
        profile = data["profile"]
        stats = data["submitStats"]["acSubmissionNum"]
        
        total = next((item["count"] for item in stats if item["difficulty"] == "All"), 0)
        easy = next((item["count"] for item in stats if item["difficulty"] == "Easy"), 0)
        medium = next((item["count"] for item in stats if item["difficulty"] == "Medium"), 0)
        hard = next((item["count"] for item in stats if item["difficulty"] == "Hard"), 0)
        
        # 2. Keep your exact Gemini AI prompt intact
        prompt = f"""
Act as an expert coding mentor. The user '{username}' has solved {total} total problems ({easy} Easy, {medium} Medium, {hard} Hard).
Provide a short 2-sentence performance report and a 3-item daily practice recommendation for C++.
"""
        ai_response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        
        # 3. Return both the stats for the UI and the AI report
        return {
            "ranking": profile.get("ranking", "N/A"),
            "reputation": profile.get("reputation", 0),
            "totalSolved": total,
            "easy": easy,
            "medium": medium,
            "hard": hard,
            "ai_coach_report": ai_response.text
        }
    except Exception as e:
        return {"error": str(e), "ranking": "N/A", "reputation": 0, "totalSolved": 0}

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
@app.get("/recommend-similar/{problem_name}")
def recommend_similar_problems(problem_name: str):
    prompt = f"The user just solved the LeetCode problem '{problem_name}'. Recommend exactly 4 similar problems to help them master this specific pattern. Return ONLY a comma-separated list of problem names without extra text."
    
    ai_response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
    recommendations = [rec.strip() for rec in ai_response.text.split(",")]
        
    return {
        "user_solved": problem_name,
        "ai_recommendations": recommendations
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
@app.get("/compare/{user1}/{user2}")
def compare_with_friend(user1: str, user2: str):
    def get_user_data(username):
        url = f"https://alfa-leetcode-api.vercel.app/{username}/solved"
        try:
            response = requests.get(url, timeout=8)
            return response.json() if response.status_code == 200 else {}
        except:
            return {}

    data1 = get_user_data(user1)
    data2 = get_user_data(user2)

    def get_bar(solved, total_max=100):
        count = min(int((solved / total_max) * 10), 10)
        return "█" * count + "░" * (10 - count)

    return {
        "comparison": {
            "user1": {
                "Arrays": get_bar(data1.get("easySolved", 0)),
                "Graphs": get_bar(data1.get("mediumSolved", 0)),
                "DP": get_bar(data1.get("hardSolved", 0)),
            },
            "user2": {
                "Arrays": get_bar(data2.get("easySolved", 0)),
                "Graphs": get_bar(data2.get("mediumSolved", 0)),
                "DP": get_bar(data2.get("hardSolved", 0)),
            }
        }
    }

# 10. Friends Group Leaderboard (Compares 4 specific friends with solved endpoint)
@app.get("/friends-leaderboard/{user1}/{user2}/{user3}/{user4}")
async def get_friends_leaderboard(user1: str, user2: str, user3: str, user4: str):
    usernames = [user1, user2, user3, user4]
    url = "https://leetcode.com/graphql"
    query = """
    query userPublicProfile($username: String!) {
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
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    friend_data = []

    for name in usernames:
        if not name or name.lower() in ["none", "null", "undefined", ""]:
            continue

        easy, medium, hard, total, xp = 0, 0, 0, 0, 0

        try:
            response = requests.post(url, json={"query": query, "variables": {"username": name}}, headers=headers, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and data["data"]["matchedUser"]:
                    stats = data["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]
                    easy = next((item["count"] for item in stats if item["difficulty"] == "Easy"), 0)
                    medium = next((item["count"] for item in stats if item["difficulty"] == "Medium"), 0)
                    hard = next((item["count"] for item in stats if item["difficulty"] == "Hard"), 0)
                    total = next((item["count"] for item in stats if item["difficulty"] == "All"), 0)
                    xp = (easy * 1) + (medium * 3) + (hard * 5)
        except:
            pass  # Fallback to 0 if request fails

        friend_data.append({
            "username": name,
            "total_solved": total,
            "breakdown": {"easy": easy, "medium": medium, "hard": hard},
            "xp": xp
        })

    sorted_friends = sorted(friend_data, key=lambda x: x["xp"], reverse=True)

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