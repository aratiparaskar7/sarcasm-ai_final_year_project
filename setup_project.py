#!/usr/bin/env python3
"""
Sarcasm Detection Project - Automated Setup Script
Run: python setup_project.py
"""
import os
import subprocess
import sys

BASE = r"c:\Final yr Project\sarcasm_detect"

# ── File contents ──────────────────────────────────────────────────────────────

FILES = {}

FILES["requirements.txt"] = """\
django==4.2.11
djangorestframework==3.15.1
python-dotenv==1.0.1
anthropic==0.25.0
torch==2.6.0
torchvision==0.21.0
transformers==4.40.1
Pillow==10.3.0
opencv-python==4.9.0.80
librosa==0.10.1
soundfile==0.12.1
emoji==2.11.1
numpy==1.26.4
scikit-learn==1.4.2
gunicorn==22.0.0
whitenoise==6.6.0
"""

FILES[".env"] = """\
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production-abc123xyz
ALLOWED_HOSTS=localhost,127.0.0.1
"""

FILES[".gitignore"] = """\
.env
*.pyc
__pycache__/
db.sqlite3
media/
.venv/
venv/
*.egg-info/
dist/
.DS_Store
"""

FILES["runtime.txt"] = "python-3.11.9\n"

FILES["Procfile"] = "web: gunicorn sarcasm_detect.wsgi --log-file -\n"

FILES["manage.py"] = """\
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sarcasm_detect.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
"""

FILES["sarcasm_detect/__init__.py"] = ""

FILES["sarcasm_detect/settings.py"] = """\
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'analyzer.apps.AnalyzerConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sarcasm_detect.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sarcasm_detect.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

FILE_UPLOAD_MAX_MEMORY_SIZE = 104857600   # 100 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600
"""

FILES["sarcasm_detect/urls.py"] = """\
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('analyzer.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""

FILES["sarcasm_detect/wsgi.py"] = """\
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sarcasm_detect.settings')
application = get_wsgi_application()
"""

# ── Analyzer app ───────────────────────────────────────────────────────────────

FILES["analyzer/__init__.py"] = ""

FILES["analyzer/apps.py"] = """\
from django.apps import AppConfig
import threading

class AnalyzerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analyzer'

    def ready(self):
        # Warm up ML models in background thread so first request isn't slow
        def warmup():
            try:
                from analyzer.ml.text_analyzer import TextAnalyzer
                from analyzer.ml.image_analyzer import ImageAnalyzer
                from analyzer.ml.audio_analyzer import AudioAnalyzer
                TextAnalyzer()
                ImageAnalyzer()
                AudioAnalyzer()
                print('[Warmup] ML models loaded successfully.')
            except Exception as e:
                print(f'[Warmup] Warning: {e}')
        threading.Thread(target=warmup, daemon=True).start()
"""

FILES["analyzer/models.py"] = """\
from django.db import models
import uuid

class SarcasmAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    text_content = models.TextField(blank=True)
    has_image = models.BooleanField(default=False)
    has_audio = models.BooleanField(default=False)
    has_video = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Analysis {self.id} @ {self.created_at:%Y-%m-%d %H:%M}'


class ImageInput(models.Model):
    analysis = models.OneToOneField(SarcasmAnalysis, on_delete=models.CASCADE, related_name='image_input')
    image_file = models.ImageField(upload_to='images/')

class AudioInput(models.Model):
    analysis = models.OneToOneField(SarcasmAnalysis, on_delete=models.CASCADE, related_name='audio_input')
    audio_file = models.FileField(upload_to='audio/')
    transcript = models.TextField(blank=True)

class VideoInput(models.Model):
    analysis = models.OneToOneField(SarcasmAnalysis, on_delete=models.CASCADE, related_name='video_input')
    video_file = models.FileField(upload_to='videos/')

class ModalityResult(models.Model):
    MODALITY_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('audio', 'Audio'),
        ('video', 'Video'),
        ('emoji', 'Emoji'),
        ('claude', 'Claude AI'),
    ]
    analysis = models.ForeignKey(SarcasmAnalysis, on_delete=models.CASCADE, related_name='modality_results')
    modality = models.CharField(max_length=10, choices=MODALITY_CHOICES)
    score = models.FloatField()   # 0.0 = not sarcastic, 1.0 = sarcastic
    confidence = models.FloatField(default=0.0)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('analysis', 'modality')

class SarcasmResult(models.Model):
    analysis = models.OneToOneField(SarcasmAnalysis, on_delete=models.CASCADE, related_name='result')
    is_sarcastic = models.BooleanField()
    confidence = models.FloatField()   # 0–100 %
    reasoning = models.TextField(blank=True)
    text_score = models.FloatField(default=0.0)
    image_score = models.FloatField(default=0.0)
    audio_score = models.FloatField(default=0.0)
    video_score = models.FloatField(default=0.0)
    emoji_score = models.FloatField(default=0.0)
    claude_score = models.FloatField(default=0.0)

    def __str__(self):
        verdict = 'Sarcastic' if self.is_sarcastic else 'Not Sarcastic'
        return f'{verdict} ({self.confidence:.1f}%)'
"""

FILES["analyzer/admin.py"] = """\
from django.contrib import admin
from .models import SarcasmAnalysis, ImageInput, AudioInput, VideoInput, ModalityResult, SarcasmResult

@admin.register(SarcasmAnalysis)
class SarcasmAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'has_image', 'has_audio', 'has_video', 'get_verdict')
    list_filter = ('has_image', 'has_audio', 'has_video', 'result__is_sarcastic')
    search_fields = ('text_content',)
    readonly_fields = ('id', 'created_at')

    def get_verdict(self, obj):
        try:
            return '🎭 Sarcastic' if obj.result.is_sarcastic else '✅ Sincere'
        except Exception:
            return '—'
    get_verdict.short_description = 'Verdict'

@admin.register(SarcasmResult)
class SarcasmResultAdmin(admin.ModelAdmin):
    list_display = ('analysis', 'is_sarcastic', 'confidence', 'claude_score', 'text_score')
    list_filter = ('is_sarcastic',)

@admin.register(ModalityResult)
class ModalityResultAdmin(admin.ModelAdmin):
    list_display = ('analysis', 'modality', 'score', 'confidence')
    list_filter = ('modality',)

admin.site.register(ImageInput)
admin.site.register(AudioInput)
admin.site.register(VideoInput)
"""

FILES["analyzer/serializers.py"] = """\
from rest_framework import serializers
from .models import SarcasmAnalysis, SarcasmResult, ModalityResult

class ModalityResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModalityResult
        fields = ['modality', 'score', 'confidence', 'details']

class SarcasmResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SarcasmResult
        fields = ['is_sarcastic', 'confidence', 'reasoning',
                  'text_score', 'image_score', 'audio_score',
                  'video_score', 'emoji_score', 'claude_score']

class SarcasmAnalysisSerializer(serializers.ModelSerializer):
    result = SarcasmResultSerializer(read_only=True)
    modality_results = ModalityResultSerializer(many=True, read_only=True)

    class Meta:
        model = SarcasmAnalysis
        fields = ['id', 'created_at', 'text_content',
                  'has_image', 'has_audio', 'has_video',
                  'result', 'modality_results']
"""

FILES["analyzer/forms.py"] = """\
from django import forms

ALLOWED_IMAGE = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
ALLOWED_AUDIO = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/mp4', 'audio/x-wav']
ALLOWED_VIDEO = ['video/mp4', 'video/webm', 'video/ogg', 'video/quicktime']
MAX_SIZE = 100 * 1024 * 1024  # 100 MB

class AnalyzeForm(forms.Form):
    text = forms.CharField(required=False, max_length=5000, widget=forms.Textarea)
    image = forms.ImageField(required=False)
    audio = forms.FileField(required=False)
    video = forms.FileField(required=False)

    def clean_image(self):
        f = self.cleaned_data.get('image')
        if f:
            if f.content_type not in ALLOWED_IMAGE:
                raise forms.ValidationError('Unsupported image format.')
            if f.size > MAX_SIZE:
                raise forms.ValidationError('Image file too large (max 100 MB).')
        return f

    def clean_audio(self):
        f = self.cleaned_data.get('audio')
        if f:
            if f.size > MAX_SIZE:
                raise forms.ValidationError('Audio file too large (max 100 MB).')
        return f

    def clean_video(self):
        f = self.cleaned_data.get('video')
        if f:
            if f.size > MAX_SIZE:
                raise forms.ValidationError('Video file too large (max 100 MB).')
        return f

    def clean(self):
        data = super().clean()
        if not data.get('text') and not data.get('image') and not data.get('audio') and not data.get('video'):
            raise forms.ValidationError('Please provide at least one input (text, image, audio, or video).')
        return data
"""

FILES["analyzer/views.py"] = """\
from django.shortcuts import render, get_object_or_404
from .models import SarcasmAnalysis, SarcasmResult

def index(request):
    total = SarcasmAnalysis.objects.count()
    sarcastic = SarcasmResult.objects.filter(is_sarcastic=True).count()
    return render(request, 'analyzer/index.html', {'total_analyses': total, 'sarcastic_count': sarcastic})

def analyze_view(request):
    return render(request, 'analyzer/analyze.html')

def result_view(request, analysis_id):
    analysis = get_object_or_404(SarcasmAnalysis, id=analysis_id)
    result = get_object_or_404(SarcasmResult, analysis=analysis)
    modality_results = analysis.modality_results.all()
    return render(request, 'analyzer/result.html', {
        'analysis': analysis,
        'result': result,
        'modality_results': modality_results,
    })

def history_view(request):
    analyses = SarcasmAnalysis.objects.select_related('result').all()[:100]
    return render(request, 'analyzer/history.html', {'analyses': analyses})
"""

FILES["analyzer/api_views.py"] = """\
import base64
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import SarcasmAnalysis, ImageInput, AudioInput, VideoInput, ModalityResult, SarcasmResult
from .forms import AnalyzeForm

@csrf_exempt
@require_http_methods(['POST'])
def api_analyze(request):
    form = AnalyzeForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({'error': form.errors}, status=400)

    text = form.cleaned_data.get('text', '')
    image_file = form.cleaned_data.get('image')
    audio_file = form.cleaned_data.get('audio')
    video_file = form.cleaned_data.get('video')

    analysis = SarcasmAnalysis.objects.create(
        text_content=text,
        has_image=bool(image_file),
        has_audio=bool(audio_file),
        has_video=bool(video_file),
    )

    if image_file:
        ImageInput.objects.create(analysis=analysis, image_file=image_file)
    if audio_file:
        AudioInput.objects.create(analysis=analysis, audio_file=audio_file)
    if video_file:
        VideoInput.objects.create(analysis=analysis, video_file=video_file)

    try:
        scores = _run_analysis(analysis, text, image_file, audio_file, video_file)
    except Exception as e:
        analysis.delete()
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'id': str(analysis.id), 'result': scores})


def _run_analysis(analysis, text, image_file, audio_file, video_file):
    from analyzer.ml.claude_analyzer import ClaudeAnalyzer
    from analyzer.ml.text_analyzer import TextAnalyzer
    from analyzer.ml.image_analyzer import ImageAnalyzer
    from analyzer.ml.audio_analyzer import AudioAnalyzer
    from analyzer.ml.video_analyzer import VideoAnalyzer
    from analyzer.ml.emoji_analyzer import EmojiAnalyzer
    from analyzer.ml.fusion import FusionLayer

    scores = {}

    # Emoji (fast, no model)
    if text:
        emoji_result = EmojiAnalyzer().analyze(text)
        scores['emoji'] = emoji_result['score']
        ModalityResult.objects.create(
            analysis=analysis, modality='emoji',
            score=emoji_result['score'], confidence=emoji_result['confidence'],
            details=emoji_result,
        )

    # Text (RoBERTa)
    if text:
        text_result = TextAnalyzer().analyze(text)
        scores['text'] = text_result['score']
        ModalityResult.objects.create(
            analysis=analysis, modality='text',
            score=text_result['score'], confidence=text_result['confidence'],
            details=text_result,
        )

    # Image (CLIP)
    if image_file:
        img_path = analysis.image_input.image_file.path
        image_result = ImageAnalyzer().analyze(img_path)
        scores['image'] = image_result['score']
        ModalityResult.objects.create(
            analysis=analysis, modality='image',
            score=image_result['score'], confidence=image_result['confidence'],
            details=image_result,
        )

    # Audio (Whisper)
    if audio_file:
        audio_path = analysis.audio_input.audio_file.path
        audio_result = AudioAnalyzer().analyze(audio_path)
        scores['audio'] = audio_result['score']
        transcript = audio_result.get('transcript', '')
        analysis.audio_input.transcript = transcript
        analysis.audio_input.save()
        ModalityResult.objects.create(
            analysis=analysis, modality='audio',
            score=audio_result['score'], confidence=audio_result['confidence'],
            details=audio_result,
        )

    # Video (CLIP on frames)
    if video_file:
        video_path = analysis.video_input.video_file.path
        video_result = VideoAnalyzer().analyze(video_path)
        scores['video'] = video_result['score']
        ModalityResult.objects.create(
            analysis=analysis, modality='video',
            score=video_result['score'], confidence=video_result['confidence'],
            details=video_result,
        )

    # Claude API
    image_b64 = None
    if image_file:
        with open(analysis.image_input.image_file.path, 'rb') as f:
            image_b64 = base64.b64encode(f.read()).decode()
        image_mime = analysis.image_input.image_file.name.split('.')[-1]
    else:
        image_mime = None

    claude_result = ClaudeAnalyzer().analyze(text, image_b64, image_mime)
    scores['claude'] = claude_result['score']
    ModalityResult.objects.create(
        analysis=analysis, modality='claude',
        score=claude_result['score'], confidence=claude_result['confidence'],
        details=claude_result,
    )

    # Fusion
    final = FusionLayer().fuse(scores)

    SarcasmResult.objects.create(
        analysis=analysis,
        is_sarcastic=final['is_sarcastic'],
        confidence=final['confidence'],
        reasoning=claude_result.get('reasoning', ''),
        text_score=scores.get('text', 0.0),
        image_score=scores.get('image', 0.0),
        audio_score=scores.get('audio', 0.0),
        video_score=scores.get('video', 0.0),
        emoji_score=scores.get('emoji', 0.0),
        claude_score=scores.get('claude', 0.0),
    )

    return {
        'is_sarcastic': final['is_sarcastic'],
        'confidence': final['confidence'],
        'reasoning': claude_result.get('reasoning', ''),
        'scores': scores,
    }


@require_http_methods(['GET'])
def api_result(request, analysis_id):
    from .models import SarcasmAnalysis, SarcasmResult
    from .serializers import SarcasmAnalysisSerializer
    analysis = SarcasmAnalysis.objects.get(id=analysis_id)
    serializer = SarcasmAnalysisSerializer(analysis)
    return JsonResponse(serializer.data)


@require_http_methods(['GET'])
def api_history(request):
    from .serializers import SarcasmAnalysisSerializer
    analyses = SarcasmAnalysis.objects.select_related('result').all()[:50]
    serializer = SarcasmAnalysisSerializer(analyses, many=True)
    return JsonResponse(serializer.data, safe=False)


@require_http_methods(['GET'])
def api_ablation(request, analysis_id):
    from .models import SarcasmAnalysis
    from analyzer.ml.fusion import FusionLayer
    analysis = SarcasmAnalysis.objects.get(id=analysis_id)
    modality_results = {mr.modality: mr.score for mr in analysis.modality_results.all()}

    ablation = {}
    fusion = FusionLayer()
    for modality in list(modality_results.keys()):
        subset = {k: v for k, v in modality_results.items() if k != modality}
        ablation[f'without_{modality}'] = fusion.fuse(subset)

    for modality in modality_results:
        ablation[f'only_{modality}'] = fusion.fuse({modality: modality_results[modality]})

    return JsonResponse({'modality_scores': modality_results, 'ablation': ablation})


@require_http_methods(['GET'])
def api_health(request):
    return JsonResponse({'status': 'ok', 'version': '1.0.0'})
"""

FILES["analyzer/urls.py"] = """\
from django.urls import path
from . import views, api_views

urlpatterns = [
    # HTML pages
    path('', views.index, name='index'),
    path('analyze/', views.analyze_view, name='analyze'),
    path('result/<uuid:analysis_id>/', views.result_view, name='result'),
    path('history/', views.history_view, name='history'),

    # REST API
    path('api/analyze/', api_views.api_analyze, name='api_analyze'),
    path('api/result/<uuid:analysis_id>/', api_views.api_result, name='api_result'),
    path('api/history/', api_views.api_history, name='api_history'),
    path('api/ablation/<uuid:analysis_id>/', api_views.api_ablation, name='api_ablation'),
    path('api/health/', api_views.api_health, name='api_health'),
]
"""

# ── ML Modules ─────────────────────────────────────────────────────────────────

FILES["analyzer/ml/__init__.py"] = ""

FILES["analyzer/ml/claude_analyzer.py"] = """\
import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = \"\"\"You are an expert sarcasm and irony detector. Analyze the provided content
and return a JSON response with exactly these fields:
{
  "is_sarcastic": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation",
  "text_signal": "what in the text signals sarcasm or not",
  "image_signal": "what in the image signals sarcasm or not (if provided)"
}
Be precise. Confidence 0.0 = definitely not sarcastic, 1.0 = definitely sarcastic.\"\"\"


class ClaudeAnalyzer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = anthropic.Anthropic(
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        return cls._instance

    def analyze(self, text: str, image_b64: str = None, image_mime: str = None) -> dict:
        content = []

        if image_b64 and image_mime:
            mime_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                        'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp'}
            media_type = mime_map.get(image_mime.lower(), 'image/jpeg')
            content.append({
                'type': 'image',
                'source': {'type': 'base64', 'media_type': media_type, 'data': image_b64}
            })

        prompt = f'Analyze this for sarcasm:\\n\\nText: {text or "(no text provided)"}\\n\\nReturn only valid JSON.'
        content.append({'type': 'text', 'text': prompt})

        try:
            message = self.client.messages.create(
                model='claude-3-5-haiku-20241022',
                max_tokens=512,
                system=SYSTEM_PROMPT,
                messages=[{'role': 'user', 'content': content}]
            )
            raw = message.content[0].text.strip()
            # Extract JSON if wrapped in markdown
            if '```' in raw:
                raw = raw.split('```')[1]
                if raw.startswith('json'):
                    raw = raw[4:]
            data = json.loads(raw)
            score = float(data.get('confidence', 0.5))
            if not data.get('is_sarcastic', False):
                score = 1.0 - score
            return {
                'score': round(score, 4),
                'confidence': round(float(data.get('confidence', 0.5)), 4),
                'is_sarcastic': data.get('is_sarcastic', False),
                'reasoning': data.get('reasoning', ''),
                'text_signal': data.get('text_signal', ''),
                'image_signal': data.get('image_signal', ''),
            }
        except Exception as e:
            return {
                'score': 0.5, 'confidence': 0.0,
                'is_sarcastic': False,
                'reasoning': f'Claude API error: {e}',
                'text_signal': '', 'image_signal': '',
            }
"""

FILES["analyzer/ml/text_analyzer.py"] = """\
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F

MODEL_NAME = 'cardiffnlp/twitter-roberta-base-irony'

class TextAnalyzer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def _load(self):
        if not self._loaded:
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model.to(self.device)
            self.model.eval()
            self._loaded = True

    def analyze(self, text: str) -> dict:
        self._load()
        # Replace emojis with text representation for RoBERTa
        inputs = self.tokenizer(text, return_tensors='pt',
                                truncation=True, max_length=512).to(self.device)
        with torch.no_grad():
            logits = self.model(**inputs).logits
        probs = F.softmax(logits, dim=-1)[0]
        # Model labels: 0=non_irony, 1=irony
        irony_score = float(probs[1])
        confidence = float(probs.max())
        return {
            'score': round(irony_score, 4),
            'confidence': round(confidence, 4),
            'non_irony_prob': round(float(probs[0]), 4),
            'irony_prob': round(float(probs[1]), 4),
        }
"""

FILES["analyzer/ml/image_analyzer.py"] = """\
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch.nn.functional as F

MODEL_NAME = 'openai/clip-vit-base-patch32'

SARCASM_PROMPTS = [
    'a sarcastic meme',
    'an ironic image',
    'a mocking photograph',
    'a satirical picture',
]
SINCERE_PROMPTS = [
    'a sincere photograph',
    'a genuine moment',
    'a straightforward image',
    'a normal picture',
]
ALL_PROMPTS = SARCASM_PROMPTS + SINCERE_PROMPTS

class ImageAnalyzer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def _load(self):
        if not self._loaded:
            self.processor = CLIPProcessor.from_pretrained(MODEL_NAME)
            self.model = CLIPModel.from_pretrained(MODEL_NAME)
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model.to(self.device)
            self.model.eval()
            self._loaded = True

    def analyze(self, image_path: str) -> dict:
        self._load()
        image = Image.open(image_path).convert('RGB')
        inputs = self.processor(text=ALL_PROMPTS, images=image,
                                return_tensors='pt', padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs.logits_per_image[0]
        probs = F.softmax(logits, dim=0).cpu().numpy()

        sarcasm_score = float(probs[:len(SARCASM_PROMPTS)].mean())
        sincere_score = float(probs[len(SARCASM_PROMPTS):].mean())
        total = sarcasm_score + sincere_score
        normalized = sarcasm_score / total if total > 0 else 0.5

        return {
            'score': round(normalized, 4),
            'confidence': round(max(sarcasm_score, sincere_score), 4),
            'sarcasm_score': round(sarcasm_score, 4),
            'sincere_score': round(sincere_score, 4),
        }
"""

FILES["analyzer/ml/audio_analyzer.py"] = """\
import torch
import numpy as np
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import soundfile as sf

MODEL_NAME = 'openai/whisper-base'
SAMPLE_RATE = 16000

class AudioAnalyzer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def _load(self):
        if not self._loaded:
            self.processor = WhisperProcessor.from_pretrained(MODEL_NAME)
            self.model = WhisperForConditionalGeneration.from_pretrained(MODEL_NAME)
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model.to(self.device)
            self.model.eval()
            self._loaded = True

    def _transcribe(self, audio_path: str) -> str:
        try:
            audio, sr = sf.read(audio_path)
            if len(audio.shape) > 1:
                audio = audio.mean(axis=1)
            # Resample if needed
            if sr != SAMPLE_RATE:
                import librosa
                audio = librosa.resample(audio.astype(np.float32), orig_sr=sr, target_sr=SAMPLE_RATE)
            audio = audio.astype(np.float32)
            inputs = self.processor(audio, sampling_rate=SAMPLE_RATE, return_tensors='pt')
            input_features = inputs.input_features.to(self.device)
            with torch.no_grad():
                predicted_ids = self.model.generate(input_features)
            transcript = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            return transcript.strip()
        except Exception as e:
            return f'[Transcription error: {e}]'

    def _pitch_variance_score(self, audio_path: str) -> float:
        try:
            import librosa
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            f0, _, _ = librosa.pyin(y, fmin=50, fmax=600, sr=sr)
            f0_valid = f0[~np.isnan(f0)] if f0 is not None else np.array([])
            if len(f0_valid) < 10:
                return 0.3
            variance = float(np.std(f0_valid) / (np.mean(f0_valid) + 1e-6))
            # Normalize: high variance → might be sarcastic
            return float(min(variance / 0.5, 1.0))
        except Exception:
            return 0.3

    def analyze(self, audio_path: str) -> dict:
        self._load()
        transcript = self._transcribe(audio_path)
        pitch_score = self._pitch_variance_score(audio_path)

        text_score = 0.5
        if transcript and not transcript.startswith('['):
            from analyzer.ml.text_analyzer import TextAnalyzer
            text_result = TextAnalyzer().analyze(transcript)
            text_score = text_result['score']

        # Combine: 70% text, 30% pitch
        combined = 0.7 * text_score + 0.3 * pitch_score

        return {
            'score': round(combined, 4),
            'confidence': round(abs(combined - 0.5) * 2, 4),
            'transcript': transcript,
            'text_score': round(text_score, 4),
            'pitch_variance_score': round(pitch_score, 4),
        }
"""

FILES["analyzer/ml/video_analyzer.py"] = """\
import torch
import numpy as np
from PIL import Image
from analyzer.ml.image_analyzer import ImageAnalyzer

NUM_FRAMES = 5

class VideoAnalyzer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _extract_frames(self, video_path: str, n: int = NUM_FRAMES):
        import cv2
        cap = cv2.VideoCapture(video_path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total == 0:
            cap.release()
            return []
        indices = np.linspace(0, total - 1, n, dtype=int)
        frames = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ret, frame = cap.read()
            if ret:
                frames.append(Image.fromarray(frame[:, :, ::-1]))  # BGR→RGB
        cap.release()
        return frames

    def analyze(self, video_path: str) -> dict:
        frames = self._extract_frames(video_path, NUM_FRAMES)
        if not frames:
            return {'score': 0.5, 'confidence': 0.0, 'frames_analyzed': 0}

        img_analyzer = ImageAnalyzer()
        scores = []
        for frame in frames:
            # Save frame to temp file for ImageAnalyzer
            import tempfile, os
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                frame.save(tmp.name, 'JPEG')
                result = img_analyzer.analyze(tmp.name)
                scores.append(result['score'])
                os.unlink(tmp.name)

        avg_score = float(np.mean(scores))
        return {
            'score': round(avg_score, 4),
            'confidence': round(abs(avg_score - 0.5) * 2, 4),
            'frames_analyzed': len(frames),
            'frame_scores': [round(s, 4) for s in scores],
        }
"""

FILES["analyzer/ml/emoji_analyzer.py"] = """\
import emoji
import re

# Hand-curated sarcasm signal scores for high-signal emojis
EMOJI_SCORES = {
    '🙄': 0.90,  # eye roll - very sarcastic
    '😒': 0.85,  # unamused
    '🤦': 0.80,  # facepalm
    '🤦‍♂️': 0.80,
    '🤦‍♀️': 0.80,
    '😤': 0.75,  # frustrated
    '💀': 0.75,  # "dead" from cringe
    '😑': 0.75,  # expressionless
    '🙃': 0.85,  # upside-down smile (very ironic)
    '😏': 0.80,  # smirking
    '👏': 0.70,  # slow clap (sarcastic)
    '💯': 0.65,  # "sure, totally"
    '🤩': 0.60,  # over-enthusiastic
    '😂': 0.55,  # laughing (often sarcastic)
    '🤣': 0.55,
    '😆': 0.50,
    '😍': 0.45,  # could be sincere
    '❤️': 0.20,  # sincere
    '😊': 0.15,  # sincere
    '🥰': 0.10,  # sincere
    '😭': 0.50,  # ambiguous
    '🔥': 0.45,
    '✨': 0.30,
    '🎉': 0.25,
    '👍': 0.35,  # could be sarcastic thumbs up
    '🤔': 0.40,
    '😬': 0.65,
    '🙂': 0.55,  # subtle smile = often sarcastic in context
    '😌': 0.30,
    '🫠': 0.70,  # melting = sarcastic despair
    '💁': 0.65,
    '💁‍♀️': 0.65,
    '💁‍♂️': 0.65,
    '✌️': 0.30,
    '🤷': 0.50,
    '🤷‍♀️': 0.50,
    '🤷‍♂️': 0.50,
    '😮‍💨': 0.60,
    '😪': 0.45,
    '🫡': 0.55,
}

class EmojiAnalyzer:
    def analyze(self, text: str) -> dict:
        found_emojis = [e['emoji'] for e in emoji.emoji_list(text)]

        if not found_emojis:
            return {
                'score': 0.3,
                'confidence': 0.1,
                'emojis_found': [],
                'emoji_scores': {},
                'count': 0,
            }

        emoji_scores_found = {}
        scored = []
        for e in found_emojis:
            s = EMOJI_SCORES.get(e, 0.4)  # default neutral-ish
            emoji_scores_found[e] = s
            scored.append(s)

        avg_score = sum(scored) / len(scored)
        # More emojis = slightly higher confidence
        confidence = min(0.3 + 0.1 * len(scored), 0.9)

        return {
            'score': round(avg_score, 4),
            'confidence': round(confidence, 4),
            'emojis_found': found_emojis,
            'emoji_scores': emoji_scores_found,
            'count': len(found_emojis),
        }
"""

FILES["analyzer/ml/fusion.py"] = """\
# Fusion layer: weighted vote across modalities

DEFAULT_WEIGHTS = {
    'claude': 0.35,
    'text':   0.25,
    'image':  0.20,
    'audio':  0.12,
    'emoji':  0.08,
    'video':  0.10,
}

THRESHOLD = 0.5  # score > threshold → sarcastic

class FusionLayer:
    def fuse(self, scores: dict) -> dict:
        \"\"\"
        scores: dict mapping modality name → float score (0=sincere, 1=sarcastic)
        Returns: {is_sarcastic, confidence, weighted_score, weights_used}
        \"\"\"
        if not scores:
            return {'is_sarcastic': False, 'confidence': 0.0,
                    'weighted_score': 0.5, 'weights_used': {}}

        # Gather weights for present modalities and re-normalize
        raw_weights = {k: DEFAULT_WEIGHTS.get(k, 0.1) for k in scores}
        total_weight = sum(raw_weights.values())
        weights = {k: v / total_weight for k, v in raw_weights.items()}

        weighted_score = sum(scores[k] * weights[k] for k in scores)
        is_sarcastic = weighted_score > THRESHOLD

        # Confidence = how far from 0.5 threshold, scaled to 0-100%
        confidence = round(abs(weighted_score - 0.5) * 200, 1)
        confidence = min(confidence, 99.9)

        return {
            'is_sarcastic': bool(is_sarcastic),
            'confidence': confidence,
            'weighted_score': round(float(weighted_score), 4),
            'weights_used': weights,
        }
"""

# ── Templates ──────────────────────────────────────────────────────────────────

FILES["analyzer/templates/analyzer/base.html"] = """\
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}SarcasmAI{% endblock %}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
  {% load static %}
  <link rel="stylesheet" href="{% static 'analyzer/css/styles.css' %}">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark border-bottom border-secondary fixed-top">
  <div class="container">
    <a class="navbar-brand fw-bold" href="{% url 'index' %}">
      <i class="fa-solid fa-masks-theater text-warning me-2"></i>SarcasmAI
    </a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navMenu">
      <ul class="navbar-nav ms-auto">
        <li class="nav-item"><a class="nav-link" href="{% url 'index' %}"><i class="fa fa-home me-1"></i>Home</a></li>
        <li class="nav-item"><a class="nav-link" href="{% url 'analyze' %}"><i class="fa fa-search me-1"></i>Analyze</a></li>
        <li class="nav-item"><a class="nav-link" href="{% url 'history' %}"><i class="fa fa-clock-rotate-left me-1"></i>History</a></li>
        <li class="nav-item"><a class="nav-link" href="/admin/"><i class="fa fa-gear me-1"></i>Admin</a></li>
      </ul>
    </div>
  </div>
</nav>

<main class="container mt-5 pt-4">
  {% block content %}{% endblock %}
</main>

<footer class="mt-5 py-4 border-top border-secondary text-center text-muted small">
  <p class="mb-0">SarcasmAI &mdash; Hybrid Multimodal Sarcasm Detection &bull; Built with Django + Claude AI + PyTorch</p>
  <p class="mb-0">Final Year Project &mdash; Team of 5</p>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
{% block extra_js %}{% endblock %}
</body>
</html>
"""

FILES["analyzer/templates/analyzer/index.html"] = """\
{% extends 'analyzer/base.html' %}
{% block title %}SarcasmAI — Multimodal Sarcasm Detection{% endblock %}
{% block content %}
<div class="hero-section text-center py-5 mb-5">
  <h1 class="display-4 fw-bold mb-3">
    <span class="text-warning">Detect Sarcasm</span> Across All Media
  </h1>
  <p class="lead text-muted mb-4">
    Hybrid AI system combining RoBERTa, CLIP, Whisper &amp; Claude to detect sarcasm
    in text, images, audio, and video.
  </p>
  <a href="{% url 'analyze' %}" class="btn btn-warning btn-lg px-5 fw-bold">
    <i class="fa fa-bolt me-2"></i>Try It Now
  </a>
</div>

<div class="row g-4 mb-5">
  {% for mod in modalities %}
  <div class="col-md-4 col-lg-2-4">{% endfor %}
  <div class="col-sm-6 col-lg-4">
    <div class="card h-100 border-0" style="background:#1e2030;">
      <div class="card-body text-center p-4">
        <div class="mb-3" style="font-size:2.5rem;">📝</div>
        <h5 class="card-title" style="color:#4361ee;">Text Analysis</h5>
        <p class="card-text text-muted small">RoBERTa-base fine-tuned on Twitter irony data. Catches subtle linguistic sarcasm patterns.</p>
      </div>
    </div>
  </div>
  <div class="col-sm-6 col-lg-4">
    <div class="card h-100 border-0" style="background:#1e2030;">
      <div class="card-body text-center p-4">
        <div class="mb-3" style="font-size:2.5rem;">🖼️</div>
        <h5 class="card-title" style="color:#7209b7;">Image Analysis</h5>
        <p class="card-text text-muted small">CLIP ViT-B/32 compares image embeddings against sarcastic vs. sincere text prompts.</p>
      </div>
    </div>
  </div>
  <div class="col-sm-6 col-lg-4">
    <div class="card h-100 border-0" style="background:#1e2030;">
      <div class="card-body text-center p-4">
        <div class="mb-3" style="font-size:2.5rem;">🎵</div>
        <h5 class="card-title" style="color:#f72585;">Audio Analysis</h5>
        <p class="card-text text-muted small">Whisper transcribes speech + pitch variance detection for tonal sarcasm signals.</p>
      </div>
    </div>
  </div>
  <div class="col-sm-6 col-lg-4">
    <div class="card h-100 border-0" style="background:#1e2030;">
      <div class="card-body text-center p-4">
        <div class="mb-3" style="font-size:2.5rem;">🎬</div>
        <h5 class="card-title" style="color:#4cc9f0;">Video Analysis</h5>
        <p class="card-text text-muted small">CLIP applied to 5 sampled frames detects visual irony cues in video content.</p>
      </div>
    </div>
  </div>
  <div class="col-sm-6 col-lg-4">
    <div class="card h-100 border-0" style="background:#1e2030;">
      <div class="card-body text-center p-4">
        <div class="mb-3" style="font-size:2.5rem;">😏</div>
        <h5 class="card-title" style="color:#f8961e;">Emoji Analysis</h5>
        <p class="card-text text-muted small">Rule-based emoji sentiment mapping: 🙄 scores 0.90 sarcasm, 🙃 scores 0.85, etc.</p>
      </div>
    </div>
  </div>
  <div class="col-sm-6 col-lg-4">
    <div class="card h-100 border-0" style="background:#1e2030;">
      <div class="card-body text-center p-4">
        <div class="mb-3" style="font-size:2.5rem;">🤖</div>
        <h5 class="card-title" style="color:#ffd60a;">Claude AI</h5>
        <p class="card-text text-muted small">Anthropic Claude 3.5 Haiku provides reasoning-based multimodal sarcasm judgment.</p>
      </div>
    </div>
  </div>
</div>

<div class="text-center py-4">
  <div class="row justify-content-center g-4">
    <div class="col-auto">
      <div class="p-3 rounded" style="background:#1e2030;">
        <div class="h2 fw-bold text-warning">{{ total_analyses }}</div>
        <div class="text-muted small">Total Analyses</div>
      </div>
    </div>
    <div class="col-auto">
      <div class="p-3 rounded" style="background:#1e2030;">
        <div class="h2 fw-bold text-danger">{{ sarcastic_count }}</div>
        <div class="text-muted small">Sarcasm Detected</div>
      </div>
    </div>
    <div class="col-auto">
      <div class="p-3 rounded" style="background:#1e2030;">
        <div class="h2 fw-bold text-success">6</div>
        <div class="text-muted small">Modalities</div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
"""

FILES["analyzer/templates/analyzer/analyze.html"] = """\
{% extends 'analyzer/base.html' %}
{% load static %}
{% block title %}Analyze — SarcasmAI{% endblock %}
{% block content %}
<h2 class="mb-4"><i class="fa fa-search me-2 text-warning"></i>Analyze Content</h2>

<div id="alertBox" class="d-none"></div>

<div class="card border-0" style="background:#1e2030;">
  <div class="card-body p-4">
    <ul class="nav nav-pills mb-4" id="modalityTabs">
      <li class="nav-item"><button class="nav-link active" data-bs-toggle="pill" data-bs-target="#textTab">📝 Text</button></li>
      <li class="nav-item"><button class="nav-link" data-bs-toggle="pill" data-bs-target="#imageTab">🖼️ Image</button></li>
      <li class="nav-item"><button class="nav-link" data-bs-toggle="pill" data-bs-target="#audioTab">🎵 Audio</button></li>
      <li class="nav-item"><button class="nav-link" data-bs-toggle="pill" data-bs-target="#videoTab">🎬 Video</button></li>
    </ul>

    <form id="analyzeForm" enctype="multipart/form-data">
      {% csrf_token %}
      <div class="tab-content">
        <!-- TEXT TAB -->
        <div class="tab-pane fade show active" id="textTab">
          <div class="mb-3">
            <label class="form-label fw-semibold">Enter text to analyze</label>
            <textarea class="form-control bg-dark text-light border-secondary" id="textInput" name="text"
              rows="5" maxlength="5000"
              placeholder="Type or paste text here... Emojis welcome! 🙄"></textarea>
            <div class="d-flex justify-content-between mt-1">
              <small class="text-muted">Include emojis for better analysis</small>
              <small class="text-muted"><span id="charCount">0</span>/5000</small>
            </div>
          </div>
          <div id="emojiPreview" class="d-none mb-3 p-2 rounded" style="background:#12131a;">
            <small class="text-muted">Detected emojis: </small>
            <span id="emojiList" class="fs-5"></span>
          </div>
        </div>

        <!-- IMAGE TAB -->
        <div class="tab-pane fade" id="imageTab">
          <div class="mb-3">
            <label class="form-label fw-semibold">Upload image (JPEG, PNG, GIF, WebP)</label>
            <div class="drop-zone" id="imageDropZone">
              <i class="fa fa-image fa-3x mb-2 text-muted"></i>
              <p class="text-muted mb-2">Drag &amp; drop or click to upload</p>
              <input type="file" id="imageInput" name="image" accept="image/*" class="d-none">
              <button type="button" class="btn btn-outline-secondary btn-sm" onclick="document.getElementById('imageInput').click()">Browse</button>
            </div>
            <div id="imagePreviewContainer" class="d-none mt-2 text-center">
              <img id="imagePreview" class="img-fluid rounded" style="max-height:250px;">
            </div>
          </div>
        </div>

        <!-- AUDIO TAB -->
        <div class="tab-pane fade" id="audioTab">
          <div class="mb-3">
            <label class="form-label fw-semibold">Upload audio (MP3, WAV, OGG)</label>
            <div class="drop-zone" id="audioDropZone">
              <i class="fa fa-music fa-3x mb-2 text-muted"></i>
              <p class="text-muted mb-2">Drag &amp; drop or click to upload</p>
              <input type="file" id="audioInput" name="audio" accept="audio/*" class="d-none">
              <button type="button" class="btn btn-outline-secondary btn-sm" onclick="document.getElementById('audioInput').click()">Browse</button>
            </div>
            <div id="audioPreviewContainer" class="d-none mt-2">
              <audio id="audioPreview" controls class="w-100"></audio>
            </div>
          </div>
        </div>

        <!-- VIDEO TAB -->
        <div class="tab-pane fade" id="videoTab">
          <div class="mb-3">
            <label class="form-label fw-semibold">Upload video (MP4, WebM, MOV)</label>
            <div class="drop-zone" id="videoDropZone">
              <i class="fa fa-video fa-3x mb-2 text-muted"></i>
              <p class="text-muted mb-2">Drag &amp; drop or click to upload</p>
              <input type="file" id="videoInput" name="video" accept="video/*" class="d-none">
              <button type="button" class="btn btn-outline-secondary btn-sm" onclick="document.getElementById('videoInput').click()">Browse</button>
            </div>
            <div id="videoPreviewContainer" class="d-none mt-2">
              <video id="videoPreview" controls class="w-100 rounded" style="max-height:250px;"></video>
            </div>
          </div>
        </div>
      </div>

      <hr class="border-secondary">
      <div class="d-flex align-items-center gap-3">
        <button type="submit" class="btn btn-warning btn-lg fw-bold px-5" id="submitBtn">
          <i class="fa fa-bolt me-2"></i>Analyze Now
        </button>
        <div id="loadingState" class="d-none">
          <div class="spinner-border spinner-border-sm text-warning me-2" role="status"></div>
          <span id="loadingText" class="text-muted">Running analysis...</span>
        </div>
      </div>
    </form>
  </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{% static 'analyzer/js/analyze.js' %}"></script>
{% endblock %}
"""

FILES["analyzer/templates/analyzer/result.html"] = """\
{% extends 'analyzer/base.html' %}
{% load static %}
{% block title %}Result — SarcasmAI{% endblock %}
{% block content %}

{% if result.is_sarcastic %}
<div class="verdict-banner sarcastic text-center p-5 mb-5 rounded-4">
  <div style="font-size:4rem;">🎭</div>
  <h1 class="display-5 fw-bold text-white">SARCASTIC</h1>
  <div class="confidence-meter mt-3">
    <div class="progress" style="height:24px;border-radius:12px;">
      <div class="progress-bar bg-danger fw-bold" style="width:{{ result.confidence }}%">
        {{ result.confidence|floatformat:1 }}% confident
      </div>
    </div>
  </div>
</div>
{% else %}
<div class="verdict-banner sincere text-center p-5 mb-5 rounded-4">
  <div style="font-size:4rem;">✅</div>
  <h1 class="display-5 fw-bold text-white">NOT SARCASTIC</h1>
  <div class="confidence-meter mt-3">
    <div class="progress" style="height:24px;border-radius:12px;">
      <div class="progress-bar bg-success fw-bold" style="width:{{ result.confidence }}%">
        {{ result.confidence|floatformat:1 }}% confident
      </div>
    </div>
  </div>
</div>
{% endif %}

<div class="row g-4 mb-4">
  <!-- Radar Chart -->
  <div class="col-lg-5">
    <div class="card border-0 h-100" style="background:#1e2030;">
      <div class="card-body p-4">
        <h5 class="card-title mb-3"><i class="fa fa-chart-radar me-2 text-warning"></i>Modality Scores</h5>
        <canvas id="radarChart" style="max-height:300px;"></canvas>
      </div>
    </div>
  </div>

  <!-- Score Cards -->
  <div class="col-lg-7">
    <div class="row g-3">
      {% for mr in modality_results %}
      <div class="col-sm-6">
        <div class="card border-0 modality-card modality-{{ mr.modality }}" style="background:#1e2030;">
          <div class="card-body p-3">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="fw-semibold text-capitalize">
                {% if mr.modality == 'text' %}📝{% elif mr.modality == 'image' %}🖼️{% elif mr.modality == 'audio' %}🎵{% elif mr.modality == 'video' %}🎬{% elif mr.modality == 'emoji' %}😏{% else %}🤖{% endif %}
                {{ mr.modality|title }}
              </span>
              <span class="badge {% if mr.score > 0.5 %}bg-danger{% else %}bg-success{% endif %}">
                {{ mr.score|floatformat:2 }}
              </span>
            </div>
            <div class="progress" style="height:8px;border-radius:4px;">
              <div class="progress-bar modality-bar-{{ mr.modality }}"
                   style="width:{{ mr.score|floatformat:0 }}00%;" role="progressbar"></div>
            </div>
            <small class="text-muted mt-1 d-block">Confidence: {{ mr.confidence|floatformat:2 }}</small>
            {% if mr.details.transcript %}
            <small class="text-info d-block mt-1">📄 "{{ mr.details.transcript|truncatechars:60 }}"</small>
            {% endif %}
            {% if mr.details.emojis_found %}
            <small class="text-muted d-block mt-1">Emojis: {{ mr.details.emojis_found|join:" " }}</small>
            {% endif %}
          </div>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
</div>

<!-- Claude Reasoning -->
{% if result.reasoning %}
<div class="card border-0 mb-4" style="background:#1e2030;">
  <div class="card-body p-4">
    <h5 class="card-title">
      <i class="fa fa-brain me-2 text-warning"></i>Claude's Reasoning
      <button class="btn btn-sm btn-outline-secondary ms-2" type="button"
              data-bs-toggle="collapse" data-bs-target="#reasoningText">Toggle</button>
    </h5>
    <div class="collapse show" id="reasoningText">
      <p class="text-muted mt-2">{{ result.reasoning }}</p>
    </div>
  </div>
</div>
{% endif %}

<!-- Input Summary -->
<div class="card border-0 mb-4" style="background:#1e2030;">
  <div class="card-body p-4">
    <h5 class="card-title"><i class="fa fa-file-lines me-2 text-warning"></i>Analyzed Content</h5>
    {% if analysis.text_content %}
    <p class="mb-1"><strong>Text:</strong> <span class="text-muted">{{ analysis.text_content|truncatechars:300 }}</span></p>
    {% endif %}
    <p class="mb-0 small text-muted">
      <i class="fa fa-clock me-1"></i>{{ analysis.created_at }}
      {% if analysis.has_image %}<span class="ms-2">🖼️ Image</span>{% endif %}
      {% if analysis.has_audio %}<span class="ms-2">🎵 Audio</span>{% endif %}
      {% if analysis.has_video %}<span class="ms-2">🎬 Video</span>{% endif %}
    </p>
  </div>
</div>

<div class="d-flex gap-3">
  <a href="{% url 'analyze' %}" class="btn btn-warning fw-bold">
    <i class="fa fa-plus me-2"></i>Analyze Another
  </a>
  <a href="{% url 'history' %}" class="btn btn-outline-secondary">
    <i class="fa fa-clock-rotate-left me-2"></i>View History
  </a>
</div>

{% endblock %}

{% block extra_js %}
<script>
const scores = {
  text: {{ result.text_score }},
  image: {{ result.image_score }},
  audio: {{ result.audio_score }},
  video: {{ result.video_score }},
  emoji: {{ result.emoji_score }},
  claude: {{ result.claude_score }},
};
</script>
<script src="{% static 'analyzer/js/result.js' %}"></script>
{% endblock %}
"""

FILES["analyzer/templates/analyzer/history.html"] = """\
{% extends 'analyzer/base.html' %}
{% load static %}
{% block title %}History — SarcasmAI{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
  <h2><i class="fa fa-clock-rotate-left me-2 text-warning"></i>Analysis History</h2>
  <a href="{% url 'analyze' %}" class="btn btn-warning btn-sm fw-bold">
    <i class="fa fa-plus me-1"></i>New Analysis
  </a>
</div>

<!-- Filter buttons -->
<div class="mb-3" id="filterBtns">
  <button class="btn btn-sm btn-outline-secondary active" data-filter="all">All</button>
  <button class="btn btn-sm btn-outline-danger" data-filter="sarcastic">🎭 Sarcastic</button>
  <button class="btn btn-sm btn-outline-success" data-filter="sincere">✅ Sincere</button>
</div>

<!-- Search -->
<div class="mb-3">
  <input type="text" id="searchInput" class="form-control bg-dark text-light border-secondary"
         placeholder="Search by text content...">
</div>

{% if analyses %}
<div class="table-responsive">
  <table class="table table-dark table-hover align-middle" id="historyTable">
    <thead class="table-secondary">
      <tr>
        <th>Date</th>
        <th>Text Preview</th>
        <th>Modalities</th>
        <th>Verdict</th>
        <th>Confidence</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      {% for a in analyses %}
      <tr class="history-row" data-verdict="{% if a.result.is_sarcastic %}sarcastic{% else %}sincere{% endif %}">
        <td class="text-muted small">{{ a.created_at|date:"M j, Y H:i" }}</td>
        <td>
          <span class="text-truncate d-inline-block" style="max-width:220px;">
            {{ a.text_content|default:"(no text)"|truncatechars:60 }}
          </span>
        </td>
        <td>
          {% if a.has_image %}<span title="Image">🖼️</span>{% endif %}
          {% if a.has_audio %}<span title="Audio">🎵</span>{% endif %}
          {% if a.has_video %}<span title="Video">🎬</span>{% endif %}
          {% if not a.has_image and not a.has_audio and not a.has_video %}<span class="text-muted">—</span>{% endif %}
        </td>
        <td>
          {% if a.result %}
            {% if a.result.is_sarcastic %}
              <span class="badge bg-danger">🎭 Sarcastic</span>
            {% else %}
              <span class="badge bg-success">✅ Sincere</span>
            {% endif %}
          {% else %}
            <span class="badge bg-secondary">Pending</span>
          {% endif %}
        </td>
        <td>
          {% if a.result %}
          <div class="progress" style="width:80px;height:8px;">
            <div class="progress-bar {% if a.result.is_sarcastic %}bg-danger{% else %}bg-success{% endif %}"
                 style="width:{{ a.result.confidence }}%;"></div>
          </div>
          <small class="text-muted">{{ a.result.confidence|floatformat:1 }}%</small>
          {% endif %}
        </td>
        <td>
          <a href="{% url 'result' a.id %}" class="btn btn-sm btn-outline-warning">View</a>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% else %}
<div class="text-center py-5 text-muted">
  <i class="fa fa-inbox fa-3x mb-3"></i>
  <p>No analyses yet. <a href="{% url 'analyze' %}" class="text-warning">Run your first analysis</a>.</p>
</div>
{% endif %}
{% endblock %}

{% block extra_js %}
<script src="{% static 'analyzer/js/history.js' %}"></script>
{% endblock %}
"""

# ── Static files ───────────────────────────────────────────────────────────────

FILES["analyzer/static/analyzer/css/styles.css"] = """\
/* SarcasmAI — Dark Theme + Modality Colors */
:root {
  --color-text:   #4361ee;
  --color-image:  #7209b7;
  --color-audio:  #f72585;
  --color-video:  #4cc9f0;
  --color-emoji:  #f8961e;
  --color-claude: #ffd60a;
  --bg-card:      #1e2030;
  --bg-dark:      #12131a;
}

body {
  background: var(--bg-dark);
  color: #e0e0e0;
  min-height: 100vh;
}

/* Hero gradient */
.hero-section {
  background: linear-gradient(135deg, #12131a 0%, #1a1f3a 50%, #12131a 100%);
  border-radius: 1rem;
  border: 1px solid #2a2d4a;
}

/* Verdict banners */
.verdict-banner.sarcastic {
  background: linear-gradient(135deg, #ef233c, #d90429);
  border: 2px solid #ef233c;
}
.verdict-banner.sincere {
  background: linear-gradient(135deg, #2d6a4f, #52b788);
  border: 2px solid #52b788;
}

/* Drop zones */
.drop-zone {
  border: 2px dashed #444;
  border-radius: 0.75rem;
  padding: 3rem 1rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}
.drop-zone:hover, .drop-zone.dragover {
  border-color: var(--color-claude);
  background: rgba(255, 214, 10, 0.05);
}

/* Modality border colors */
.modality-text   { border-left: 3px solid var(--color-text)   !important; }
.modality-image  { border-left: 3px solid var(--color-image)  !important; }
.modality-audio  { border-left: 3px solid var(--color-audio)  !important; }
.modality-video  { border-left: 3px solid var(--color-video)  !important; }
.modality-emoji  { border-left: 3px solid var(--color-emoji)  !important; }
.modality-claude { border-left: 3px solid var(--color-claude) !important; }

/* Modality progress bars */
.modality-bar-text   { background: var(--color-text);   }
.modality-bar-image  { background: var(--color-image);  }
.modality-bar-audio  { background: var(--color-audio);  }
.modality-bar-video  { background: var(--color-video);  }
.modality-bar-emoji  { background: var(--color-emoji);  }
.modality-bar-claude { background: var(--color-claude); }

/* Cards */
.card { transition: transform 0.15s; }
.card:hover { transform: translateY(-2px); }

/* Navbar active */
.nav-link.active, .nav-link:hover { color: #ffd60a !important; }

/* Table */
.table-dark { background: var(--bg-card); }
.table-dark td, .table-dark th { border-color: #2a2d4a; }

/* Loading progress steps */
#loadingSteps li { transition: color 0.3s; }
"""

FILES["analyzer/static/analyzer/js/analyze.js"] = """\
// analyze.js — Form submit with AJAX + live emoji preview

const LOADING_STEPS = [
  'Extracting emojis...',
  'Running text analysis (RoBERTa)...',
  'Analyzing image (CLIP)...',
  'Processing audio (Whisper)...',
  'Analyzing video frames...',
  'Consulting Claude AI...',
  'Running fusion layer...',
  'Finalizing results...',
];

let stepIdx = 0;
let stepInterval = null;

function startLoadingSteps() {
  stepIdx = 0;
  const el = document.getElementById('loadingText');
  if (!el) return;
  el.textContent = LOADING_STEPS[0];
  stepInterval = setInterval(() => {
    stepIdx = (stepIdx + 1) % LOADING_STEPS.length;
    el.textContent = LOADING_STEPS[stepIdx];
  }, 2000);
}

function stopLoadingSteps() {
  clearInterval(stepInterval);
}

function showAlert(msg, type = 'danger') {
  const box = document.getElementById('alertBox');
  box.className = `alert alert-${type}`;
  box.textContent = msg;
  box.classList.remove('d-none');
  window.scrollTo(0, 0);
}

// Emoji live preview
const textInput = document.getElementById('textInput');
const emojiPreview = document.getElementById('emojiPreview');
const emojiList = document.getElementById('emojiList');
const charCount = document.getElementById('charCount');

if (textInput) {
  textInput.addEventListener('input', () => {
    const text = textInput.value;
    charCount.textContent = text.length;
    // Simple emoji regex
    const emojis = [...text.matchAll(/\\p{Emoji_Presentation}|\\p{Extended_Pictographic}/gu)].map(m => m[0]);
    if (emojis.length > 0) {
      emojiList.textContent = emojis.join(' ');
      emojiPreview.classList.remove('d-none');
    } else {
      emojiPreview.classList.add('d-none');
    }
  });
}

// File preview helpers
function setupFilePreview(inputId, previewId, containerId, type) {
  const input = document.getElementById(inputId);
  const preview = document.getElementById(previewId);
  const container = document.getElementById(containerId);
  if (!input) return;
  input.addEventListener('change', () => {
    const file = input.files[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    if (type === 'image') preview.src = url;
    else preview.src = url;
    container.classList.remove('d-none');
  });
}

setupFilePreview('imageInput', 'imagePreview', 'imagePreviewContainer', 'image');
setupFilePreview('audioInput', 'audioPreview', 'audioPreviewContainer', 'audio');
setupFilePreview('videoInput', 'videoPreview', 'videoPreviewContainer', 'video');

// Drag-drop
['image', 'audio', 'video'].forEach(mod => {
  const zone = document.getElementById(`${mod}DropZone`);
  const input = document.getElementById(`${mod}Input`);
  if (!zone || !input) return;
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
      input.files = e.dataTransfer.files;
      input.dispatchEvent(new Event('change'));
    }
  });
  zone.addEventListener('click', e => { if (e.target.tagName !== 'BUTTON') input.click(); });
});

// Form submit
document.getElementById('analyzeForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const submitBtn = document.getElementById('submitBtn');
  const loadingState = document.getElementById('loadingState');
  const alertBox = document.getElementById('alertBox');
  alertBox.classList.add('d-none');

  const formData = new FormData(e.target);
  const text = formData.get('text') || '';
  const image = formData.get('image');
  const audio = formData.get('audio');
  const video = formData.get('video');

  if (!text.trim() && (!image || !image.size) && (!audio || !audio.size) && (!video || !video.size)) {
    showAlert('Please provide at least one input (text, image, audio, or video).');
    return;
  }

  submitBtn.disabled = true;
  loadingState.classList.remove('d-none');
  startLoadingSteps();

  try {
    const resp = await fetch('/api/analyze/', { method: 'POST', body: formData });
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.error ? JSON.stringify(data.error) : 'Analysis failed.');
    }
    window.location.href = `/result/${data.id}/`;
  } catch (err) {
    stopLoadingSteps();
    submitBtn.disabled = false;
    loadingState.classList.add('d-none');
    showAlert('Error: ' + err.message);
  }
});
"""

FILES["analyzer/static/analyzer/js/result.js"] = """\
// result.js — Chart.js radar chart for modality scores

document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById('radarChart');
  if (!ctx || typeof scores === 'undefined') return;

  const COLORS = {
    text:   '#4361ee',
    image:  '#7209b7',
    audio:  '#f72585',
    video:  '#4cc9f0',
    emoji:  '#f8961e',
    claude: '#ffd60a',
  };

  const labels = Object.keys(scores).map(k => k.charAt(0).toUpperCase() + k.slice(1));
  const values = Object.values(scores).map(v => Math.round(v * 100));
  const bgColors = Object.keys(scores).map(k => COLORS[k] || '#888');

  new Chart(ctx, {
    type: 'radar',
    data: {
      labels,
      datasets: [{
        label: 'Sarcasm Score (%)',
        data: values,
        backgroundColor: 'rgba(255, 214, 10, 0.1)',
        borderColor: '#ffd60a',
        borderWidth: 2,
        pointBackgroundColor: bgColors,
        pointRadius: 5,
      }]
    },
    options: {
      responsive: true,
      scales: {
        r: {
          min: 0, max: 100,
          ticks: { color: '#888', backdropColor: 'transparent', stepSize: 25 },
          grid: { color: '#2a2d4a' },
          pointLabels: { color: '#ccc', font: { size: 13 } },
          angleLines: { color: '#2a2d4a' },
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.formattedValue}% sarcasm signal`
          }
        }
      }
    }
  });
});
"""

FILES["analyzer/static/analyzer/js/history.js"] = """\
// history.js — client-side filter and search

document.addEventListener('DOMContentLoaded', () => {
  const rows = Array.from(document.querySelectorAll('.history-row'));
  const searchInput = document.getElementById('searchInput');
  const filterBtns = document.querySelectorAll('#filterBtns button');

  let activeFilter = 'all';

  function applyFilters() {
    const query = searchInput ? searchInput.value.toLowerCase() : '';
    rows.forEach(row => {
      const verdict = row.dataset.verdict;
      const text = row.textContent.toLowerCase();
      const matchFilter = activeFilter === 'all' || verdict === activeFilter;
      const matchSearch = !query || text.includes(query);
      row.style.display = matchFilter && matchSearch ? '' : 'none';
    });
  }

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.dataset.filter;
      applyFilters();
    });
  });

  if (searchInput) {
    searchInput.addEventListener('input', applyFilters);
  }
});
"""

# ── GitHub Actions CI ──────────────────────────────────────────────────────────

FILES[".github/workflows/test.yml"] = """\
name: Django CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd sarcasm_detect
          pip install -r requirements.txt
      - name: Run migrations
        run: |
          cd sarcasm_detect
          python manage.py migrate
      - name: Health check
        run: |
          cd sarcasm_detect
          python manage.py check
"""

# ── Write all files ────────────────────────────────────────────────────────────

def write_file(rel_path: str, content: str):
    full_path = os.path.join(BASE, rel_path.replace('/', os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  ✓ {rel_path}')

def main():
    print(f'\n📁 Writing project files to: {BASE}\n')
    os.makedirs(BASE, exist_ok=True)
    for path, content in FILES.items():
        write_file(path, content)

    # Create .github/workflows outside BASE
    github_dir = r"c:\Final yr Project\.github\workflows"
    os.makedirs(github_dir, exist_ok=True)
    gha_path = os.path.join(github_dir, 'test.yml')
    with open(gha_path, 'w', encoding='utf-8') as f:
        f.write(FILES['.github/workflows/test.yml'])
    print(f'  ✓ .github/workflows/test.yml')

    print('\n✅ All files written!\n')
    print('=' * 50)
    print('NEXT STEPS:')
    print('  1. Edit sarcasm_detect\\.env and add your ANTHROPIC_API_KEY')
    print('  2. Run: pip install -r sarcasm_detect\\requirements.txt')
    print('  3. Run: cd sarcasm_detect && python manage.py migrate')
    print('  4. Run: python manage.py runserver')
    print('  5. Open: http://localhost:8000/')
    print('=' * 50)

if __name__ == '__main__':
    main()
