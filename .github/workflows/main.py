import os
import requests
from google import genai
from google.genai import types
from pymongo import MongoClient
from datetime import datetime

# --- 1. CONFIGURATION & CLIENTS ---
NEWSDATA_KEY = os.getenv("NEWSDATA_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

# Initialize AI Client
ai_client = genai.Client(api_key=GEMINI_KEY)

# Initialize Database Client
db_client = MongoClient(MONGO_URI)
db = db_client['news_aggregator']
collection = db['articles']

# --- 2. THE AI BRAIN (Categorization) ---
def classify_industry(title, snippet):
    prompt = f"Title: {title}\nSnippet: {snippet}"
    try:
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="Categorize into EXACTLY one: [Tech, Finance, Healthcare, Energy, Sports, Politics]. Respond with ONLY the word.",
                temperature=0.1
            )
        )
        return response.text.strip()
    except Exception as e:
        print(f"AI Error: {e}")
        return "General"

# --- 3. THE CAPTURE & STORE LOGIC ---
def run_pipeline():
    url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&language=en"
    res = requests.get(url)
    
    if res.status_code != 200:
        print(f"Failed to fetch news. Status: {res.status_code}")
        return

    articles = res.json().get("results", [])
    
    for item in articles:
        # Check for duplicates using the link
        if collection.find_one({"link": item['link']}):
            continue 

        # Segregate using AI
        industry = classify_industry(item['title'], item.get('description', ''))
        
        # Prepare document
        doc = {
            "title": item['title'],
            "link": item['link'],
            "description": item.get('description', ''),
            "industry": industry,
            "source": item.get('source_id', 'Unknown'),
            "captured_at": datetime.utcnow()
        }
        
        # Save to MongoDB
        collection.insert_one(doc)
        print(f"Stored: [{industry}] {item['title'][:50]}...")

if __name__ == "__main__":
    run_pipeline()
