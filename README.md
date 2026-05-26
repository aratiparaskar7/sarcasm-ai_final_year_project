# SarcasmAI — Hybrid Multimodal Sarcasm Detection

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Django 4.2](https://img.shields.io/badge/django-4.2-darkgreen)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A comprehensive **final-year project** that detects sarcasm across **text, images, audio, video, and emoji** using a hybrid approach combining fine-tuned local ML models with Anthropic's Claude AI for semantic reasoning.

---

## 🎯 Project Overview

SarcasmAI is a multi-modal sarcasm detection system designed to identify sarcastic content across diverse input formats. The system uses a **weighted ensemble fusion** approach that combines:

- **Text Analysis**: RoBERTa-based irony detection
- **Image Analysis**: CLIP vision-language understanding
- **Audio Analysis**: Whisper transcription + acoustic features
- **Video Analysis**: Frame sampling with CLIP analysis
- **Emoji Detection**: Rule-based sentiment mapping
- **AI Reasoning**: Claude 3.5 Haiku for contextual analysis

### Key Features

✨ **Multi-Modal Input Support**: Text, images, audio, video, emoji  
🧠 **Hybrid Intelligence**: Local ML + Claude API for reasoning  
⚖️ **Weighted Fusion**: Dynamic score combination with auto-normalization  
📊 **Detailed Analytics**: Per-modality confidence scores and ablation analysis  
🌐 **REST API**: Complete API endpoints for integration  
💾 **Analysis History**: SQLite-backed persistent storage  
🎨 **Intuitive UI**: Bootstrap-based responsive interface  

---

## 📋 Table of Contents

- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Detailed Installation](#-detailed-installation)
- [Configuration](#-configuration)
- [Running the Project](#-running-the-project)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Model Information](#-model-information)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🛠️ Tech Stack

| Component | Technology | Details |
|-----------|-----------|---------|
| **Backend Framework** | Django 4.2 | Web application framework |
| **REST API** | Django REST Framework | API endpoints |
| **Text Models** | RoBERTa-base | Twitter-trained irony detection |
| **Vision Models** | CLIP ViT-B/32 | Vision-language encoding |
| **Audio Models** | Whisper-base | Speech-to-text transcription |
| **ML Framework** | PyTorch 2.6+ | Deep learning backend |
| **AI Reasoning** | Anthropic Claude 3.5 | Optional semantic analysis |
| **Frontend** | Bootstrap 5.3 + Vanilla JS | UI/UX |
| **Charts** | Chart.js 4 | Result visualization |
| **Database** | SQLite | Local data persistence |
| **Server** | Gunicorn + WhiteNoise | Production deployment |

---

## ⚡ Quick Start

**Prerequisites**: Python 3.11+, pip, git

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/sarcasm-ai.git
cd sarcasm-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies (CPU)
cd sarcasm_detect
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings (API keys optional)

# 5. Run migrations and start
python manage.py migrate
python manage.py runserver
```

**Access the app**: http://localhost:8000

See [INSTALLATION.md](INSTALLATION.md) for detailed setup including GPU support.

---

## 📦 Detailed Installation

### Prerequisites

- **Python**: 3.11 or higher
- **pip**: Latest version
- **Virtual Environment**: venv (recommended)
- **System**: Windows, macOS, or Linux
- **Storage**: ~3 GB for ML models (first run)
- **Memory**: 8 GB RAM minimum (16 GB recommended for smooth operation)

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/sarcasm-ai.git
cd sarcasm-ai
```

### Step 2: Create Virtual Environment

```bash
# Create
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### Step 3: Navigate to Project Directory

```bash
cd sarcasm_detect
```

### Step 4: Install Python Dependencies

**For CPU (Universal)**:
```bash
pip install --upgrade pip
pip install torch torchvision              # CPU version
pip install -r requirements.txt
```

**For GPU (NVIDIA CUDA 12.4)**:
```bash
pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
```

**For GPU (NVIDIA CUDA 11.8)**:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

> **Check your CUDA version**: Run `nvidia-smi` in terminal

### Step 5: Environment Configuration

```bash
# Copy template
cp .env.example .env

# Edit .env file with your configuration
```

**Required environment variables**:
```
SECRET_KEY=your-secret-key-here
DEBUG=True                          # Set to False for production
ALLOWED_HOSTS=localhost,127.0.0.1
ANTHROPIC_API_KEY=sk-ant-...       # Optional (app works without it)
```

See [Configuration](#-configuration) section for details.

### Step 6: Database Migrations

```bash
python manage.py makemigrations analyzer
python manage.py migrate
```

### Step 7: Create Admin User (Optional)

```bash
python manage.py createsuperuser
# Follow prompts to create superuser account
```

### Step 8: Download ML Models (One-time)

Models auto-download on first use, but you can pre-download:
```bash
python manage.py shell
>>> from analyzer.ml.text_analyzer import TextAnalyzer
>>> TextAnalyzer().load_model()  # ~500 MB
>>> exit()
```

---

## ⚙️ Configuration

### Environment Variables

Create/edit `.env` file in `sarcasm_detect/` directory:

```ini
# Django Settings
SECRET_KEY=django-insecure-your-random-key-change-in-production
DEBUG=True                          # MUST be False in production
ALLOWED_HOSTS=localhost,127.0.0.1

# API Keys (Optional)
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Database (default: SQLite)
# Uncomment for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/sarcasm_db

# Static Files
STATIC_ROOT=staticfiles/
STATIC_URL=/static/

# Media Files
MEDIA_URL=/media/
MEDIA_ROOT=media/
```

### Model Selection

Edit `analyzer/ml/fusion.py` to adjust fusion weights:

```python
MODALITY_WEIGHTS = {
    'claude': 0.35,      # Claude AI (optional)
    'text': 0.25,        # RoBERTa text
    'image': 0.20,       # CLIP image
    'audio': 0.12,       # Whisper audio
    'video': 0.10,       # CLIP video
    'emoji': 0.08,       # Rule-based emoji
}
```

Weights auto-normalize when modalities are unavailable (no upload/no API key).

---

## 🚀 Running the Project

### Development Server

```bash
# From sarcasm_detect/ directory
python manage.py runserver
```

**Access**:
- Web UI: http://localhost:8000
- Admin Panel: http://localhost:8000/admin (with superuser)
- API: http://localhost:8000/api/

### Running Tests

```bash
# Run all tests
python manage.py test analyzer

# Run with verbose output
python manage.py test analyzer -v 2

# Run specific test
python manage.py test analyzer.tests.TestClassName
```

### Collect Static Files (Production)

```bash
python manage.py collectstatic --noinput
```

---

## 🔌 API Documentation

Complete API endpoints and examples. See [API.md](API.md) for detailed reference.

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| GET | `/analyze/` | Analysis form UI |
| POST | `/api/analyze/` | Submit analysis |
| GET | `/result/<id>/` | View result UI |
| GET | `/api/result/<id>/` | Get result JSON |
| GET | `/history/` | Analysis history UI |
| GET | `/api/history/` | History JSON |
| GET | `/api/ablation/<id>/` | Per-modality breakdown |
| GET | `/api/health/` | Health check |

### Example: Text Analysis

```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -H "Content-Type: multipart/form-data" \
  -F "text=Oh great, another Monday 🙄"
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "result": {
    "is_sarcastic": true,
    "confidence": 78.4,
    "reasoning": "Expression suggests frustration with recurring event...",
    "modality_scores": {
      "text": 0.82,
      "emoji": 0.87,
      "claude": 0.72
    },
    "final_score": 0.80
  }
}
```

---

## 📁 Project Structure

```
sarcasm-ai/
├── sarcasm_detect/                 # Django project root
│   ├── analyzer/                   # Main app
│   │   ├── ml/
│   │   │   ├── __init__.py
│   │   │   ├── text_analyzer.py    # RoBERTa-base irony model
│   │   │   ├── image_analyzer.py   # CLIP ViT-B/32 encoder
│   │   │   ├── audio_analyzer.py   # Whisper + Librosa pitch
│   │   │   ├── video_analyzer.py   # CLIP on 5 sampled frames
│   │   │   ├── emoji_analyzer.py   # Rule-based emoji sentiment
│   │   │   ├── claude_analyzer.py  # Claude 3.5 Haiku integration
│   │   │   ├── rule_based_analyzer.py  # Heuristic rules
│   │   │   └── fusion.py           # Score fusion & normalization
│   │   ├── templates/analyzer/
│   │   │   ├── base.html           # Base template
│   │   │   ├── index.html          # Landing page
│   │   │   ├── analyze.html        # Analysis form
│   │   │   ├── result.html         # Results display
│   │   │   └── history.html        # History view
│   │   ├── static/analyzer/
│   │   │   ├── css/
│   │   │   │   └── styles.css      # Custom styling
│   │   │   └── js/
│   │   │       ├── analyze.js      # Form handling
│   │   │       ├── result.js       # Results visualization
│   │   │       └── history.js      # History interactions
│   │   ├── migrations/             # Database migrations
│   │   ├── models.py               # Django models
│   │   ├── views.py                # HTML views
│   │   ├── api_views.py            # REST API views
│   │   ├── serializers.py          # DRF serializers
│   │   ├── forms.py                # Django forms
│   │   ├── urls.py                 # URL routing
│   │   ├── admin.py                # Admin configuration
│   │   └── apps.py                 # App configuration
│   ├── sarcasm_detect/
│   │   ├── settings.py             # Django settings
│   │   ├── urls.py                 # Root URL routing
│   │   ├── wsgi.py                 # WSGI application
│   │   └── asgi.py                 # ASGI application
│   ├── manage.py                   # Django CLI
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment variables (local)
│   ├── .env.example                # Environment template
│   ├── .gitignore                  # Git ignore patterns
│   ├── Procfile                    # Heroku/Railway deployment
│   ├── runtime.txt                 # Python version (deployment)
│   ├── db.sqlite3                  # SQLite database (local)
│   └── media/                      # User uploads
├── .github/
│   └── workflows/
│       └── test.yml                # CI/CD workflow
├── README.md                       # This file
├── INSTALLATION.md                 # Detailed setup guide
├── API.md                          # API reference
└── LICENSE                         # MIT License
```

---

## 📊 Model Information

### Model Sizes & Performance

| Model | Type | Size | VRAM | Accuracy Notes |
|-------|------|------|------|----------------|
| twitter-roberta-base-irony | Text | ~500 MB | ~0.5 GB | Fine-tuned on Twitter irony |
| clip-vit-base-patch32 | Image/Video | ~600 MB | ~0.6 GB | Zero-shot classification |
| openai/whisper-base | Audio | ~150 MB | ~0.3 GB | Multilingual ASR |
| Claude 3.5 Haiku | API | ~0 MB | ~0 GB | Semantic reasoning (optional) |

**First-run Download**: ~1.3 GB total  
**Model Cache Location**: `~/.cache/huggingface/`

### Fusion Architecture

```
Text Input → RoBERTa (25%)
            ↓
Image Input → CLIP (20%)
            ↓
Audio Input → Whisper + Librosa (12%)  } → Fusion Algorithm
            ↓
Video Input → CLIP Frames (10%)        } → Weighted Ensemble
            ↓
Emoji Analysis → Rule-based (8%)       } → Re-normalization
            ↓
Claude API → AI Reasoning (35%)

Final Output: is_sarcastic (bool) + confidence (0-100)
```

---

## 🌐 Deployment

### Local Testing

```bash
cd sarcasm_detect
python manage.py runserver 0.0.0.0:8000
```

### Railway (Recommended for Free Tier)

1. **Connect Repository**:
   - Push code to GitHub
   - Log in to [Railway](https://railway.app)
   - Create new project from GitHub

2. **Configure Environment**:
   ```
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   ALLOWED_HOSTS=your-railway-domain.up.railway.app
   ANTHROPIC_API_KEY=sk-ant-...  (optional)
   ```

3. **Deploy**:
   - Railway auto-detects `Procfile`
   - Runs `python manage.py collectstatic` automatically
   - Service starts on port 8000

### Heroku

```bash
heroku create your-app-name
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret
heroku config:set ANTHROPIC_API_KEY=sk-ant-...
git push heroku main
```

### Docker (Optional)

```bash
docker build -t sarcasm-ai .
docker run -p 8000:8000 \
  -e SECRET_KEY=your-key \
  -e DEBUG=False \
  sarcasm-ai
```

---

## 👥 Team

This is a final-year university project developed by a team of 5 students.

**Project Duration**: Academic Year (Semester Final Year)  
**Status**: Completed and Production-Ready

---

## 📖 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/your-feature`
3. **Commit** changes: `git commit -m "Add feature description"`
4. **Push** to branch: `git push origin feature/your-feature`
5. **Open** a Pull Request with description

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for detailed guidelines.

---

## 📝 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) file for details.

**In short**: You're free to use, modify, and distribute this project for any purpose (personal, commercial) with attribution.

---

## 🔗 Additional Resources

- **Installation Help**: See [INSTALLATION.md](INSTALLATION.md)
- **API Reference**: See [API.md](API.md)
- **Django Docs**: https://docs.djangoproject.com/
- **PyTorch**: https://pytorch.org/
- **CLIP**: https://github.com/openai/CLIP
- **Whisper**: https://github.com/openai/whisper

---

## ❓ FAQ

**Q: Do I need an API key to run this?**  
A: No! The app works with local models only. Claude API is optional for enhanced reasoning.

**Q: What are the hardware requirements?**  
A: Minimum 8 GB RAM, ~3 GB disk for models. GPU (NVIDIA) highly recommended for audio/video.

**Q: How accurate is the detection?**  
A: Varies by modality (text: ~82%, emoji: ~87%). Fusion improves overall accuracy to ~80%+.

**Q: Can I use this for commercial purposes?**  
A: Yes! MIT license allows commercial use with attribution.

**Q: How do I update the models?**  
A: Models auto-update from Hugging Face. Delete `~/.cache/huggingface/` to re-download latest versions.

---

**Last Updated**: 2026-05-26  
**Version**: 1.0.0
