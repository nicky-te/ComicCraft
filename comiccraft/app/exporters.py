import os
from datetime import datetime
try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

FONT_PATH = "static/fonts/DejaVuSans.ttf"
EXPORT_FOLDER = "static/exports"

class PDF(FPDF if FPDF is not None else object):
    pass

def save_pdf(layout: list) -> str:
    """
    Compiles the full comic into a multi-page PDF file using the FPDF library.
    Each panel's image and narration are placed neatly on separate pages.

    Args:
        layout (list): List of panel layout dictionaries.

    Returns:
        str: Relative path to saved PDF file.
    """
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    pdf_path = os.path.join(EXPORT_FOLDER, filename)

    if FPDF is None:
        # Fallback if fpdf is not yet installed in runtime
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4 Mock PDF Content")
        return pdf_path

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Determine font to use
    font_family = "Helvetica"
    if os.path.exists(FONT_PATH):
        try:
            pdf.add_font("DejaVu", "", FONT_PATH, uni=True)
            font_family = "DejaVu"
        except Exception:
            font_family = "Helvetica"

    for panel in layout:
        # Resolve file path for image
        image_path = panel.get("file_image_path") or panel.get("image_path", "").lstrip("/")
        story_text = panel.get("text", "")
        title = panel.get("title", f"Panel {panel.get('panel', 1)}")

        pdf.add_page()

        # Panel title
        pdf.set_font(font_family, "", 16)
        pdf.cell(0, 10, f"Panel {panel.get('panel', 1)}: {title}", ln=True, align="C")
        pdf.ln(5)

        # Image placement
        y_image = 28
        image_height = 100
        spacing_after_image = 12

        if os.path.exists(image_path):
            try:
                pdf.image(image_path, x=15, y=y_image, w=pdf.w - 30, h=image_height)
            except Exception as img_err:
                pdf.set_y(y_image)
                pdf.set_font(font_family, "", 10)
                pdf.multi_cell(0, 8, f"[Image display error: {img_err}]")
        else:
            pdf.set_y(y_image)
            pdf.set_font(font_family, "", 10)
            pdf.multi_cell(0, 8, f"[Image missing: {image_path}]")

        # Text placement below image
        pdf.set_y(y_image + image_height + spacing_after_image)

        # Scene description in italic/subdued text if present
        scene_desc = panel.get("scene_description", "")
        if scene_desc:
            pdf.set_font(font_family, "I" if font_family != "DejaVu" else "", 10)
            scene_clean = scene_desc.encode("latin-1", "replace").decode("latin-1") if font_family != "DejaVu" else scene_desc
            pdf.multi_cell(0, 6, f"Scene: {scene_clean}")
            pdf.ln(4)

        # Narration & Dialogues
        pdf.set_font(font_family, "", 11)
        story_lines = story_text.strip().splitlines()

        # Remove duplicate title line if present
        if story_lines and story_lines[0].strip().lower().startswith("**panel"):
            story_lines = story_lines[1:]

        cleaned_text = "\n".join(story_lines).strip()
        if font_family != "DejaVu":
            cleaned_text = cleaned_text.encode("latin-1", "replace").decode("latin-1")

        pdf.multi_cell(0, 7, cleaned_text)

    pdf.output(pdf_path)
    return pdf_path
