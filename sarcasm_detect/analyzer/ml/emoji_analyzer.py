import emoji

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
                'score': 0.5,
                'confidence': 0.0,   # confidence=0 → excluded from fusion
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
