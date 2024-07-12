import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# Initialize FastAPI app
app = FastAPI()

# Set up CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the environment variables
os.environ["GEMINI_API_KEY"] = "AIzaSyAnWuK1Rpa-iOU1A3PPjHC8dSI4wRt0TWA"
os.environ["UNSPLASH_ACCESS_KEY"] = "wYRPjP-5nxnAOJWDtKE6ShI1fcE909gX5dXMXjD6mF4"

# Configure the API key for Google Generative AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Define the generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the generative model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Function to search for images on Unsplash
def search_unsplash_images(query):
    url = f"https://api.unsplash.com/search/photos"
    headers = {
        "Accept-Version": "v1",
        "Authorization": f"Client-ID {os.environ['UNSPLASH_ACCESS_KEY']}"
    }
    params = {
        "query": query,
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if 'results' in data:
            images = data['results']
            image_urls = [img['urls']['regular'] for img in images]
            return image_urls
        else:
            raise HTTPException(status_code=404, detail="No images found for the query")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching images from Unsplash: {e}")

# Integrate images into the article
def integrate_images(article_text, image_urls):
    paragraphs = article_text.split('\n\n')
    enhanced_article = ""

    for i, paragraph in enumerate(paragraphs):
        enhanced_article += paragraph + '\n\n'
        if i < len(image_urls):
            enhanced_article += f"{image_urls[i]}\n\n"

    return enhanced_article

# Define the request body model
class ArticleRequest(BaseModel):
    topic_title: str

@app.post("/generate_article/")
async def generate_article(request: ArticleRequest):
    # Start a chat session
    chat_session = model.start_chat(history=[])

    # Generate the article text
    response = chat_session.send_message(f"Write an article on the topic: {request.topic_title}")
    article_text = response.text

    # Extract keywords and search for images
    keywords = [request.topic_title]
    image_urls = []
    for keyword in keywords:
        image_urls.extend(search_unsplash_images(keyword))

    enhanced_article = integrate_images(article_text, image_urls)
    return {"article": enhanced_article}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
