import os
import traceback
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class PromptRequest(BaseModel):
    prompt: str
    character_name: str = "Free"
    setting: str = "Forest"
    tone: str = "Dramatic"
    style: str = "Realistic"

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the homepage for comic story creation."""
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    style: str = Form(...)
):
    """
    Handle user form submission, orchestrate the AI pipeline:
    1. Gemini Flash -> 5-panel outline
    2. Gemini Pro -> Full story narration & dialogues
    3. Stable Diffusion / Generator -> Panel illustrations
    4. Layout Builder -> Combine into panel cards
    5. PDF Exporter -> Compile into downloadable PDF
    """
    try:
        # Combine user input into a single full prompt
        full_prompt = (
            f"{prompt}\n"
            f"The main character is {character_name}. "
            f"The setting is a {setting}. "
            f"The tone is {tone}. The art style is {style}."
        )

        # Step 1: Generate panel outline
        outline = generate_outline(full_prompt)

        if not isinstance(outline, list) or not all("image_prompt" in panel for panel in outline if isinstance(panel, dict)):
            raise ValueError("Invalid outline structure from Gemini response.")

        # Step 2: Generate story narration & dialogue
        full_story = generate_story(outline)

        # Step 3: Generate panel images
        images = [generate_image(panel["image_prompt"]) for panel in outline]

        # Step 4: Build Comic Layout
        layout = build_comic_layout(images, full_story, outline)

        # Step 5: Export to PDF
        pdf_path = save_pdf(layout)
        web_pdf_path = "/" + pdf_path.replace("\\", "/").lstrip("/")

        return templates.TemplateResponse("comic_preview.html", {
            "request": request,
            "layout": layout,
            "pdf_path": web_pdf_path,
            "user_prompt": prompt,
            "character_name": character_name,
            "setting": setting,
            "tone": tone,
            "style": style
        })

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-comic/json")
async def generate_comic_json(req: PromptRequest):
    """
    API endpoint to generate comics programmatically via JSON payload.
    """
    try:
        full_prompt = (
            f"{req.prompt}\n"
            f"The main character is {req.character_name}. "
            f"The setting is a {req.setting}. "
            f"The tone is {req.tone}. The art style is {req.style}."
        )

        outline = generate_outline(full_prompt)
        if not isinstance(outline, list) or not all("image_prompt" in panel for panel in outline if isinstance(panel, dict)):
            raise ValueError("Invalid outline structure from Gemini response.")

        full_story = generate_story(outline)
        images = [generate_image(panel["image_prompt"]) for panel in outline]
        layout = build_comic_layout(images, full_story, outline)
        pdf_path = save_pdf(layout)
        web_pdf_path = "/" + pdf_path.replace("\\", "/").lstrip("/")

        return JSONResponse({
            "status": "success",
            "outline": outline,
            "full_story": full_story,
            "layout": layout,
            "pdf_path": web_pdf_path
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_path: str = ""):
    """Render the comic export confirmation and download success page."""
    return templates.TemplateResponse("export_success.html", {
        "request": request,
        "pdf_path": pdf_path
    })

@router.get("/test-image")
async def test_image(prompt: str = "A futuristic city at sunset, sci-fi, cinematic, artstation"):
    """Test image generation endpoint for developers."""
    try:
        image_path = generate_image(prompt)
        return {"message": "Image generated successfully", "path": "/" + image_path.replace("\\", "/").lstrip("/")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
