# ros-chatbot-app/main.py
import os
import glob
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Mount static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates for Jinja2 (for HTML pages)
templates = Jinja2Templates(directory="templates")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Path to the Docusaurus book's docs directory
# Assuming ros-chatbot-app is a sibling to physical-AI-humanoid-robotics-book
BOOK_DOCS_PATH = Path("../physical-AI-humanoid-robotics-book/docs").resolve()

def load_book_content() -> str:
    """Loads content from all markdown files in the Docusaurus book's docs directory."""
    full_content = []
    # Use glob to find all markdown files recursively
    markdown_files = glob.glob(str(BOOK_DOCS_PATH / "**/*.md"), recursive=True)
    markdown_files.extend(glob.glob(str(BOOK_DOCS_PATH / "**/*.mdx"), recursive=True))

    for file_path in markdown_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Simple cleaning: remove frontmatter (lines between ---)
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) > 2:
                        content = parts[2]
                full_content.append(content)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    return "\n\n".join(full_content)

# Load book content once when the app starts
BOOK_CONTENT = load_book_content()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_with_llm(request: Request):
    data = await request.json()
    user_message = data.get("message")

    if not user_message:
        return {"response": "Please provide a message."}

    if not BOOK_CONTENT:
        return {"response": "Book content not loaded. Cannot answer questions."}

    try:
        # Construct the prompt with book content
        prompt = f"""You are an AI assistant specialized in Physical AI & Humanoid Robotics.
You have access to the following textbook content:

---\n{BOOK_CONTENT}
---

Based on the textbook content provided above, answer the following question.
If the answer is not available in the provided text, state that you don't have enough information from the textbook to answer.
Do not make up information.

Question: {user_message}

Answer:"""

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            model="gpt-3.5-turbo", # You can change this to "gpt-4" or other models
            max_tokens=500,
            temperature=0.7,
        )
        llm_response = chat_completion.choices[0].message.content
        return {"response": llm_response}

    except Exception as e:
        print(f"Error during OpenAI API call: {e}")
        return {"response": f"An error occurred while processing your request: {e}"}

