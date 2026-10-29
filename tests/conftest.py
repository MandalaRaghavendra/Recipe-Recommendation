import os
import sys
import pytest
import json

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)

sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "ai-service"))
sys.path.insert(0, PROJECT_ROOT)

os.environ["FLASK_ENV"] = "development"
os.environ["SECRET_KEY"] = "test-secret-key-for-automated-suite-300"

import app as root_app
from backend.app import app as flask_app
from embedding_engine import ai_engine
import database as db

@pytest.fixture(scope="session")
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        with c.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "demo_tester"
        yield c

@pytest.fixture(scope="session")
def engine():
    return ai_engine

@pytest.fixture(scope="session")
def all_recipes():
    return ai_engine.get_all_recipes()
