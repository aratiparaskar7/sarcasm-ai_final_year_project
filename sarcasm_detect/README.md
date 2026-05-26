# SarcasmAI — Hybrid Multimodal Sarcasm Detection

A final-year project that detects sarcasm across **text, image, audio, video, and emoji** using a fusion of local ML models and Claude AI.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2, Django REST Framework |
| Text | RoBERTa-base (twitter-roberta-base-irony) |
| Image | CLIP ViT-B/32 |
| Audio | Whisper-base + librosa pitch variance |
| Video | CLIP on 5 sampled frames (OpenCV) |
| Emoji | Rule-based emoji sentiment mapping |
| AI Reasoning | Anthropic Claude 3.5 Haiku (optional) |
| Fusion | Weighted score fusion (re-normalized MLP) |
| Frontend | Bootstrap 5.3 + Chart.js 4 + Vanilla JS |

## Setup

### 1. Clone / download the project
```
cd "c:\Final yr Project"
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
cd sarcasm_detect
pip install torch torchvision          # CPU version
pip install -r requirements.txt
```

For CUDA (GTX 1650/1660, check your CUDA version with `nvidia-smi`):
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
```

### 4. Configure environment
Edit `sarcasm_detect\.env`:
```
ANTHROPIC_API_KEY=sk-ant-...   # Optional — app works without it
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Run migrations
```bash
python manage.py makemigrations analyzer
python manage.py migrate
```

### 6. Create admin user (optional)
```bash
python manage.py createsuperuser
```

### 7. Run the server
```bash
python manage.py runserver
```

Open → **http://localhost:8000/**

---

## API Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/` | Landing page |
| GET | `/analyze/` | Analysis form |
| POST | `/api/analyze/` | Run analysis → `{id, result}` |
| GET | `/result/<id>/` | Results page |
| GET | `/api/result/<id>/` | Results JSON |
| GET | `/history/` | History page |
| GET | `/api/history/` | History JSON |
| GET | `/api/ablation/<id>/` | Per-modality ablation |
| GET | `/api/health/` | Health check |

### Example API call
```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -F "text=Oh great, another Monday 🙄"
```

Response:
```json
{
  "id": "uuid-here",
  "result": {
    "is_sarcastic": true,
    "confidence": 78.4,
    "reasoning": "...",
    "scores": {"text": 0.82, "emoji": 0.87, "claude": 0.5}
  }
}
```

---

## Fusion Weights

| Modality | Weight |
|---|---|
| Claude AI | 35% |
| RoBERTa (text) | 25% |
| CLIP (image) | 20% |
| Whisper (audio) | 12% |
| CLIP (video) | 10% |
| Emoji | 8% |

Weights auto-renormalize when a modality is absent (no file uploaded / no API key).

---

## Model Download Sizes (first run only)

| Model | Disk | VRAM |
|---|---|---|
| twitter-roberta-base-irony | ~500 MB | ~0.5 GB |
| clip-vit-base-patch32 | ~600 MB | ~0.6 GB |
| whisper-base | ~150 MB | ~0.3 GB |
| Claude (API) | 0 MB | 0 GB |

Models auto-download to `~/.cache/huggingface/` on first use.

---

## Running Tests
```bash
python manage.py test analyzer
```

---

## Deployment (Railway)

1. Push to GitHub
2. Connect repo to [Railway](https://railway.app)
3. Set env vars: `ANTHROPIC_API_KEY`, `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`
4. Railway auto-detects `Procfile`:
   ```
   web: gunicorn sarcasm_detect.wsgi --log-file -
   ```
5. Run `python manage.py collectstatic` after deploy

---

## Project Structure

```
sarcasm_detect/
├── analyzer/
│   ├── ml/
│   │   ├── claude_analyzer.py   ← Claude API (optional)
│   │   ├── text_analyzer.py     ← RoBERTa-base irony
│   │   ├── image_analyzer.py    ← CLIP ViT-B/32
│   │   ├── audio_analyzer.py    ← Whisper-base
│   │   ├── video_analyzer.py    ← CLIP on frames
│   │   ├── emoji_analyzer.py    ← Rule-based
│   │   └── fusion.py            ← Weighted fusion
│   ├── templates/analyzer/      ← HTML pages
│   ├── static/analyzer/         ← CSS + JS
│   ├── models.py
│   ├── api_views.py
│   └── views.py
└── sarcasm_detect/
    └── settings.py
```

## Team
Final Year Project — Team of 5
