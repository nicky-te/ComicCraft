# ComicCraft - AI Comic Story Creator using Gemini Models

**ComicCraft** is an end-to-end web application that leverages Generative AI to create personalized, multi-panel comic book stories and illustrations based on user prompts. Built with **FastAPI**, **Google Gemini AI models (Flash & Pro)**, and **Stable Diffusion (Hugging Face Diffusers)**, ComicCraft automates the entire creative storytelling pipeline from outline to exportable PDF.

---

## 🌟 Features

- **Automated 5-Panel Comic Planning**: Powered by **Gemini 1.5 Flash** for rapid, structured JSON panel planning.
- **Rich Story Narration & Dialogues**: Crafted by **Gemini 1.5 Pro** to generate dialogue, captions, and narrative arcs.
- **Comic-Style Illustrations**: Generated per panel using **Stable Diffusion** / Diffusers with fallback rendering.
- **Dynamic Web Interface**: Interactive form with setting, tone, and art style customization built with HTML5, CSS3, and Jinja2 templates.
- **One-Click PDF Export**: Uses **FPDF** to compile all panels, illustrations, and dialogues into a timestamped, downloadable PDF book.
- **RESTful API**: Supports programmatic comic generation via `/generate-comic/json`.

---

## 🏗️ Technical Architecture & Pipeline

```
[ User Browser ]
       │
       ▼
[ FastAPI Backend (app/main.py) ]
       │
       ├──► HTML Templating (Jinja2 + CSS)
       │       ├── index.html (Input Form)
       │       ├── comic_preview.html (Comic Preview Page)
       │       └── export_success.html (Download Confirmation Page)
       │
       └──► AI Comic Generation Logic (routes.py + AI Modules)
               │
               ├── 1. Gemini Flash (app/gemini_flash.py) ──► 5-Panel Outline (JSON)
               ├── 2. Gemini Pro (app/gemini_pro.py)     ──► Full Story Narration & Dialogues
               ├── 3. Stable Diffusion (app/image_generator.py) ──► Panel Illustrations
               ├── 4. Layout Builder (app/layout_builder.py) ──► Assemble Comic Structure
               └── 5. Comic Exporter (app/exporters.py) ──► Multi-Page PDF via FPDF
```

---

## 📁 Project Structure

```
comiccraft/
│
├── app/
│   ├── __init__.py           # Package marker
│   ├── main.py               # FastAPI application entrypoint & static mounting
│   ├── routes.py             # Route handlers (/generate, /generate-comic/json, etc.)
│   ├── gemini_flash.py       # Gemini 1.5 Flash panel outline generator
│   ├── gemini_pro.py         # Gemini 1.5 Pro story narration & dialogue generator
│   ├── image_generator.py    # Stable Diffusion / Diffusers image generator
│   ├── layout_builder.py     # Layout binding and panel assembly logic
│   └── exporters.py          # PDF compilation and exporter using FPDF
│
├── templates/
│   ├── index.html            # Comic input form (Prompt, Character, Setting, Tone, Style)
│   ├── comic_preview.html    # Panel-by-panel comic preview page
│   └── export_success.html   # Download confirmation success page
│
├── static/
│   ├── css/
│   │   └── style.css         # Modern, responsive styles matching specification
│   ├── js/
│   │   └── script.js         # Frontend interactions, loading spinner & download handling
│   ├── panels/               # Generated panel images
│   ├── exports/              # Generated comic PDF files
│   └── fonts/                # Fonts for PDF generation
│
├── .env                      # Environment variables (API keys)
├── .env.example              # Example environment configuration
├── requirements.txt          # Python dependencies list
└── README.md                 # Complete project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites

- **Python 3.9+** installed on your system.
- **Google Gemini API Key** (from [Google AI Studio](https://aistudio.google.com/)).
- *(Optional)* Hugging Face API Token (for remote Stable Diffusion generation).

### 2. Create and Activate Virtual Environment

```bash
cd comiccraft

# Create virtual environment
python -m venv comiccraft-env

# Activate virtual environment:
# On macOS / Linux:
source comiccraft-env/bin/activate

# On Windows:
comiccraft-env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Edit the `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
HF_API_KEY=your_huggingface_api_token_here
```

*(Note: ComicCraft includes built-in offline fallbacks, so the app will run and demonstrate full functionality even before configuring API keys.)*

---

## 🖥️ Running the Application

Launch the FastAPI development server with hot-reload enabled:

```bash
uvicorn app.main:app --reload
```

Once running, access the web pages in your browser:

- **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc API Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Loads the homepage with the comic input form. |
| `POST` | `/generate` | Handles form submission, executes AI pipeline, and renders the comic preview. |
| `POST` | `/generate-comic/json` | Programmatic API endpoint accepting JSON payloads to return structured layout & PDF path. |
| `GET` | `/export-success` | Displays the export confirmation success page. |
| `GET` | `/test-image` | Developer utility route to test image generation from a custom prompt. |

### Example JSON API Request

```bash
curl -X POST "http://127.0.0.1:8000/generate-comic/json" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "A brave fox explores an ancient enchanted forest.",
       "character_name": "Free",
       "setting": "Forest",
       "tone": "Dramatic",
       "style": "Realistic"
     }'
```

---

## 📜 License

This project is open-source and available under the MIT License.
