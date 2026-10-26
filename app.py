"""
Tastio: AI Recipe Recommendation and Nutrition System
Root entry point: Launches the modular backend Flask server.
"""
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(CURRENT_DIR, "backend"))
sys.path.insert(0, os.path.join(CURRENT_DIR, "ai-service"))

from backend.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[Tastio Server] Starting on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
