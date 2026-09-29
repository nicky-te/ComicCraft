import os
import re
import hashlib
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()

# Global diffusers pipeline cache
_pipe = None

def sanitize_filename(prompt: str) -> str:
    """Sanitizes a prompt into a filesystem-safe unique filename."""
    clean = re.sub(r'[^a-zA-Z0-9_-]', '_', prompt[:30]).strip('_')
    if not clean:
        clean = "comic_panel"
    hash_suffix = hashlib.md5(prompt.encode('utf-8')).hexdigest()[:8]
    return f"{clean}_{hash_suffix}.png"

def _get_diffusers_pipeline():
    """Lazy loader for Hugging Face Diffusers pipeline."""
    global _pipe
    if _pipe is not None:
        return _pipe

    try:
        import torch
        from diffusers import StableDiffusionPipeline

        model_id = os.getenv("SD_MODEL_ID", "runwayml/stable-diffusion-v1-5")
        
        # Determine device
        if torch.cuda.is_available():
            device = "cuda"
            dtype = torch.float16
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            device = "mps"
            dtype = torch.float32
        else:
            device = "cpu"
            dtype = torch.float32

        print(f"Loading Stable Diffusion pipeline ({model_id}) on {device}...")
        pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype)
        pipe = pipe.to(device)
        _pipe = pipe
        return _pipe
    except Exception as e:
        print(f"Diffusers pipeline not loaded: {e}. Falling back to API or generator.")
        return None

def _generate_via_hf_api(prompt: str, hf_token: str) -> Image.Image:
    """Generates image using Hugging Face Inference API."""
    api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {"inputs": prompt}
    response = requests.post(api_url, headers=headers, json=payload, timeout=60)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        raise RuntimeError(f"HF API returned status {response.status_code}: {response.text}")

def _generate_styled_comic_panel(prompt: str) -> Image.Image:
    """
    Generates a stylized comic art panel image using Pillow.
    Ensures seamless local execution without requiring massive GPU downloads.
    """
    width, height = 768, 512
    # Create image with artistic comic-style gradient background
    img = Image.new("RGB", (width, height), color=(20, 24, 38))
    draw = ImageDraw.Draw(img)

    # Color palette based on prompt content
    p_lower = prompt.lower()
    if "forest" in p_lower or "woods" in p_lower:
        top_color = (15, 45, 25)
        bottom_color = (40, 110, 60)
        accent_color = (255, 140, 0)
    elif "space" in p_lower or "cyber" in p_lower:
        top_color = (10, 10, 35)
        bottom_color = (30, 15, 60)
        accent_color = (0, 220, 255)
    elif "sunset" in p_lower or "fire" in p_lower:
        top_color = (45, 15, 30)
        bottom_color = (180, 70, 30)
        accent_color = (255, 215, 0)
    else:
        top_color = (25, 35, 60)
        bottom_color = (60, 90, 140)
        accent_color = (255, 180, 50)

    # Draw vertical gradient
    for y in range(height):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * (y / height))
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * (y / height))
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Comic border effect
    draw.rectangle([8, 8, width - 8, height - 8], outline=(255, 255, 255), width=3)
    draw.rectangle([14, 14, width - 14, height - 14], outline=(0, 0, 0), width=2)

    # Draw scenic art elements
    # Sun / Moon orb
    draw.ellipse([width - 180, 40, width - 80, 140], fill=accent_color, outline=(255, 255, 255), width=2)

    # Mountain/Hill silhouettes
    points = [
        (0, height - 120),
        (120, height - 240),
        (260, height - 180),
        (420, height - 310),
        (600, height - 200),
        (width, height - 260),
        (width, height),
        (0, height)
    ]
    draw.polygon(points, fill=(10, 15, 25))

    # Foreground ground
    draw.rectangle([0, height - 90, width, height], fill=(5, 10, 15))

    # Comic Halftone/Action Dots accent
    for i in range(30, 250, 25):
        draw.ellipse([i, 35, i + 8, 43], fill=(255, 255, 255, 120))

    # Comic Caption Header Banner
    draw.rectangle([30, 30, width - 220, 80], fill=(255, 255, 255), outline=(0, 0, 0), width=2)
    
    # Try to load a font or default
    try:
        font_large = ImageFont.load_default()
    except Exception:
        font_large = None

    title_text = "COMIC SCENE ILLUSTRATION"
    draw.text((45, 48), title_text, fill=(20, 20, 20), font=font_large)

    # Render Prompt snippet at bottom overlay
    draw.rectangle([20, height - 75, width - 20, height - 20], fill=(0, 0, 0, 180), outline=(255, 255, 255), width=1)
    prompt_display = prompt if len(prompt) < 85 else prompt[:82] + "..."
    draw.text((35, height - 58), f"PROMPT: {prompt_display}", fill=(240, 240, 240), font=font_large)

    return img

def generate_image(prompt: str, filename: str = None) -> str:
    """
    Generates a comic-style image based on the provided image prompt.
    Saves the image into static/panels/ and returns the relative path.

    Args:
        prompt (str): Image generation prompt.
        filename (str, optional): Target filename.

    Returns:
        str: Relative path to saved image ('static/panels/...').
    """
    if not filename:
        filename = sanitize_filename(prompt)

    path = f"static/panels/{filename}"
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # If image already generated, reuse
    if os.path.exists(path):
        return path

    hf_token = os.getenv("HF_API_KEY") or os.getenv("HF_TOKEN")
    use_local_sd = os.getenv("USE_LOCAL_SD", "false").lower() == "true"

    image = None

    # 1. Try local Diffusers pipeline if enabled
    if use_local_sd:
        pipe = _get_diffusers_pipeline()
        if pipe is not None:
            try:
                image = pipe(prompt).images[0]
            except Exception as e:
                print(f"Error in diffusers generation: {e}")

    # 2. Try Hugging Face Inference API if token available
    if image is None and hf_token:
        try:
            image = _generate_via_hf_api(prompt, hf_token)
        except Exception as e:
            print(f"HF API image generation fallback: {e}")

    # 3. Stylized Comic Panel Generator (High quality offline fallback)
    if image is None:
        image = _generate_styled_comic_panel(prompt)

    image.save(path, format="PNG")
    return path
