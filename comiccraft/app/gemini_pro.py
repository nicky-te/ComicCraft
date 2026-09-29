import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

PRO_MODEL_NAME = os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-pro")

def get_pro_model():
    return genai.GenerativeModel(PRO_MODEL_NAME)

def generate_story(outline: list) -> str:
    """
    Generates a detailed comic story with narration and character dialogue
    from a list of comic panel outlines using Gemini 1.5 Pro.

    Args:
        outline (list): A list of dictionaries or strings representing each comic panel's idea.

    Returns:
        str: The generated comic story text or an error message.
    """
    # Format the panel outline as a numbered list for clarity
    formatted_items = []
    for i, item in enumerate(outline):
        if isinstance(item, dict):
            title = item.get("title", f"Panel {i+1}")
            desc = item.get("scene_description", "")
            formatted_items.append(f"{i+1}. {title} - {desc}")
        else:
            formatted_items.append(f"{i+1}. {item}")
    
    formatted_outline = "\n".join(formatted_items)

    # Construct the prompt
    prompt = f"""
You're a comic book writer.

Given the following panel breakdown, write a comic-style story with engaging narration and character dialogues for each panel.

Panel Outline:
{formatted_outline}

Guidelines:
- Format each panel section starting with **Panel 1: <Title>**
- Use a fun and engaging tone, like an actual comic book.
- Include **CAPTION:**, **NARRATION:** and clearly marked character dialogue lines like **CHARACTER_NAME:** "...".
- Keep each panel self-contained but part of a cohesive story.
"""
    try:
        if not os.getenv("GEMINI_API_KEY"):
            print("⚠️ GEMINI_API_KEY not found in environment. Using demo story narration.")
            return _generate_demo_story(outline)

        model = get_pro_model()
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Error generating story with Gemini Pro: {e}")
        return _generate_demo_story(outline)

def _generate_demo_story(outline: list) -> str:
    """Fallback story generation for demo/testing purposes."""
    story_parts = []
    for idx, panel in enumerate(outline, start=1):
        if isinstance(panel, dict):
            title = panel.get("title", f"Panel {idx}")
            desc = panel.get("scene_description", "")
        else:
            title = f"Panel {idx}"
            desc = str(panel)

        part = f"""**Panel {idx}: {title}**
**CAPTION:** Whispers carried on the wind, tales of magic and mystery. Tales of the Whispering Woods...
**NARRATION:** Free, the bravest fox this side of Silverstream, stood at the threshold. The ancient trees loomed like watchful giants, their shadows a daunting promise.
**FREE:** "No turning back now. The heart of the forest calls, and I must answer."
"""
        story_parts.append(part)
    return "\n\n".join(story_parts)
