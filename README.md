# 🏆 Squad Ladder — LeetCode Competitive Dashboard

Squad Ladder is a live, gamified dashboard for tracking your LeetCode progress against a small group of rivals. It pulls real solve data straight from LeetCode, computes a weighted XP leaderboard, projects future contest ratings, and includes a Gemini-powered AI mentor you can ask for study advice — all wrapped in a premium, animated dark UI.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Frontend](https://img.shields.io/badge/frontend-HTML%20%2B%20Tailwind%20%2B%20Chart.js-blue)
![Backend](https://img.shields.io/badge/backend-FastAPI%20(Python)-009688)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-8E44AD)

---

## ✨ Features

| Module | Description |
|---|---|
| **Squad Leaderboard** | Ranks you and up to 3 rivals using a weighted XP algorithm (`Easy×1 + Medium×3 + Hard×5`), fetched via a single batched LeetCode GraphQL query. |
| **Your Overview** | Live breakdown of solved counts per difficulty. |
| **Daily Activity Trend** | Chart.js line graph of problems solved over the past 7 days. |
| **Profile Analytics** | Ranking, reputation, and total solved count, plus a short AI-generated performance report. |
| **Rating Predictor** | Projected contest rating trajectory at 1, 3, and 6 months, based on current contest rating. |
| **Consistency Index** | Score (0–100%) derived from LeetCode streak data, capped against a 30-day goal. |
| **Rivalry Matrix** | Head-to-head topic comparison (mapped from Easy/Medium/Hard solve counts) between any two users. |
| **Earned Badges** | Pulls real badge data (name + icon) from a user's LeetCode profile. |
| **Problem Recommender** | Gemini finds the closest matching official problem and 4 genuinely similar ones, with a hardcoded fallback list if the AI call fails. |
| **AI Mentor Chat** | Ask questions about weak topics, problem approach, or a study plan and get a Gemini-generated response. |
| **Search History** | View/clear a log of past searches, persisted in SQLite. |

---

## 🧱 Tech Stack

**Frontend**
- Vanilla HTML / JavaScript (single file, no framework, no build step)
- [Tailwind CSS](https://tailwindcss.com/) via CDN
- [Chart.js](https://www.chartjs.org/) for the activity trend graph
- Custom CSS: glassmorphism cards, hex-grid canvas background, gradient blobs, particles, scroll-based reveal animations, ripple/tilt micro-interactions
- State is kept in the browser's `localStorage` (your username + rival handles) — no login required

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) (Python)
- [SQLAlchemy](https://www.sqlalchemy.org/) + SQLite (`leetcode_analyzer.db`) for search history
- [`google-genai`](https://pypi.org/project/google-genai/) client for AI-generated performance reports, problem recommendations, and mentor chat
- Most stats are fetched **directly from LeetCode's own GraphQL endpoint** (`https://leetcode.com/graphql`), spoofing a browser `User-Agent`/`Referer` to get past Cloudflare
- Contest rating prediction uses the third-party [`alfa-leetcode-api`](https://github.com/alfaarghya/alfa-leetcode-api) (`alfa-leetcode-api.vercel.app`) as a fallback data source
- CORS is currently wide open (`allow_origins=["*"]`) for easy local development

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/<your-username>/squad-ladder.git
cd squad-ladder
```

### 2. Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install fastapi uvicorn sqlalchemy requests pydantic google-genai
```

Create a `.env` file (or export directly) with your Gemini API key:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

Run the API locally:
```bash
uvicorn main:app --reload --port 8000
```
The SQLite database (`leetcode_analyzer.db`) and its tables are created automatically on first run.

### 3. Frontend setup
This is a static single-file app — no build step needed.
```bash
cd frontend
npx serve .
# or just open index.html directly in a browser
```

Point the frontend at your backend by updating this line in `index.html`:
```js
const API_URL = "http://localhost:8000"; // or your deployed backend URL
```

### 4. Launch your squad
On first load, enter:
- **Your LeetCode username**
- Up to **3 rival usernames**

Click **Launch Ladder** — this saves your setup to `localStorage` and loads the dashboard.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/solved/{username}` | Raw solved counts (all/easy/medium/hard) via LeetCode GraphQL |
| `GET` | `/analyze-profile/{username}` | Ranking, reputation, solved counts, and an AI-generated 2-sentence performance report + practice tips |
| `GET` | `/predict-rating/{username}` | Current contest rating and 1/3/6-month projections (via `alfa-leetcode-api`) |
| `GET` | `/consistency/{username}` | Consistency score (0–100%) based on current streak |
| `GET` | `/achievements/{username}` | Earned LeetCode badges (name + icon URL) |
| `GET` | `/compare/{user1}/{user2}` | Topic comparison (Arrays / Graphs / DP) between two users |
| `GET` | `/friends-leaderboard/{user1}/{user2}/{user3}/{user4}` | Weighted XP leaderboard for up to 4 users, sorted by rank |
| `GET` | `/recommend/{query_str}` | AI-matched problem name + 4 similar problems (title, difficulty, slug) |
| `POST` | `/chat` | Body: `{ "username": string, "question": string }` → AI mentor response |
| `GET` | `/history` | List all stored search history records |
| `DELETE` | `/history` | Clear all search history |

---

## ⚠️ Known Issues

- **LeetCode GraphQL blocking:** most endpoints call `leetcode.com/graphql` directly from the server. LeetCode's Cloudflare protection can rate-limit or silently block requests from shared cloud-hosting IPs (e.g. Render), which is caught by the `except:` blocks and returns zeroed-out data (`0` solved, `0%` consistency, empty badges) instead of a visible error. If your dashboard suddenly shows all zeros — including for accounts you know are active — this is almost always the cause, not a frontend bug.
- **`/predict-rating` depends on `alfa-leetcode-api.vercel.app`:** if that third-party service is down, this endpoint returns `{"error": "Could not fetch contest data."}`.
- **Possible invalid Gemini model name:** `/chat` currently requests `model='gemini-3.6-flash'`, while other endpoints use `'gemini-2.0-flash'`. If the AI Mentor consistently returns the "currently resting" fallback message, check that the model name is valid for your `google-genai` version/API key.
- **SQLite on ephemeral hosting:** if deployed on a platform with an ephemeral filesystem (like Render's free tier), `leetcode_analyzer.db` — and therefore `/history` — will reset on every redeploy/restart.
- **Open CORS:** `allow_origins=["*"]` is convenient for development but should be locked down to your actual frontend domain before shipping to production.
- **No authentication:** usernames are stored client-side only; anyone using the same browser/device can view or change the configured squad.

---

## 🗺️ Roadmap

- [ ] Surface a clear "data unavailable" state in the UI when LeetCode/GraphQL calls fail, instead of showing `0`
- [ ] Fix/verify the Gemini model name used in `/chat`
- [ ] Move off SQLite to a persistent store for `/history` in production
- [ ] Support more than 3 rivals
- [ ] Restrict CORS to the deployed frontend origin
- [ ] Dark/light theme toggle

---

## 🤝 Contributing

Issues and PRs are welcome. If you're adding a UI feature, please keep it consistent with the existing gold/glass aesthetic and respect `prefers-reduced-motion`. If you're touching the backend, please keep the try/except fallback pattern so a single failed upstream call never crashes the whole endpoint.

