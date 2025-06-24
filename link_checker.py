# link_checker.py

from pymongo import MongoClient
import os

# Get the MongoDB URI from environment
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)

# Connect to the correct DB and collection
db = client["qrscanner"]
collection = db["scam_reports"]  # make sure your collection name matches

# Function to check if link already exists in database
def check_against_db(link):
    result = collection.find_one({"link": link})
    if result:
        return "suspicious", "Found in local scam database."
    return None, None

# Main function to use in app.py
def check_link(link):
    verdict, reason = check_against_db(link)
    if verdict:
        return verdict, reason
    return "unknown", "Not found in any known database."
