# 📱 Mobile App Testing & Run Guide

This guide explains how to run and test the **Tastio Mobile Application** on your physical phone (Android/iOS) or in a web simulator using **Expo**.

---

## 🚀 Quick Start (2 Steps)

### Step 1: Start the Backend Server
First, make sure the backend REST API is running:
```bash
# Navigate to the backend directory
cd backend

# Install dependencies if you haven't already
pip install -r requirements.txt

# Start the Flask API server
python app.py
```
> The backend will start on **`http://localhost:5000`** and expose REST APIs at `/api/...`.

---

### Step 2: Launch the Mobile App with Expo
Open a new terminal window :
```bash
# Navigate to the mobile app directory
cd mobile-app

# Start the Expo development server (use npx.cmd on Windows if powershell scripts are restricted)
npx.cmd expo start
# Or: npm start
```

---

## 📲 Testing on Your Physical Phone (Recommended)

1. Download the free **Expo Go** app on your phone:
   - **Android**: [Google Play Store - Expo Go](https://play.google.com/store/apps/details?id=host.exp.exponent)
   - **iPhone (iOS)**: [Apple App Store - Expo Go](https://apps.apple.com/app/expo-go/id982107779)
2. Connect your phone to the **same Wi-Fi network** as your computer.
3. The API host in `mobile-app/src/services/api.js` is automatically detected from Expo or defaults to your Wi-Fi IP:
   - **`http://10.231.101.150:5000/api`**
4. In **Expo Go** on Android:
   - Tap **"Enter URL manually"** and enter:
     ```text
     exp://10.231.101.150:8081
     ```
   - Or scan the terminal QR code.
5. The **Tastio** mobile app will build and open directly on your phone! 🎉

---

## 💻 Testing in Web Browser Simulator
You can preview the mobile app interface directly in your browser:
```bash
cd mobile-app
npx.cmd expo start --web
```
Or open: **[http://localhost:8081](http://localhost:8081)**

---

## 🌐 Web Application Access
- **Local PC**: [http://localhost:5000](http://localhost:5000)
- **Phone / Wi-Fi Network**: [http://172.25.62.215:5000](http://172.25.62.215:5000)

---

## 🌟 Mobile Features Available in the App:
- 🏠 **Home Screen**: Daily recommendation cards, category filter pills (All, Veg, Non-Veg, Keto, Protein), and full catalog.
- 🔍 **AI Semantic Search**: Type ingredients in your pantry to get instant BERT vector similarity recommendations.
- 📋 **Recipe Details**: View ingredients, preparation steps, and calorie breakdown.
- 🍽️ **Mark as Cooked/Eaten**: Log meals to your diet history with 1 tap.
- ⭐ **Star Rating Reviews**: Submit 1–5 star ratings and comments.
- 👤 **Nutrition & Health Profile**: Automated Mifflin-St Jeor BMR, TDEE, and daily target calorie projections.
