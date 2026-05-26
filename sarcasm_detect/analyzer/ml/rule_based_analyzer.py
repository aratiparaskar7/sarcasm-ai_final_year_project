"""
Rule-based sarcasm detector.
Works instantly with zero model downloads.
Used as primary detector when ML model is unavailable, and as a signal blended into text scoring.
"""
import re

# ── Exact phrase matches (lowercase, score = probability of sarcasm) ───────────
PHRASE_SCORES = {
    # Sarcastic admissions / contradictions
    "didn't want to come":       0.92,
    "didn't want to be here":    0.93,
    "didn't want to go":         0.88,
    "didn't want to attend":     0.88,
    "didn't want to":            0.80,
    "not like i wanted":         0.85,
    "not like i asked":          0.87,
    "not like i care":           0.85,
    "not like it matters":       0.82,
    "not like anyone":           0.78,
    "as if anyone cares":        0.88,
    "as if i care":              0.87,
    "as if that helps":          0.85,
    # Classic sarcastic openers
    "oh great":                  0.90,
    "oh wonderful":              0.88,
    "oh fantastic":              0.88,
    "oh perfect":                0.87,
    "oh brilliant":              0.88,
    "oh sure":                   0.82,
    "oh wow":                    0.72,
    "oh yeah":                   0.68,
    "oh totally":                0.78,
    "oh absolutely":             0.78,
    "oh of course":              0.82,
    "oh yes because":            0.85,
    # Enthusiastic sarcasm
    "yeah right":                0.95,
    "suuure":                    0.90,
    "suure":                     0.88,
    "riiiight":                  0.90,
    "riiight":                   0.88,
    "riight":                    0.85,
    "sure jan":                  0.93,
    "sure thing":                0.65,
    "totally fine":              0.80,
    "totally okay":              0.78,
    "absolutely fine":           0.72,
    "totally normal":            0.80,
    "totally not":               0.85,
    "definitely not":            0.75,
    "clearly":                   0.52,  # weak — kept but low
    # Thanks / acknowledgement sarcasm
    "thanks for nothing":        0.97,
    "thanks a lot":              0.75,
    "thanks for your help":      0.65,
    "thank you so much":         0.60,
    "wow thanks":                0.72,
    "gee thanks":                0.88,
    "oh thanks":                 0.75,
    # "Must be nice" patterns
    "must be nice":              0.88,
    "must be great":             0.85,
    "must be wonderful":         0.87,
    # "I love how" sarcastic
    "love how you":              0.82,
    "love how they":             0.80,
    "love how it":               0.78,
    "love when people":          0.80,
    "love that for":             0.78,
    # Surprise expressions (sarcastic)
    "what a surprise":           0.90,
    "what a shock":              0.90,
    "how surprising":            0.90,
    "how shocking":              0.90,
    "color me surprised":        0.95,
    "i'm so surprised":          0.87,
    "never would have guessed":  0.90,
    "who would have thought":    0.85,
    "who knew":                  0.78,
    # Self-aware sarcasm
    "not that i wanted to":      0.85,
    "not that i was invited":    0.90,
    "not that i care":           0.85,
    "not that it matters":       0.80,
    "not that anyone asked":     0.87,
    "not that you'd know":       0.85,
    # Obvious/real/actual sarcasm
    "real original":             0.85,
    "real creative":             0.85,
    "real helpful":              0.88,
    "real useful":               0.85,
    "really helpful":            0.72,
    "so helpful":                0.70,
    "so useful":                 0.70,
    "so original":               0.82,
    "so creative":               0.75,
    "so impressed":              0.72,
    "so funny":                  0.65,
    "so very helpful":           0.82,
    # Dismissive phrases (only keep ones that are genuinely sarcastic standalone)
    "whatsoever":                0.60,
    "because that makes sense":  0.92,
    "makes perfect sense":       0.82,
    "makes total sense":         0.82,
    "as always":                 0.62,
    "as usual":                  0.65,
    "same as always":            0.65,
    "right because":             0.80,
    "sure because":              0.82,
    # News headline sarcasm phrases
    "who could have guessed":    0.92,
    "who could have known":      0.90,
    "who would have thought":    0.88,
    "shocking news":             0.75,
    "in a shocking turn":        0.80,
    "totally didn't see that coming": 0.93,
    "didn't see that coming":    0.87,
    "never would have guessed":  0.92,
    "what a revelation":         0.88,
    "groundbreaking discovery":  0.65,  # slightly sarcastic in headlines
    # "Sure, I totally wanted to" type
    "totally wanted to":         0.85,
    "really wanted to spend":    0.80,
    "wanted to spend my":        0.75,
    "best way to spend":         0.72,
    # Social sarcasm
    "we don't deserve":          0.78,
    "i'm fine":                  0.60,  # weak
    "everything is fine":        0.72,
    "this is fine":              0.78,
    "perfectly fine":            0.68,
    "living my best life":       0.75,

    # ── Hindi sarcasm phrases (Devanagari script) ─────────────────────────
    "वाह":                        0.82,  # Wah! (ironic wow)
    "वाह वाह":                    0.90,  # Wah wah (very sarcastic applause)
    "क्या बात है":                0.85,  # What a thing! (sarcastic)
    "क्या खूब":                   0.87,  # How lovely (sarcastic)
    "क्या टैलेंट":                0.90,  # What talent (sarcastic)
    # NOTE: शाबाश below threshold alone (0.45) so sincere use doesn't trigger;
    #       but combined with other signals (बहुत खूब, emoji etc) it contributes
    "शाबाश":                      0.45,  # Well done — below threshold alone, only fires in combos
    "बहुत खूब":                   0.85,  # Very fine (ironic)
    # REMOVED "बहुत अच्छा" — too ambiguous, triggers on sincere "आज बहुत अच्छा दिन था"
    "हां हां":                    0.78,  # Yeah yeah (dismissive)
    "ज़रूर":                       0.44,  # Sure — below threshold alone; contributes in combos
    "बिल्कुल":                    0.40,  # Absolutely — very common, too risky alone
    "पागल":                       0.38,  # Crazy — only a weak signal
    "पैदाइशी":                    0.85,  # Born like this (insulting compliment)
    "बेशक":                       0.42,  # Of course — common word, weak signal
    "हद है":                      0.80,  # The limit (frustrated sarcasm)
    "कमाल है":                    0.82,  # Amazing (ironic)
    "कमाल कर दिया":               0.88,  # You did amazing (sarcastic)
    "अरे वाह":                    0.87,  # Oh wow (sarcastic)
    "अति सुंदर":                  0.80,  # Very beautiful (ironic)
    "लाजवाब":                     0.78,  # Incomparable (ironic)

    # ── Spanish sarcasm ────────────────────────────────────────────────────
    "qué sorpresa":               0.88,  # What a surprise
    "qué genial":                 0.85,  # How great
    "qué talento":                0.87,  # What talent
    "claro que sí":               0.75,  # Of course (sarcastic)
    "lo que faltaba":             0.82,  # That's all we needed
    "faltaba más":                0.80,  # Could it get worse
    "qué maravilla":              0.82,  # How wonderful (sarcastic)

    # ── French sarcasm ─────────────────────────────────────────────────────
    "quelle surprise":            0.88,  # What a surprise
    "bien sûr":                   0.70,  # Of course (sarcastic)
    "évidemment":                 0.65,  # Obviously
    "comme d'habitude":           0.68,  # As usual
    "bravo":                      0.70,  # Bravo (often sarcastic)

    # ── German sarcasm ─────────────────────────────────────────────────────
    "wie überraschend":           0.90,  # How surprising
    "natürlich":                  0.62,  # Naturally (sarcastic)
    "toll":                       0.72,  # Great (sarcastic in German)
    "was für ein talent":         0.88,  # What a talent

    # ── Portuguese sarcasm ─────────────────────────────────────────────────
    "que surpresa":               0.88,  # What a surprise
    "que talento":                0.87,  # What talent
    "claro":                      0.62,  # Of course
}

# ── Regex patterns (compiled for speed) ────────────────────────────────────────
RAW_PATTERNS = [
    # "Sorry I'm late, I didn't want to come" type
    (r"sorry\s+i.?m\s+late.{0,30}didn.?t\s+want",     0.95),
    (r"didn.?t\s+want\s+to\s+come(\s+at\s+all)?",      0.92),
    (r"didn.?t\s+want\s+to\s+(be|go|attend|show)",     0.90),
    # "Oh [positive word]" sarcasm
    (r"\boh[\s,!]+\b(great|wonderful|fantastic|brilliant|perfect|amazing|lovely|super|awesome)\b", 0.90),
    # "Wow so/very/such [adjective]" sarcasm
    (r"\bwow[\s,]+so\s+\w+",                           0.78),
    (r"\bwow[\s,]+very\s+\w+",                         0.78),
    # "Yeah right"
    (r"\byeah\s+right\b",                              0.95),
    # "Like I [verb]" dismissive
    (r"\blike\s+i\s+(care|needed|wanted|asked|said|was\s+going)\b", 0.80),
    # "Not that I [verb]" dismissive
    (r"\bnot\s+that\s+(i|anyone)\s+(care|asked|needed|wanted|would)\b", 0.85),
    # "Must be nice [to/that]"
    (r"\bmust\s+be\s+(so\s+)?(nice|great|wonderful|fun|easy|hard|difficult)\b", 0.87),
    # "Thanks for [nothing/everything]" sarcastic
    (r"\bthanks?\s+for\s+(nothing|everything\s+you.?ve\s+done|all\s+(your|the)\s+help)\b", 0.93),
    # Gee thanks / wow thanks
    (r"\b(gee|oh|wow)\s+thanks?\b",                   0.85),
    # "I'm so [emotion] right now"
    (r"\bi.?m\s+so\s+(excited|happy|glad|thrilled|delighted|pumped)\s+(right\s+now|about\s+this|about\s+that)\b", 0.78),
    # "What a surprise / shock"
    (r"\bwhat\s+a\s+(surprise|shock|shocker|revelation|twist)\b", 0.90),
    (r"\bhow\s+(surprising|shocking|unexpected|unbelievable)\b",  0.88),
    # "Color me surprised"
    (r"\bcolor\s+me\s+surprised\b",                    0.97),
    # "Because that makes [so much] sense"
    (r"\bbecause\s+that\s+(totally\s+|really\s+|so\s+)?makes\s+(so\s+much\s+|perfect\s+|total\s+)?sense\b", 0.92),
    # "Clearly [verb] [negative]"
    (r"\bclearly\s+\w+\s+(not|never|no\s+one|nobody|nothing)\b", 0.72),
    # "As if [pronoun/that/it]" — expanded
    (r"\bas\s+if\s+(i|you|they|he|she|we|anyone|that|it|this|we'd|they'd)\b", 0.78),
    # "Sure, because [statement]"
    (r"\bsure[,.]?\s+because\b",                       0.83),
    # "Right, because [statement]"
    (r"\bright[,.]?\s+because\b",                      0.82),
    # "I love how [someone does something negative]"
    (r"\bi\s+love\s+how\s+\w+\s+(always|never|still|just|only|somehow)\b", 0.82),
    # extended "not like" + verb
    (r"\bnot\s+like\s+(i|you|we|they|anyone|he|she)\s+(care|needed|wanted|asked|was|would|could|should)\b", 0.83),
    # "Wow [subject] is so [adjective]" — stretched sarcasm
    (r"\bwow,?\s+\w+\s+is\s+so\s+\w+",               0.65),
    # Repeated letters for sarcasm stress: "sooo", "soooo", "reeeally", "suuure"
    (r"\b\w*([a-z])\1{2,}\w*\b",                       0.72),
    # All-caps sarcasm phrases (REMOVED - was causing false positives on normal text)
    # "Not exactly [word]" — understatement sarcasm
    (r"\bnot\s+exactly\s+(a\s+)?\w+",                  0.65),
    # Congratulatory sarcasm: "Congratulations, you [did something obvious/bad]"
    (r"\bcongratulations?,?\s+you\b",                   0.75),
    # "Well done" only sarcastic when followed by negative context
    (r"\bwell\s+done\s+(for\s+(nothing|that|screwing|breaking|messing|ruining)|you\s+(really|finally|managed))\b", 0.78),
    # Ironic "enjoy" / "have fun"
    (r"\b(enjoy|have\s+fun)\s+(your|the|this|that)\b", 0.60),
    # "Sure, I totally [verb]ed to [place/thing]"
    (r"\bsure[,.]?\s+(i|we)\s+totally\b",              0.88),
    (r"\btotally\s+wanted\s+to\b",                     0.83),
    (r"\bwho\s+could\s+have\s+(guessed|known|predicted)\b", 0.92),
    (r"\btotally\s+didn.?t\s+see\s+that\s+coming\b",   0.93),
    (r"\bdidn.?t\s+see\s+that\s+coming\b",             0.88),
    # "Clearly [something happened] / [result]"
    (r"\bclearly\s+\w+\s+is\s+(not|never|no\s+one)\b", 0.78),
    # "Congratulations on [something bad]"
    (r"\bcongratulations?\s+on\b",                      0.72),
    # "Great job" only sarcastic with explicit sarcasm marker (really, totally, etc.)
    (r"\b(great|nice|brilliant|wonderful)\s+job[,!.]\s+(really|truly|seriously|not|totally)\b", 0.78),
    # "Oh I'm so [positive emotion]" with sarcastic doubt
    (r"\boh[,\s]+i.?m\s+so\s+(sure|glad|happy|excited|surprised|shocked)\b", 0.82),
    # "Totally [positive adj]" sarcastic intensifier
    (r"\btotally\s+(fine|okay|normal|cool|great|fantastic|amazing|perfect)\b", 0.80),
    # "Super [positive adj]" sarcasm
    (r"\bsuper\s+(helpful|useful|fun|great|awesome|easy|simple|obvious)\b", 0.78),
    # "Because that's [totally/so/just] [adjective]" sarcasm
    (r"\bbecause\s+that.?s\s+(totally|so|just|really|completely)\s+\w+\b", 0.82),
    # "Oh [really/sure/right/totally]" standalone
    (r"\boh[,\s]+(really|sure|right|totally|absolutely|definitely)\b", 0.78),
    # "How [adjective] of you" — sarcastic
    (r"\bhow\s+(kind|thoughtful|considerate|helpful|wonderful|great|nice)\s+of\s+you\b", 0.85),
    # ── Hindi regex patterns ───────────────────────────────────────────────
    # "वाह! क्या [noun] है" — ironic praise
    (r"वाह[\s!]*क्या\s+\w+\s+है",                      0.92),
    # "कमाल है / कमाल कर दिया"
    (r"कमाल\s+(है|कर\s+दिया|हो\s+गया)",               0.88),
    # "अरे वाह" — sarcastic wow
    (r"अरे\s+वाह",                                      0.87),
    # "क्या बात है" — what a thing
    (r"क्या\s+बात\s+है",                                0.85),
    # "हद है यार" / "हद हो गई"
    (r"हद\s+(है|हो\s+गई|हो\s+गए)",                    0.83),
    # "पागल हो" + "पैदाइशी" pattern — core sarcasm in given example
    (r"पागल.{0,20}पैदाइशी",                            0.95),
    (r"पैदाइशी\s+हो",                                   0.90),
    # "मुझे तो लगा था" — "I thought..." setup phrase (often precedes a sarcastic punchline)
    (r"मुझे\s+तो\s+लगा\s+था",                          0.72),
    # "शाबाश" in regex form (kept for context matching — same 0.45 effective score via phrase)
    # ── Cross-language emoji + marker combinations ─────────────────────────
    # Slow clap 👏 at end of sentence (strongly sarcastic)
    (r"[\w\s\u0900-\u097F]+👏\s*$",                    0.82),
    (r"👏\s*(😂|🙄|😒|😏)",                           0.88),
]

PATTERNS = [(re.compile(p, re.IGNORECASE), score) for p, score in RAW_PATTERNS]


def _is_non_latin(text: str) -> bool:
    """Returns True if text contains significant non-Latin script (Hindi, Arabic, CJK, etc.)."""
    non_latin = sum(1 for c in text if ord(c) > 0x02FF)
    return non_latin > len(text) * 0.15


def analyze_rule_based(text: str) -> dict:
    """Returns sarcasm score 0.0–1.0 based purely on rules. Fast, no model needed."""
    lower = text.lower()
    matched_phrases = []
    matched_patterns = []
    scores = []
    non_latin = _is_non_latin(text)

    # Phrase matching (works on original text for Unicode, lowercase for Latin)
    for phrase, score in PHRASE_SCORES.items():
        if phrase in lower or phrase in text:
            matched_phrases.append((phrase, score))
            scores.append(score)

    # Regex matching
    for pattern, score in PATTERNS:
        m = pattern.search(text)
        if m:
            matched_patterns.append((m.group(0)[:40], score))
            scores.append(score)

    if not scores:
        # Neutral 0.50 for all languages — don't bias toward non-sarcastic just because
        # no explicit patterns were found. Let ML decide; rule-based stays neutral.
        return {
            'score': 0.50,
            'confidence': 0.05,
            'method': 'rule_based',
            'matched_phrases': [],
            'matched_patterns': [],
            'non_latin': non_latin,
        }

    # Weight higher scores more (take top-3 average, but cap at max)
    scores.sort(reverse=True)
    top_scores = scores[:3]
    final_score = sum(top_scores) / len(top_scores)
    # Confidence grows with number of matches and their strength
    confidence = min(0.3 + 0.15 * len(scores) + 0.1 * (final_score - 0.5), 0.95)

    return {
        'score': round(final_score, 4),
        'confidence': round(confidence, 4),
        'method': 'rule_based',
        'matched_phrases': [p for p, _ in matched_phrases[:5]],
        'matched_patterns': [p for p, _ in matched_patterns[:5]],
    }


# ── Quick self-test ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    TEST_CASES = [
        # ════════════════════════════════════════════════════════════════════
        # 10 ENGLISH SARCASTIC
        # ════════════════════════════════════════════════════════════════════
        ("Oh great, another Monday!",                                          True),
        ("Yeah right, like that would ever work",                               True),
        ("Sure, because that totally makes sense",                              True),
        ("Not like I wanted to be here anyway",                                 True),
        ("Thanks for nothing, buddy",                                           True),
        ("I love how you always know best",                                     True),
        ("Must be nice being so perfect",                                       True),
        ("What a surprise, the meeting ran late again",                         True),
        ("Oh wow, so helpful. Truly.",                                          True),
        ("As if that would ever help",                                          True),  # fixed regex
        # ════════════════════════════════════════════════════════════════════
        # 10 ENGLISH NON-SARCASTIC
        # ════════════════════════════════════════════════════════════════════
        ("I had a wonderful day at the park",                                  False),
        ("The weather is beautiful today",                                      False),
        ("She worked hard and finally got promoted",                            False),
        ("Scientists discover new vaccine for malaria",                         False),
        ("I love spending time with my family",                                 False),
        ("The team won the championship last night",                            False),
        ("He smiled and thanked the audience warmly",                          False),
        ("It was a great movie, highly recommend it",                           False),
        ("She is very talented and hardworking",                               False),
        ("The presentation went really well today",                             False),
        # ════════════════════════════════════════════════════════════════════
        # 10 HINDI SARCASTIC
        # ════════════════════════════════════════════════════════════════════
        ("वाह! क्या टैलेंट है, तुम तो पैदाइशी हो!",                          True),
        ("अरे वाह! क्या बात है यार!",                                         True),
        ("वाह वाह! कमाल कर दिया!",                                            True),
        ("हद है यार, यही बचा था!",                                             True),
        ("शाबाश! बहुत खूब किया तुमने",                                        True),  # शाबाश+बहुत खूब combo
        ("हां हां, बिल्कुल सही बात है",                                       True),  # हां हां=0.78 alone
        ("क्या खूब! ऐसा काम तो तुम्हीं करते हो",                             True),
        ("लाजवाब! पहले कभी ऐसा नहीं सुना",                                   True),
        ("कमाल है! तुमसे यही उम्मीद थी",                                      True),
        ("मुझे तो लगा था तुम समझदार हो, पर तुम तो पैदाइशी हो!",             True),
        # ════════════════════════════════════════════════════════════════════
        # 10 HINDI NON-SARCASTIC
        # ════════════════════════════════════════════════════════════════════
        ("आज मौसम बहुत सुहावना है",                                           False),
        ("मुझे तुमसे बहुत प्यार है",                                          False),
        ("उसने बहुत मेहनत की और सफल हुआ",                                    False),
        ("आज का खाना बहुत स्वादिष्ट था",                                     False),
        ("वो एक बहुत अच्छे इंसान हैं",                                       False),
        ("मैं बहुत खुश हूं आज",                                               False),
        ("आज बहुत अच्छा दिन था",                                              False),  # was false+ before fix
        ("शाबाश बेटे, तुमने बहुत मेहनत की",                                  False),  # was false+ before fix
        ("बिल्कुल सही, तुमने अच्छा काम किया",                               False),  # was false+ before fix
        ("यह फिल्म बहुत पसंद आई, देखनी चाहिए",                              False),
        # ════════════════════════════════════════════════════════════════════
        # 10 ENGLISH + EMOJI SARCASTIC
        # ════════════════════════════════════════════════════════════════════
        ("Oh great, another Monday 🙄",                                        True),
        ("Yeah right, as if! 🤣",                                              True),
        ("Must be nice being the boss 😏",                                     True),
        ("Thanks for nothing 👍",                                              True),
        ("Not like I asked for this 🙃",                                       True),
        ("Because that totally makes sense 🙄",                               True),
        ("What a surprise, again 😒",                                          True),
        ("I love how you always have an excuse 😑",                            True),
        ("Sure thing 👏",                                                      True),
        ("Wow, so helpful today 🤦",                                           True),
        # ════════════════════════════════════════════════════════════════════
        # 10 HINDI + EMOJI SARCASTIC
        # ════════════════════════════════════════════════════════════════════
        ("वाह! क्या टैलेंट है! 👏😂",                                         True),
        ("अरे वाह! 🙄",                                                        True),
        ("शाबाश! बहुत खूब! 👏😒",                                             True),
        ("हद है यार 😤",                                                       True),
        ("कमाल है! 👏",                                                        True),
        ("वाह! सच में? 🙃",                                                    True),
        ("हां हां, ज़रूर 😏",                                                  True),
        ("बिल्कुल सही 😒",                                                     True),  # emoji rescues weak rule score
        ("क्या बात है 🙄",                                                     True),
        ("लाजवाब! 👏😂",                                                       True),
    ]

    # Note: emoji combos (rows 41-50) — rule_based alone can't see emoji_analyzer's score.
    # Those last 20 need full fusion (emoji_analyzer contributes separately in the web app).
    # Here we test rule_based alone, so emoji rows partially depend on fusion in production.
    EMOJI_ONLY_START = 50  # last 20 are text+emoji (emoji part tested separately)

    print(f"{'Text':<55} {'Exp':>4} {'Score':>6} {'Got':>5} {'OK':>3}")
    print("=" * 80)
    sections = [
        (0,  10, "English Sarcastic"),
        (10, 20, "English Non-Sarcastic"),
        (20, 30, "Hindi Sarcastic"),
        (30, 40, "Hindi Non-Sarcastic"),
        (40, 50, "English + Emoji (rule-based component)"),
        (50, 60, "Hindi + Emoji (rule-based component)"),
    ]
    correct = 0
    for start, end, label in sections:
        print(f"\n── {label} ──")
        section_correct = 0
        for text, expected in TEST_CASES[start:end]:
            result = analyze_rule_based(text)
            predicted = result['score'] > 0.5
            ok = predicted == expected
            if ok:
                correct += 1
                section_correct += 1
            icon = "✓" if ok else "✗"
            exp_lbl = "SARC" if expected else "SINC"
            got_lbl = "SARC" if predicted else "SINC"
            matches = (result['matched_phrases'] + result['matched_patterns'])[:2]
            print(f"  {text[:54]:<55} {exp_lbl:>4} {result['score']:>6.3f} {got_lbl:>5} {icon:>3}  {matches}")
        print(f"  Section: {section_correct}/{end-start}")
    print(f"\n{'='*80}")
    print(f"TOTAL ACCURACY: {correct}/{len(TEST_CASES)} = {correct/len(TEST_CASES)*100:.0f}%")
    print("(Text+emoji rows: rule-based component only — emoji boosts applied separately in fusion)")

