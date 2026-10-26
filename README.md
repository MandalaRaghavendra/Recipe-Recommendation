# 🍲 Tastio: AI Recipe Recommendation & Nutrition Monorepo

A modern, full-stack **Recipe Recommendation and Nutrition Tracking** system with BERT semantic vector embeddings, Mifflin-St Jeor metabolic calculation engine, and cross-platform web and mobile interfaces.

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
