import os
import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import anthropic

# Load environment variables
load_dotenv()

# MongoDB setup
mongo_url = os.getenv("MONGO_URL")
db_name = os.getenv("DB_NAME")
client = MongoClient(mongo_url)
db = client[db_name]

# Anthropic API setup
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# Function to fetch trending topics
def fetch_trending_topics():
    response = requests.get("https://dev.to/t/trending")
    soup = BeautifulSoup(response.text, "html.parser")
    topics = [a.text for a in soup.find_all("h2")[:5]]
    return topics

# Function to generate blog content
def generate_blog_content(topic):
    client = anthropic.Client(api_key=anthropic_api_key)
    prompt = f"Write a detailed blog post about {topic}. Make it engaging and informative."
    response = client.completions.create(
        model="claude-3-opus",
        prompt=prompt,
        max_tokens=1000
    )
    return response["completion"]

# Main function to create and store a blog
def main():
    topics = fetch_trending_topics()
    if not topics:
        print("No trending topics found.")
        return

    topic = topics[0]  # Select the first trending topic
    blog_content = generate_blog_content(topic)

    # Store the blog in MongoDB
    db.blogs.insert_one({
        "title": topic,
        "content": blog_content,
        "created_at": datetime.utcnow()
    })

    print("Blog post created successfully.")

if __name__ == "__main__":
    main()