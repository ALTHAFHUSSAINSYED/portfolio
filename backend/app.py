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
        
        if not user_message:
            return jsonify({"reply": "It seems like you didn't send any message. How can I help you?"}), 400

        # Import web scraper and search engine
        from web_scraper import WebScraper
        from search_engine import SearchEngine
        
        # Initialize tools
        scraper = WebScraper()
        search_engine = SearchEngine()
        
        # Check if the message is requesting internet information
        internet_keywords = ["latest", "news", "current", "today", "recent", "update", "trend", "2025", "new"]
        is_internet_query = any(keyword in user_message.lower() for keyword in internet_keywords)
        
        # Get internet content if it seems like a query needing fresh data
        internet_context = ""
        if is_internet_query:
            try:
                # Extract search terms
                search_terms = user_message.replace("?", "").replace(".", "").replace("!", "").split()
                search_query = " ".join([term for term in search_terms if len(term) > 3])
                
                # Get search results
                search_results = search_engine.search(search_query, num_results=3)
                articles = scraper.fetch_articles(limit=2)
                
                if search_results:
                    internet_context += "\nRelevant search results:\n"
                    for result in search_results:
                        internet_context += f"- {result.get('title')}: {result.get('snippet', '')[:100]}...\n"
                
                if articles:
                    internet_context += "\nRecent tech articles:\n"
                    for article in articles:
                        internet_context += f"- {article.get('title')}: {article.get('summary', '')[:100]}...\n"
            except Exception as e:
                print(f"Error fetching internet data: {e}")
                # Continue even if internet fetch fails

        # Query MongoDB for portfolio-related questions and skills
        portfolio_data = db.portfolio.find_one({"type": "general"})
        skills_data = db.skills.find({})
        
        # Build context from portfolio and skills data
        portfolio_context = portfolio_data.get("content", "") if portfolio_data else ""
        skills_context = ", ".join([skill.get("name", "") for skill in skills_data]) if skills_data else ""
        
        context = f"Portfolio information: {portfolio_context}\nSkills: {skills_context}"
        
        if internet_context:
            context += f"\n\nInternet Information (current as of {datetime.now().strftime('%B %d, %Y')}):{internet_context}"

        # Call OpenAI GPT-4 API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are Allu Bot, a witty, helpful, and tech-focused chatbot for a portfolio website. You specialize in discussing technologies, answering questions about the portfolio owner's experience, projects, and skills. You can also provide up-to-date information on tech topics by accessing internet data. For any malicious, harmful, or completely unrelated questions, respond with a humorous deflection. Keep responses concise, professional, yet conversational. If you don't know something specific, be honest and say so."},
                {"role": "system", "content": context},
                {"role": "user", "content": user_message}
            ]
        )

        bot_reply = response["choices"][0]["message"]["content"]
        
        # Log the interaction
        db.chat_logs.insert_one({
            "user_message": user_message,
            "bot_reply": bot_reply,
            "timestamp": datetime.now(),
            "internet_query": is_internet_query
        })
        
        return jsonify({"reply": bot_reply})

    except Exception as e:
        print(f"Error in Allu Bot API: {str(e)}")
        return jsonify({"reply": "I'm having trouble connecting right now. Please try again later."}), 500

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