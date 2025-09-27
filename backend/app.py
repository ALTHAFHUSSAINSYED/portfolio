from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os
import openai
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB setup
mongo_url = os.getenv("MONGO_URL")
db_name = os.getenv("DB_NAME")
client = MongoClient(mongo_url)
db = client[db_name]

# OpenAI API setup
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/api/ask-all-u-bot", methods=["POST"])
def ask_allu_bot():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        # Query MongoDB for portfolio-related questions
        portfolio_data = db.portfolio.find_one({"type": "general"})
        portfolio_context = portfolio_data.get("content", "") if portfolio_data else ""

        # Call OpenAI GPT-4 API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Allu Bot, a witty, helpful, and tech-focused chatbot. You only answer questions related to technologies, portfolio details, and specified topics. For malicious or unrelated questions, respond humorously and decently."},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": portfolio_context}
            ]
        )

        bot_reply = response["choices"][0]["message"]["content"]
        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/post-blog", methods=["POST"])
def post_blog():
    try:
        # Authenticate request
        auth_token = request.headers.get("Authorization")
        if auth_token != os.getenv("BLOG_POST_AUTH_TOKEN"):
            return jsonify({"error": "Unauthorized"}), 403

        data = request.get_json()
        title = data.get("title")
        content = data.get("content")
        category = data.get("category", "General")

        if not title or not content:
            return jsonify({"error": "Title and content are required"}), 400

        # Insert blog into MongoDB
        db.blogs.insert_one({
            "title": title,
            "content": content,
            "category": category,
            "created_at": datetime.utcnow()
        })

        return jsonify({"message": "Blog posted successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)