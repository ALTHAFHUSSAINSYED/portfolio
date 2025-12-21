import pymongo
import os

# Get MongoDB URL from .env or hardcode here
MONGO_URL = "mongodb+srv://allualthaf42_db_user:9912640155Aa@cluster1.dllhnmp.mongodb.net/portfolioDB?retryWrites=true&w=majority&appName=Cluster1"
DB_NAME = "portfolioDB"
COLLECTION = "projects"

def main():
    client = pymongo.MongoClient(MONGO_URL)
    db = client[DB_NAME]
    projects = list(db[COLLECTION].find())
    print(f"Total projects: {len(projects)}\n")
    for i, project in enumerate(projects, 1):
        print(f"Project {i}:")
        for k, v in project.items():
            print(f"  {k}: {v}")
        print("-"*40)

if __name__ == "__main__":
    main()
