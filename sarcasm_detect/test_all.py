"""Comprehensive sarcasm detection test suite."""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sarcasm_detect.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from analyzer.ml.text_analyzer import TextAnalyzer
from analyzer.ml.emoji_analyzer import EmojiAnalyzer
from analyzer.ml.claude_analyzer import ClaudeAnalyzer
from analyzer.ml.fusion import FusionLayer

PASS = 0
FAIL = 0

def test(label, score, expected_sarcastic, threshold=0.50):
    global PASS, FAIL
    is_sarc = score > threshold
    ok = is_sarc == expected_sarcastic
    icon = "✅" if ok else "❌"
    tag = "SARC" if is_sarc else "NOT "
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(f"  {icon} [{tag}] score={score:.3f} | {label}")
    return ok

print("=" * 70)
print("TEST 1: TEXT SARCASM (English)")
print("=" * 70)
ta = TextAnalyzer()
eng_tests = [
    ("Oh great, another Monday morning!", True),
    ("Yeah right, like that's ever gonna happen", True),
    ("Wow, what a surprise... not", True),
    ("Sure, because that worked SO well last time", True),
    ("Thanks for nothing, really appreciate it", True),
    ("Oh wonderful, my car broke down again", True),
    ("I just LOVE being stuck in traffic for 3 hours", True),
    ("What a brilliant idea, said no one ever", True),
    ("I had a great day at work today", False),
    ("The weather is nice and sunny", False),
    ("Thank you for helping me with this", False),
    ("I really enjoyed the movie last night", False),
    ("The food at that restaurant was delicious", False),
    ("Happy birthday! Hope you have a wonderful day", False),
]

for text, expected in eng_tests:
    r = ta.analyze(text)
    test(text[:60], r['score'], expected)

print()
print("=" * 70)
print("TEST 2: TEXT SARCASM (Hindi)")
print("=" * 70)
hindi_tests = [
    ("वाह! क्या टैलेंट है, मुझे तो लगा था तुम पागल हो, पर तुम तो पैदाइशी हो!", True),
    ("अरे वाह, कितने अच्छे दोस्त हो तुम, बिल्कुल काम के!", True),
    ("बहुत बढ़िया, और तारीफ करो अपनी!", True),
    ("शाबाश! बड़े काम की चीज हो तुम!", True),
    ("क्या बात है, दुनिया में तुमसे बड़ा कोई ज्ञानी नहीं!", True),
    ("आज मौसम बहुत अच्छा है", False),
    ("मुझे यह किताब बहुत पसंद आई", False),
    ("धन्यवाद आपकी मदद के लिए", False),
]

for text, expected in hindi_tests:
    r = ta.analyze(text)
    test(text[:60], r['score'], expected)

print()
print("=" * 70)
print("TEST 3: EMOJI ANALYSIS")
print("=" * 70)
ea = EmojiAnalyzer()
emoji_tests = [
    ("Great job 🙄😒", True),
    ("Oh sure 🙃👏", True),
    ("Love this 💀🤦", True),
    ("Amazing work 😏😤", True),
    ("Happy birthday! 🎉❤️", False),
    ("I love you 🥰😊", False),
    ("Beautiful day ✨😊", False),
    ("Congratulations! 🎉🎉🎉", False),
]

for text, expected in emoji_tests:
    r = ea.analyze(text)
    test(text, r['score'], expected)

print()
print("=" * 70)
print("TEST 4: TEXT + EMOJI FUSION (English)")
print("=" * 70)
fusion = FusionLayer()
text_emoji_en = [
    ("Oh great, another meeting 🙄😒", True),
    ("Sure, I totally believe you 🙃", True),
    ("Wow so impressive 👏👏💀", True),
    ("Thanks for the help 😤🤦", True),
    ("What a beautiful day! ☀️😊", False),
    ("Happy birthday! 🎉❤️🎂", False),
    ("I love this song! 😍🎵", False),
    ("Thank you so much! 🥰😊", False),
]

for text, expected in text_emoji_en:
    tr = ta.analyze(text)
    er = ea.analyze(text)
    scores = {'text': tr['score']}
    if er.get('confidence', 0) > 0:
        scores['emoji'] = er['score']
    fused = fusion.fuse(scores, source_text=text)
    test(text, fused['weighted_score'], expected)

print()
print("=" * 70)
print("TEST 5: TEXT + EMOJI FUSION (Hindi)")
print("=" * 70)
text_emoji_hi = [
    ("वाह क्या बात है 🙄😒", True),
    ("बहुत अच्छा काम किया 👏💀", True),
    ("शाबाश! बड़े काम के हो 🙃😤", True),
    ("अरे वाह, कमाल कर दिया! 🤦😏", True),
    ("बहुत खुशी हुई 😊❤️", False),
    ("जन्मदिन मुबारक 🎉🎂", False),
    ("बहुत अच्छा गाना है 😍🎵", False),
    ("शुक्रिया 🥰😊", False),
]

for text, expected in text_emoji_hi:
    tr = ta.analyze(text)
    er = ea.analyze(text)
    scores = {'text': tr['score']}
    if er.get('confidence', 0) > 0:
        scores['emoji'] = er['score']
    fused = fusion.fuse(scores, source_text=text)
    test(text, fused['weighted_score'], expected)

print()
print("=" * 70)
print("TEST 6: GEMINI API (Text-only)")
print("=" * 70)
ca = ClaudeAnalyzer()
claude_tests = [
    ("Oh wow, another brilliant idea from management", True),
    ("Sorry I'm late, I didn't want to come at all", True),
    ("The sunset was really beautiful today", False),
    ("I appreciate your hard work on this project", False),
]

for text, expected in claude_tests:
    r = ca.analyze(text)
    if r.get('confidence', 0) == 0 and 'not configured' in r.get('reasoning', ''):
        print(f"  ⚠️  Gemini API not working: {r.get('reasoning', '')}")
        break
    test(text[:60], r['score'], expected)

print()
print("=" * 70)
print(f"RESULTS: {PASS} passed, {FAIL} failed out of {PASS+FAIL} tests")
print("=" * 70)
