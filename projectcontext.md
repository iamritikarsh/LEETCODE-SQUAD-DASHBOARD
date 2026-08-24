# LeetCode Squad Dashboard

## 📖 Project Context & Summary
**LeetCode Squad Dashboard** (also known as LeetCode Analyser) is a highly aesthetic, cyberpunk-themed web application designed for developers to track their LeetCode progress, compare statistics with friends on a custom leaderboard, and receive AI-driven insights. 

Moving away from standard, boring dashboard layouts, this project prioritizes a **premium visual experience** featuring a Noir/Cyberpunk anime aesthetic, deep glassmorphism effects, cinematic scroll animations, and interactive elements like a magnetic custom cursor and an animated floating bubble background.

---

## ✨ Key Features
- **Real-Time Data Sync:** Fetches live user statistics directly from LeetCode's official GraphQL API (solving unreliable 3rd-party API issues).
- **Squad Leaderboard:** Compares multiple users based on a custom weighted XP algorithm (`Easy = 10XP, Medium = 30XP, Hard = 70XP`).
- **Activity & Consistency Tracking:** Visualizes daily problem-solving activity over the past year using interactive charts and consistency heatmaps.
- **Rivalry Matrix:** Directly compare your stats head-to-head with any other LeetCode user.
- **AI Mentor (Chatbot):** An integrated, context-aware AI chat assistant that can suggest topics, explain concepts, and provide problem recommendations based on your weak areas.
- **Rating Predictor:** Analyzes contest history and ranking info to predict future contest performance.
- **Premium UI/UX:**
  - **Cinematic Loader:** A staggered column reveal preloader.
  - **Smooth Scrolling:** Buttery smooth scrolling powered by Lenis with exponential easing.
  - **GSAP Animations:** Scroll-triggered element reveals, staggering, and spring animations.
  - **Custom Magnetic Cursor:** An inverted (difference blend) dot with a rotating dashed tech-ring that snaps to interactive elements.
  - **Dynamic Backgrounds:** A multi-layered background featuring grid scanlines and 50 animated, glowing neon bubbles drifting upward.

---

## 🛠️ Technologies Used

### Frontend (Zero-Build Architecture)
- **Core:** Vanilla HTML5, CSS3, JavaScript (No React, no bundlers, all single-file `index.html`).
- **Styling:** Tailwind CSS (via CDN) combined with heavy custom CSS for glassmorphism, glows, and keyframe animations.
- **Typography:** JetBrains Mono (data), Orbitron (display headers), Inter (body).
- **Animations:** GSAP (GreenSock), ScrollTrigger (scroll animations), Lenis (smooth scroll hijacking).
- **Data Visualization:** Chart.js
- **Icons:** Lucide Icons

### Backend
- **Core:** Python 3, FastAPI
- **Server:** Uvicorn (Hot-reloading local development)
- **Data Fetching:** Direct HTTP `POST` requests to `https://leetcode.com/graphql` to securely fetch `userContestRankingInfo`, `submissionCalendar`, and public profile data.
