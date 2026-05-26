import os
import json
import base64

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SYSTEM_PROMPT = """You are an expert sarcasm and irony detector. You can detect sarcasm in ANY language including English, Hindi, Spanish, and others.

Analyze the provided content and return a JSON response with exactly these fields:
{
  "is_sarcastic": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation",
  "text_signal": "what in the text signals sarcasm or not",
  "image_signal": "what in the image signals sarcasm or not (if provided)"
}

Rules:
- Confidence 0.0 = definitely not sarcastic, 1.0 = definitely sarcastic
- Look for irony, mock praise, exaggerated enthusiasm, contradictions
- For images: look for memes, sarcastic captions, reaction images, ironic juxtaposition
- Return ONLY valid JSON, no markdown formatting"""

_NO_KEY_RESULT = {
    'score': 0.5, 'confidence': 0.0,
    'is_sarcastic': False,
    'reasoning': 'AI analyzer not configured (no GEMINI_API_KEY). Add it to .env to enable.',
    'text_signal': '', 'image_signal': '',
}


class ClaudeAnalyzer:
    """AI-powered sarcasm analyzer using Google Gemini API (free tier)."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._api_key = os.getenv('GEMINI_API_KEY', '').strip()
            cls._instance._model = None
        return cls._instance

    def _get_model(self):
        if not self._api_key:
            return None
        if self._model is None:
            import google.generativeai as genai
            genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel(
                'gemini-2.0-flash',
                system_instruction=SYSTEM_PROMPT,
            )
        return self._model

    def analyze(self, text: str, image_b64: str = None, image_mime: str = None) -> dict:
        model = self._get_model()
        if model is None:
            return _NO_KEY_RESULT

        parts = []

        # Add image if provided
        if image_b64 and image_mime:
            mime_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                        'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp'}
            media_type = mime_map.get(image_mime.lower(), 'image/jpeg')
            parts.append({
                'inline_data': {
                    'mime_type': media_type,
                    'data': image_b64,
                }
            })

        prompt = f'Analyze this for sarcasm:\n\nText: {text or "(no text provided)"}\n\nReturn only valid JSON.'
        parts.append(prompt)

        try:
            response = model.generate_content(parts)
            raw = response.text.strip()
            # Extract JSON if wrapped in markdown
            if '```' in raw:
                raw = raw.split('```')[1]
                if raw.startswith('json'):
                    raw = raw[4:]
                raw = raw.strip()
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
            print(f'[Gemini] API error: {e}')
            return {
                'score': 0.5, 'confidence': 0.0,
                'is_sarcastic': False,
                'reasoning': f'AI API error: {e}',
                'text_signal': '', 'image_signal': '',
            }
