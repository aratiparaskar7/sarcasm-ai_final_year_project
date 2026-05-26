import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from analyzer.ml.rule_based_analyzer import analyze_rule_based

MODEL_NAME = 'cardiffnlp/twitter-roberta-base-irony'

class TextAnalyzer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
            cls._instance._load_error = None
        return cls._instance

    def _load(self):
        if self._loaded:
            return
        if self._load_error:
            raise RuntimeError(f'TextAnalyzer failed to load: {self._load_error}')
        try:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
            self.model.to(self.device)
            self.model.eval()
            # Find the irony label index from model config
            id2label = self.model.config.id2label
            self.irony_idx = next(
                (int(k) for k, v in id2label.items() if 'irony' in v.lower() and 'non' not in v.lower()),
                1  # fallback to index 1
            )
            print(f'[TextAnalyzer] id2label={id2label}, using irony_idx={self.irony_idx}')
            self._loaded = True
        except Exception as e:
            self._load_error = str(e)
            raise

    def analyze(self, text: str) -> dict:
        # Always run rule-based first (instant, no downloads)
        rule_result = analyze_rule_based(text)
        rule_score = rule_result['score']
        rule_conf = rule_result.get('confidence', 0.0)
        print(f'[RuleBased] text="{text[:60]}" score={rule_score:.3f} conf={rule_conf:.2f} matches={rule_result["matched_phrases"] + rule_result["matched_patterns"]}')

        try:
            self._load()
            inputs = self.tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = self.model(**inputs).logits
            probs = F.softmax(logits, dim=-1)[0]
            irony_score = float(probs[self.irony_idx])
            non_irony_score = float(probs[1 - self.irony_idx])
            ml_confidence = float(probs.max())
            print(f'[TextAnalyzer ML] irony={irony_score:.3f} non_irony={non_irony_score:.3f}')

            # ── Dynamic blend: trust rule-based MORE when it found matches ─────
            # rule_conf ≈ 0.05 (no matches) → 90% ML, 10% rule (don't let 0.35 drag ML down)
            # rule_conf ≈ 0.50 (weak match)  → 65% ML, 35% rule
            # rule_conf ≈ 0.90 (strong match) → 40% ML, 60% rule (explicit sarcasm markers)
            rule_weight = min(rule_conf * 0.67, 0.60)  # 0→0, 0.5→0.33, 0.9→0.60
            ml_weight = 1.0 - rule_weight
            blended = ml_weight * irony_score + rule_weight * rule_score

            # If rule-based found strong explicit markers, allow them to override ML
            if rule_conf > 0.6 and rule_score > 0.7:
                # Strong explicit sarcasm signal → clamp blend upward
                blended = max(blended, rule_score * 0.85)

            confidence = min(ml_confidence * (1 - rule_weight) + rule_conf * rule_weight, 0.99)
            print(f'[TextAnalyzer] ml_w={ml_weight:.2f} rule_w={rule_weight:.2f} blended={blended:.3f} conf={confidence:.3f}')
            return {
                'score': round(blended, 4),
                'confidence': round(confidence, 4),
                'ml_score': round(irony_score, 4),
                'rule_score': round(rule_score, 4),
                'non_irony_prob': round(non_irony_score, 4),
                'irony_prob': round(irony_score, 4),
                'matched_phrases': rule_result['matched_phrases'],
            }
        except Exception as e:
            # ML unavailable — use rule-based alone
            print(f'[TextAnalyzer] ML failed ({e}), using rule-based only')
            return {
                'score': round(rule_score, 4),
                'confidence': round(rule_conf, 4),
                'ml_score': None,
                'rule_score': round(rule_score, 4),
                'matched_phrases': rule_result['matched_phrases'],
                'matched_patterns': rule_result['matched_patterns'],
                'method': 'rule_based_fallback',
            }

