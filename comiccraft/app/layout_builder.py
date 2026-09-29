def build_comic_layout(image_paths: list, full_story: str, outline: list) -> list:
    """
    Organizes the generated images and full comic story into a structured layout.

    Args:
        image_paths (list): List of paths to generated panel images.
        full_story (str): Complete narration and dialogue story from Gemini Pro.
        outline (list): List of panel outlines with titles and scene descriptions.

    Returns:
        list: A list of panel dictionaries containing panel number, title,
              image_path, text, and scene_description.
    """
    # Split the full story into individual panel segments
    if "**Panel" in full_story:
        story_panels = full_story.split("**Panel")
        story_panels = [f"**Panel{panel}" for panel in story_panels if panel.strip()]
    elif "Panel " in full_story:
        story_panels = full_story.split("Panel ")
        story_panels = [f"Panel {panel}" for panel in story_panels if panel.strip()]
    else:
        # Paragraph fallback
        story_panels = [p.strip() for p in full_story.split("\n\n") if p.strip()]

    # If length doesn't match outline, pad or slice
    if len(story_panels) < len(outline):
        while len(story_panels) < len(outline):
            story_panels.append("")

    # Build layout panel by panel
    layout = []
    for idx, (image, text, panel_info) in enumerate(zip(image_paths, story_panels, outline), start=1):
        # Clean text by removing raw header if present
        raw_lines = text.strip().splitlines()
        if raw_lines and (raw_lines[0].lower().startswith("**panel") or raw_lines[0].lower().startswith("panel")):
            cleaned_text = "\n".join(raw_lines[1:]).strip()
        else:
            cleaned_text = text.strip()

        # Extract title and description
        if isinstance(panel_info, dict):
            panel_title = panel_info.get("title", f"Panel {idx}")
            scene_desc = panel_info.get("scene_description", "")
        else:
            panel_title = f"Panel {idx}"
            scene_desc = str(panel_info)

        # Ensure image path has leading slash for web rendering if relative
        web_image_path = "/" + image.replace("\\", "/").lstrip("/")

        layout.append({
            "panel": idx,
            "title": panel_title,
            "image_path": web_image_path,
            "file_image_path": image.replace("/", os_path_sep()),
            "text": cleaned_text,
            "scene_description": scene_desc
        })

    return layout

def os_path_sep():
    import os
    return os.sep
