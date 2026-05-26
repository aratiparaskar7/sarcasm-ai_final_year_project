import torch
import torch.nn.functional as F
from PIL import Image
import numpy as np

MODEL_NAME = 'openai/clip-vit-base-patch32'


def _try_ocr(image_path):
    """Try to extract text from image using pytesseract."""
    try:
        import pytesseract
        import os, shutil
        # Auto-detect Tesseract binary on Windows
        if not shutil.which('tesseract'):
            for candidate in [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                os.path.expanduser(r'~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'),
            ]:
                if os.path.isfile(candidate):
                    pytesseract.pytesseract.tesseract_cmd = candidate
                    break
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, timeout=10)
        return text.strip() if text else ''
    except Exception as e:
        print(f'[Image OCR] pytesseract error: {e}')
        return ''


def _detect_meme_features(image_path):
    """Detect meme-like features using image analysis (no ML model needed).
    Returns a dict with meme likelihood signals."""
    try:
        img = Image.open(image_path).convert('RGB')
        width, height = img.size
        arr = np.array(img)

        signals = {}

        # 1. Aspect ratio — memes are usually square-ish or slightly tall
        ratio = width / height if height > 0 else 1
        signals['aspect_ratio'] = ratio
        signals['is_square_ish'] = 0.6 < ratio < 1.7

        # 2. Color variance per region — memes often have solid color blocks (text bg)
        # Split into top/middle/bottom thirds
        h3 = height // 3
        regions = [arr[:h3], arr[h3:2*h3], arr[2*h3:]]
        region_stds = []
        for region in regions:
            std = float(region.std())
            region_stds.append(std)
        signals['region_stds'] = region_stds

        # Low std in top or bottom = likely text area with solid background
        has_solid_region = any(s < 35 for s in region_stds)
        signals['has_solid_region'] = has_solid_region

        # 3. Edge density — memes with text have more high-contrast edges
        gray = np.mean(arr, axis=2)
        # Simple edge detection: absolute difference between adjacent pixels
        edges_h = np.abs(np.diff(gray, axis=1))
        edges_v = np.abs(np.diff(gray, axis=0))
        edge_density = (float(np.mean(edges_h > 30)) + float(np.mean(edges_v > 30))) / 2
        signals['edge_density'] = edge_density
        # Memes with text typically have edge_density 0.05-0.20
        signals['has_text_edges'] = 0.03 < edge_density < 0.25

        # 4. Color histogram — memes often have fewer dominant colors
        img_small = img.resize((50, 50))
        colors = img_small.getcolors(maxcolors=2500)
        if colors:
            num_colors = len(colors)
            signals['num_colors'] = num_colors
            # Memes: typically 100-800 unique colors; photos: 1500+
            signals['limited_palette'] = num_colors < 1000
        else:
            signals['num_colors'] = 2500
            signals['limited_palette'] = False

        # 5. High contrast text detection — look for very bright or very dark areas
        bright_pct = float(np.mean(gray > 240))
        dark_pct = float(np.mean(gray < 15))
        signals['bright_pct'] = bright_pct
        signals['dark_pct'] = dark_pct
        signals['has_contrast_text'] = bright_pct > 0.05 or dark_pct > 0.05

        # Compute meme score from signals
        meme_points = 0
        if signals['is_square_ish']:
            meme_points += 1
        if signals['has_solid_region']:
            meme_points += 2
        if signals['has_text_edges']:
            meme_points += 1
        if signals['limited_palette']:
            meme_points += 2
        if signals['has_contrast_text']:
            meme_points += 1

        # Score: 0-7 points → 0.0-1.0
        meme_likelihood = min(meme_points / 5.0, 1.0)
        signals['meme_likelihood'] = meme_likelihood
        signals['is_likely_meme'] = meme_likelihood > 0.5

        return signals
    except Exception as e:
        print(f'[Image] Meme feature detection error: {e}')
        return {'meme_likelihood': 0.5, 'is_likely_meme': False}


class ImageAnalyzer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
            cls._instance._clip_available = False
        return cls._instance

    def _load(self):
        if self._loaded:
            return
        try:
            from transformers import CLIPModel, CLIPTokenizer, CLIPImageProcessor
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            # Load components separately (more reliable than CLIPProcessor)
            self.tokenizer = CLIPTokenizer.from_pretrained(MODEL_NAME)
            self.image_processor = CLIPImageProcessor.from_pretrained(MODEL_NAME)
            self.model = CLIPModel.from_pretrained(MODEL_NAME)
            self.model.to(self.device)
            self.model.eval()
            self._clip_available = True
            self._loaded = True
            print('[Image] CLIP model loaded successfully')
        except Exception as e:
            print(f'[Image] CLIP not available ({e}), using visual+OCR fallback')
            self._clip_available = False
            self._loaded = True

    def _clip_classify(self, image, prompts_a, prompts_b):
        """Return probability that image matches prompts_a vs prompts_b."""
        all_prompts = prompts_a + prompts_b
        text_inputs = self.tokenizer(all_prompts, padding=True, return_tensors='pt',
                                     truncation=True, max_length=77)
        image_inputs = self.image_processor(images=image, return_tensors='pt')
        with torch.no_grad():
            text_features = self.model.get_text_features(
                input_ids=text_inputs['input_ids'].to(self.device),
                attention_mask=text_inputs['attention_mask'].to(self.device),
            )
            image_features = self.model.get_image_features(
                pixel_values=image_inputs['pixel_values'].to(self.device),
            )
            # Normalize
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            # Cosine similarity (scaled by CLIP's logit_scale)
            logit_scale = self.model.logit_scale.exp()
            logits = (image_features @ text_features.T * logit_scale)[0]
        probs = F.softmax(logits, dim=0).cpu().numpy()
        a_mass = float(probs[:len(prompts_a)].sum())
        b_mass = float(probs[len(prompts_a):].sum())
        total = a_mass + b_mass
        return (a_mass / total) if total > 0 else 0.5

    def analyze(self, image_path: str) -> dict:
        self._load()

        # Always run meme feature detection (no ML needed)
        features = _detect_meme_features(image_path)
        meme_likelihood = features.get('meme_likelihood', 0.5)
        is_likely_meme = features.get('is_likely_meme', False)
        print(f'[Image] Visual features: meme_likelihood={meme_likelihood:.2f} is_meme={is_likely_meme}')

        # Try OCR
        ocr_text = _try_ocr(image_path)
        ocr_score = 0.5
        ocr_conf = 0.0
        if ocr_text and len(ocr_text) > 10:
            try:
                from analyzer.ml.rule_based_analyzer import analyze_rule_based
                rb = analyze_rule_based(ocr_text)
                ocr_score = rb['score']
                ocr_conf = rb['confidence']
                print(f'[Image OCR] text="{ocr_text[:80]}" score={ocr_score:.3f} conf={ocr_conf:.3f}')
            except Exception:
                pass
        has_ocr = ocr_conf > 0.1

        # Try CLIP if available
        clip_score = 0.5
        if self._clip_available:
            try:
                image = Image.open(image_path).convert('RGB')
                MEME_P = ['a funny meme', 'a meme with text', 'a reaction meme',
                          'a motivational poster', 'a comic image']
                REAL_P = ['a landscape photo', 'a portrait photo', 'a product photo',
                          'a news photo', 'a selfie']
                clip_score = self._clip_classify(image, MEME_P, REAL_P)
                print(f'[Image CLIP] meme_clip_score={clip_score:.3f}')
            except Exception as e:
                print(f'[Image CLIP] Error: {e}')

        # ── Final score computation ───────────────────────────────────────
        # Combine all available signals
        if has_ocr:
            # OCR found text — strongest signal
            if is_likely_meme or meme_likelihood > 0.4:
                # Meme with readable text
                final = 0.45 * ocr_score + 0.30 * (0.35 + meme_likelihood * 0.35) + 0.25 * clip_score
            else:
                final = 0.60 * ocr_score + 0.40 * clip_score
        elif is_likely_meme:
            # Detected as meme visually but couldn't read text
            meme_signal = 0.40 + meme_likelihood * 0.30  # 0.50→0.55, 1.0→0.70
            if self._clip_available:
                final = 0.50 * meme_signal + 0.50 * clip_score
            else:
                final = meme_signal
        elif ocr_text:
            # Some OCR text but low confidence — still use it mildly
            final = 0.40 * ocr_score + 0.30 * (0.35 + meme_likelihood * 0.35) + 0.30 * clip_score
        else:
            # No OCR, not detected as meme
            if self._clip_available:
                final = clip_score
            else:
                # No signals at all — use meme feature detection only
                final = 0.35 + meme_likelihood * 0.30

        confidence = round(abs(final - 0.5) * 200, 1)
        confidence = min(max(confidence, 1.0), 99.9)

        print(f'[Image] FINAL: score={final:.3f} conf={confidence:.1f}% '
              f'meme={meme_likelihood:.2f} ocr="{ocr_text[:40]}" clip={clip_score:.3f}')

        return {
            'score': round(final, 4),
            'confidence': round(confidence, 2),
            'is_meme': is_likely_meme,
            'meme_likelihood': round(meme_likelihood, 4),
            'ocr_text': ocr_text[:100] if ocr_text else '',
            'method': 'clip+visual+ocr' if self._clip_available else 'visual+ocr',
        }
