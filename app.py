import os
import random
import json
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import redis
from math import pow

# -------------------------------------------------------------test
# Configuration via variables d'environnement
# -------------------------------------------------------------
MONGO_HOSTS = os.environ.get("MONGO_HOSTS", "mongo-0.mongo-headless,mongo-1.mongo-headless,mongo-2.mongo-headless")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
MONGO_DB = os.environ.get("MONGO_DB", "popdb")  
REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
CACHE_TTL = int(os.environ.get("CACHE_TTL", 30))  # en secondes

# -------------------------------------------------------------
# Connexion MongoDB (ReplicaSet)
# -------------------------------------------------------------
hosts = ",".join([f"{h}:{MONGO_PORT}" for h in MONGO_HOSTS.split(",")])
MONGO_URI = f"mongodb://{hosts}/{MONGO_DB}?replicaSet=rs0"

mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = mongo_client[MONGO_DB]
characters = db.characters

# -------------------------------------------------------------
# Connexion Redis
# -------------------------------------------------------------
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# -------------------------------------------------------------
# Application Flask
# -------------------------------------------------------------
app = Flask(__name__)

# -------------------------------------------------------------
# Fonctions utilitaires
# -------------------------------------------------------------
def cached_get_characters():
    """Récupère les personnages depuis le cache Redis ou MongoDB."""
    key = "all_characters"
    data = redis_client.get(key)
    if data:
        try:
            return json.loads(data)
        except Exception:
            redis_client.delete(key)

    docs = list(characters.find({}, {"_id": 1, "name": 1, "image": 1, "elo": 1}))
    for d in docs:
        d["_id"] = str(d["_id"])
    redis_client.set(key, json.dumps(docs), ex=CACHE_TTL)
    return docs


def invalidate_cache():
    """Supprime le cache pour forcer un refresh des données."""
    redis_client.delete("all_characters")


def elo_delta(winner_elo, loser_elo, k=32):
    """Calcule la variation Elo après un match."""
    expected_win = 1 / (1 + pow(10, (loser_elo - winner_elo) / 400))
    change = int(round(k * (1 - expected_win)))
    return change

# -------------------------------------------------------------
# Routes Flask
# -------------------------------------------------------------
@app.route("/")
def index():
    chars = cached_get_characters()
    if len(chars) < 2:
        return "Not enough characters in DB. Run the seed script.", 500
    choice = random.sample(chars, 2)
    return render_template("index.html", left=choice[0], right=choice[1], message="Qui gagne ?")


@app.route("/vote", methods=["POST"])
def vote():
    """Gère un vote utilisateur et met à jour les scores Elo."""
    winner_id = request.form.get("winner")
    loser_id = request.form.get("loser")

    if not winner_id or not loser_id:
        return redirect(url_for("index"))

    try:
        winner = characters.find_one({"_id": ObjectId(winner_id)})
        loser = characters.find_one({"_id": ObjectId(loser_id)})
    except Exception:
        return "Invalid ID format", 400

    if not winner or not loser:
        return "Character not found", 404

    w_elo = winner.get("elo", 1000)
    l_elo = loser.get("elo", 1000)
    delta = elo_delta(w_elo, l_elo)

    new_w = w_elo + delta
    new_l = l_elo - delta

    characters.update_one({"_id": ObjectId(winner_id)}, {"$set": {"elo": new_w}})
    characters.update_one({"_id": ObjectId(loser_id)}, {"$set": {"elo": new_l}})

    invalidate_cache()

    return render_template(
        "result.html",
        winner={
            "_id": winner_id,
            "name": winner["name"],
            "image": winner.get("image"),
            "old_elo": w_elo,
            "new_elo": new_w,
        },
        loser={
            "_id": loser_id,
            "name": loser["name"],
            "image": loser.get("image"),
            "old_elo": l_elo,
            "new_elo": new_l,
        },
        delta=delta,
    )


@app.route("/health")
def health():
    """Vérifie la santé des services (Mongo + Redis)."""
    ok = True
    msgs = []
    try:
        mongo_client.admin.command("ping")
    except Exception as e:
        ok = False
        msgs.append(f"mongo: {e}")
    try:
        redis_client.ping()
    except Exception as e:
        ok = False
        msgs.append(f"redis: {e}")
    return {"ok": ok, "msgs": msgs}

# -------------------------------------------------------------
# Entrée principale
# -------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
