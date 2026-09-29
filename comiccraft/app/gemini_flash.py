import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Setup GenAI with GEMINI_API_KEY
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

# We use gemini-1.5-flash as specified in the architecture (or fallback to latest flash model)
FLASH_MODEL_NAME = os.getenv("GEMINI_FLASH_MODEL", "gemini-1.5-flash")

def get_flash_model():
    return genai.GenerativeModel(FLASH_MODEL_NAME)

def generate_outline(user_prompt: str) -> list:
    """
    Generates a 5-panel comic layout based on the user's story idea using Gemini.

    Args:
        user_prompt (str): The user's comic idea prompt.

    Returns:
        list: A list of dictionaries, one for each panel.
    """
    prompt = f"""
You are a professional AI comic planner.

Your task is to generate a *strictly formatted* JSON array containing 5 panel descriptions for a comic based on the story idea below:

STORY: "{user_prompt}"

Each JSON object must include:
- "panel" (integer)
- "title" (string)
- "scene_description" (string)
- "image_prompt" (string)

Respond ONLY in this valid JSON format, without any explanations or markdown:
[
  {{
    "panel": 1,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }},
  {{
    "panel": 2,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }},
  {{
    "panel": 3,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }},
  {{
    "panel": 4,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }},
  {{
    "panel": 5,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }}
]
"""
    output_text = ""
    try:
        if not os.getenv("GEMINI_API_KEY"):
            # Provide high quality fallback outline if API key is not configured
            print("⚠️ GEMINI_API_KEY not found in environment. Using demo outline.")
            return _generate_demo_outline(user_prompt)

        model = get_flash_model()
        response = model.generate_content(prompt)
        output_text = response.text.strip()
        print("\n🔥 RAW GEMINI RESPONSE 🔥\n", output_text)

        # Remove any markdown formatting if present
        if output_text.startswith("```json"):
            output_text = output_text.replace("```json", "", 1)
            if output_text.endswith("```"):
                output_text = output_text[:-3]
            output_text = output_text.strip()
        elif output_text.startswith("```"):
            output_text = output_text.replace("```", "", 1)
            if output_text.endswith("```"):
                output_text = output_text[:-3]
            output_text = output_text.strip()

        panel_data = json.loads(output_text)

        # Additional structure validation
        if not isinstance(panel_data, list):
            raise ValueError("Gemini response is not a list.")

        for panel in panel_data:
            if not isinstance(panel, dict) or not all(key in panel for key in ("panel", "title", "scene_description", "image_prompt")):
                raise ValueError(f"Invalid panel format or missing keys: {panel}")

        return panel_data

    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", e)
        print("❌ Full Text Received:\n", output_text)
        return _generate_demo_outline(user_prompt)
    except Exception as e:
        print("❌ Unexpected Error in generate_outline:", e)
        # Fallback to demo outline so the user experience doesn't break
        return _generate_demo_outline(user_prompt)

def _generate_demo_outline(user_prompt: str) -> list:
    """Fallback generator when API key is missing or quota is exhausted."""
    return [
        {
            "panel": 1,
            "title": "The Forest's Edge",
            "scene_description": "Free, a red fox with intelligent eyes, stands at the edge of a dark, imposing forest. Sunlight barely penetrates the dense canopy. He looks apprehensive but determined.",
            "image_prompt": f"Realistic painting of a brave red fox standing at the edge of a dark mysterious enchanted forest, dramatic lighting, detailed comic art style, {user_prompt}"
        },
        {
            "panel": 2,
            "title": "Into the Deep Woods",
            "scene_description": "Free cautiously enters the forest, the path barely visible beneath twisted branches and overgrown foliage. An unnatural silence hangs in the air.",
            "image_prompt": f"Red fox exploring deep glowing enchanted woods, ancient towering trees, mystical atmosphere, vibrant colors, comic book art, {user_prompt}"
        },
        {
            "panel": 3,
            "title": "The Whispering Glade",
            "scene_description": "Free discovers a hidden clearing bathed in celestial light, where mysterious floating orbs illuminate ancient runic stones.",
            "image_prompt": f"Magical forest glade with glowing mystical runes and floating wisps of light, curious red fox observing, comic book illustration style, {user_prompt}"
        },
        {
            "panel": 4,
            "title": "An Unexpected Challenge",
            "scene_description": "A gentle guardian spirit materializes from the mist, challenging Free to prove his courage and pure intentions.",
            "image_prompt": f"Ethereal spirit guardian encountering a brave fox in an enchanted grove, magical glowing aura, dynamic comic art, {user_prompt}"
        },
        {
            "panel": 5,
            "title": "The Discovery",
            "scene_description": "Free unlocks the heart of the forest, rewarded with ancient wisdom and surrounded by flourishing magical life.",
            "image_prompt": f"Triumphant red fox basking in magical golden light in the heart of enchanted forest, inspiring comic style finale, {user_prompt}"
        }
    ]
