import sys
import json
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# -----------------------------
# 1. Load JSON dataset
# -----------------------------
with open("data.json", "r", encoding="utf-8") as f:
    data_list = json.load(f)

# Convert JSON list to DataFrame
data = pd.DataFrame(data_list)
print("[train_data] Loaded dataset:", data.shape)

# -----------------------------
# 2. Prepare text for embeddings
# -----------------------------
data['ingredients'] = data['ingredients'].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
data['steps'] = data['steps'].apply(lambda x: " ".join(x) if isinstance(x, list) else str(x))
data['recipe_name'] = data['recipe_name'].fillna('').astype(str)

# -----------------------------
# 3. Generate BERT embeddings
# -----------------------------
print("[train_data] Generating BERT embeddings...")
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

recipe_texts = (data['recipe_name'] + " " + data['ingredients'] + " " + data['steps']).tolist()
recipe_embeddings = bert_model.encode(recipe_texts, show_progress_bar=False, convert_to_numpy=True)

np.save("bert_embeddings.npy", recipe_embeddings)
print("[train_data] Saved BERT embeddings to bert_embeddings.npy")

# -----------------------------
# 4. Optional: Prepare dummy user interactions
# -----------------------------
if 'user_id' not in data.columns:
    n_users = 10
    data['user_id'] = [f"user_{i % n_users}" for i in range(len(data))]
    data['rating'] = np.random.randint(1, 6, size=len(data))

# -----------------------------
# 5. Save updated dataset
# -----------------------------
data.to_csv("data_with_embeddings.csv", index=False)
print("[train_data] Saved dataset with user info as data_with_embeddings.csv")
