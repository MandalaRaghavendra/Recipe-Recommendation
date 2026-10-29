# 🍲 Tastio: AI Recipe Recommendation & Nutrition Monorepo

[![Tastio 300 Automated Test Suite](https://github.com/MandalaRaghavendra/Recipe-Recommendation/actions/workflows/test-suite-300.yml/badge.svg)](https://github.com/MandalaRaghavendra/Recipe-Recommendation/actions/workflows/test-suite-300.yml)
![Tests](https://img.shields.io/badge/Tests-300%20Passed-brightgreen)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue)
![Backend](https://img.shields.io/badge/Backend-Render%20Live%2024%2F7-emerald)

A modern, full-stack **Recipe Recommendation and Nutrition Tracking** system with BERT semantic vector embeddings, Mifflin-St Jeor metabolic calculation engine, and cross-platform web and mobile interfaces.

---

## 🧪 Comprehensive Automated Test Suite (300 Tests)

Tastio features an enterprise-grade automated test suite containing **exactly 300 tests** executed on every commit and Pull Request via **GitHub Actions CI**:

| Module | Test File | Test Count | Description |
|---|---|---|---|
| 🥗 **Recipe Database** | 	ests/test_recipe_database.py | **50 Tests** | Schema integrity, regional cuisines (Andhra, Telangana), nutritional bounds, meal types |
| 🧠 **AI Vector Recommendations** | 	ests/test_ai_recommendation.py | **60 Tests** | 384-d BERT embeddings, 40-ingredient search queries, multi-facet dietary filters |
| 📅 **7-Day AI Meal Planner** | 	ests/test_meal_planner.py | **50 Tests** | 7-day schedule, all 28 meal slots, macro balancing, slot swaps & alternative suggestions |
| 🛒 **Smart Grocery List** | 	ests/test_smart_grocery.py | **40 Tests** | 7-category heuristic classifier, name normalizer, plan compiler, item toggle & clear |
| 🏋️ **Nutrition & AI Coach** | 	ests/test_nutrition_coach.py | **30 Tests** | Mifflin-St Jeor BMR (M/F), BMI, TDEE activity tiers, macro distributions, AI responses |
| 👁️ **Food Vision Classifier** | 	ests/test_food_vision.py | **25 Tests** | Visual signatures, interactive culinary grounding, recipe matching, verified macros |
| 🌐 **REST API Endpoints** | 	ests/test_api_endpoints.py | **45 Tests** | Health, recipes, recommendations, pantry-match, meal-planner, grocery, coach, CORS |
| **TOTAL** | | **300 Tests** | **100% Deterministic & Passing in < 6 seconds** |

---

## 📁 Monorepo Architecture

```text
📁 Recipe-Recommendation/
├── 📁 ai-service/             # 🧠 Machine Learning & BERT Embeddings Engine
│   ├── bert_embeddings.npy    # Precomputed dense 384-dimensional vector embeddings
│   ├── embedding_engine.py    # Vector similarity search & recipe lookup
│   ├── train_data.py          # Script to generate / re-train embeddings
│   └── requirements.txt       # AI/ML dependencies
│
├── 📁 backend/                # ⚙️ Central Flask REST API & Business Logic
│   ├── app.py                 # REST API endpoints (/api/...) & web routing
│   ├── database.py            # Local SQLite database manager (100% Keyless & Offline)
│   ├── nutrition_engine.py    # BMR, TDEE, BMI, and Caloric Goal calculations
│   └── requirements.txt
│
├── 📁 mobile-app/              # 📱 Cross-Platform React Native (Expo) App
│   ├── App.js                 # Bottom Tab Navigation & Root View
│   ├── src/screens/           # Home, Search, RecipeDetail, History, Profile
│   ├── src/components/        # RecipeCard, StarRating, NutritionCard
│   ├── src/services/api.js    # API service client
│   ├── package.json
│   └── app.json
│
├── 📁 web-app/                 # 💻 Responsive Web Application
│   ├── templates/             # index.html, profile.html, main.html
│   └── static/                # CSS, JS, icons, manifest.json
│
├── 📄 MOBILE_APP_TESTING_GUIDE.md  # Step-by-step mobile testing instructions
├── 📄 .env.example            # Environment variables template
└── 🖼️ icon.png, splash-icon.png, adaptive-icon.png, favicon.png
```

---

## 🚀 How to Run the Services

### 1. Run the Backend & AI Service
```bash
cd backend
pip install -r requirements.txt
python app.py
```
- **Web App**: Open `http://localhost:5000`
- **REST APIs**: Available at `http://localhost:5000/api/...`

### 2. Run the Mobile App
```bash
cd mobile-app
npx expo start
```
- Test on phone via the **Expo Go** app by scanning the terminal QR code.
- Or run in web browser: `npx expo start --web`.

---

## 🛠️ Technology Stack
- **AI & NLP**: Python, Sentence-BERT (`all-MiniLM-L6-v2`), Scikit-learn, Pandas, NumPy
- **Backend API**: Python, Flask, Flask-CORS, Requests Session Pooling
- **Database**: Local SQLite (100% Keyless, Self-Contained & Offline)
- **Mobile Frontend**: React Native, Expo, JavaScript
- **Web Frontend**: HTML5, Jinja2, Bootstrap 5.3.3, Vanilla CSS3, Font Awesome 6.4
