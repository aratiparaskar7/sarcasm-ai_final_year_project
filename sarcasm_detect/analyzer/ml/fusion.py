# Fusion layer: weighted vote across modalities (text, image, emoji, claude only)

DEFAULT_WEIGHTS = {
    'claude': 0.40,
    'text':   0.30,
    'image':  0.20,
    'emoji':  0.10,
}

# Emoji is language-agnostic → boost its weight when handling non-Latin text
MULTILINGUAL_WEIGHTS = {
    'claude': 0.35,
    'text':   0.20,  # reduced: ML model is English-biased
    'image':  0.20,
    'emoji':  0.25,  # boosted: universal signal
}

THRESHOLD = 0.50  # score > threshold → sarcastic


def _is_non_latin(text: str) -> bool:
    if not text:
        return False
    non_latin = sum(1 for c in text if ord(c) > 0x02FF)
    return non_latin > len(text) * 0.15


class FusionLayer:
    def fuse(self, scores: dict, source_text: str = '') -> dict:
        """
        scores: dict mapping modality name → float score (0=sincere, 1=sarcastic)
        source_text: original text (used to detect language for weight adjustment)
        Returns: {is_sarcastic, confidence, weighted_score, weights_used}
        """
        if not scores:
            return {'is_sarcastic': False, 'confidence': 0.0,
                    'weighted_score': 0.5, 'weights_used': {}}

        # Use boosted emoji weights for non-Latin languages (Hindi, Arabic, CJK, etc.)
        weight_table = MULTILINGUAL_WEIGHTS if _is_non_latin(source_text) else DEFAULT_WEIGHTS

        # Gather weights for present modalities and re-normalize
        raw_weights = {k: weight_table.get(k, 0.1) for k in scores}
        total_weight = sum(raw_weights.values())
        weights = {k: v / total_weight for k, v in raw_weights.items()}

        weighted_score = sum(scores[k] * weights[k] for k in scores)
        is_sarcastic = weighted_score > THRESHOLD

        # Confidence = distance from midpoint (0.5), scaled to 0-100%
        confidence = round(abs(weighted_score - 0.5) * 200, 1)
        confidence = min(max(confidence, 1.0), 99.9)

        return {
            'is_sarcastic': bool(is_sarcastic),
            'confidence': confidence,
            'weighted_score': round(float(weighted_score), 4),
            'weights_used': weights,
        }
