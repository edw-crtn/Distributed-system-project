import os
from pymongo import MongoClient
from bson.objectid import ObjectId

MONGO_HOSTS = os.environ.get("MONGO_HOSTS", "mongo-0.mongo-headless,mongo-1.mongo-headless,mongo-2.mongo-headless")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
MONGO_DB = os.environ.get("MONGO_DB", "popdb")

hosts = ",".join([f"{h}:{MONGO_PORT}" for h in MONGO_HOSTS.split(",")])
MONGO_URI = f"mongodb://{hosts}/?replicaSet=rs0"

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[MONGO_DB]
chars = db.characters

# Example characters — remplace par les images que tu veux (URL publiques)
sample = [
    {"name": "Superman", "image": "https://static.wikia.nocookie.net/heroes-fr/images/b/ba/Action_Comics_1000_Variant_Cover.jpg/revision/latest?cb=20200808094812&path-prefix=fr", "elo": 1400},
    {"name": "Batman", "image": "https://preview.redd.it/what-do-you-prefer-in-comics-batman-portrayed-in-a-more-v0-cfd0vq1jhcie1.jpg?width=449&format=pjpg&auto=webp&s=610d008ff05e4dbb7486bb8fe15dc7f38615cd21", "elo": 1300},
    {"name": "Goku", "image": "https://i.pinimg.com/564x/08/73/81/08738188195601e970f48586ca8bce59.jpg", "elo": 1500},
    {"name": "Darth Vader", "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRBBrzYzaTSExPyUeU9vYaY0HAaE2CGe43iZg&s", "elo": 1350},
    {"name": "Link", "image": "https://cdn.kinocheck.com/i/mtldmq5qik.jpg", "elo": 1250},
    {"name": "Mario", "image": "https://img.lemde.fr/2023/10/16/0/269/1347/898/1440/960/60/0/28bdd77_1697474098060-super-mario-bros-wonder-0.png", "elo": 1200}
]

if __name__ == "__main__":
    if chars.count_documents({}) == 0:
        chars.insert_many(sample)
        print("Seeded DB with sample characters.")
    else:
        print("DB already seeded.")
