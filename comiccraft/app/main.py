import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

# Ensure required static directories exist on startup
os.makedirs("static/panels", exist_ok=True)
os.makedirs("static/exports", exist_ok=True)
os.makedirs("static/fonts", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Web-based application using Gemini 1.5 Flash, Gemini 1.5 Pro, and Stable Diffusion to generate personalized comic books.",
    version="1.0.0"
)

# Enable CORS for flexible API consumption
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder for images, CSS, JS, fonts, and exported PDFs
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
