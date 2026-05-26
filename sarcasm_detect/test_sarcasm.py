#!/usr/bin/env python
"""
Test script to validate sarcasm detection with 10 test cases.
Run from sarcasm_detect directory: python test_sarcasm.py
"""
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sarcasm_detect.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from analyzer.ml.text_analyzer import TextAnalyzer
from analyzer.ml.emoji_analyzer import EmojiAnalyzer
from analyzer.ml.fusion import FusionLayer

# 10 Test cases: (text, expected_sarcastic, description)
TEST_CASES = [
    # === SARCASTIC (5 cases) ===
    ("Oh great, another meeting that could have been an email", True, "Classic 'oh great' sarcasm"),
    ("Yeah right, like that's ever going to happen", True, "'Yeah right' dismissive"),
    ("Thanks for nothing, really appreciate your help 🙄", True, "Thanks for nothing + eye roll"),
    ("What a surprise, the bus is late again", True, "What a surprise irony"),
    ("I love how you always show up on time 😒", True, "Love how + unamused emoji"),
    
    # === NOT SARCASTIC (5 cases) ===
    ("I really enjoyed the movie, it was fantastic!", False, "Genuine positive review"),
    ("Thank you for your help, I appreciate it", False, "Sincere gratitude"),
    ("The weather is beautiful today", False, "Simple factual statement"),
    ("Great job on the presentation, well done!", False, "Sincere praise"),
    ("I'm excited about the upcoming vacation", False, "Genuine excitement"),
]

# Additional complex test cases
COMPLEX_CASES = [
    # Subtle sarcasm
    ("Sure, because working overtime without pay is such a privilege", True, "Subtle workplace sarcasm"),
    ("Oh wow, you figured that out all by yourself? 👏", True, "Condescending sarcasm"),
    ("My favorite part of Monday is definitely the 6am alarm", True, "Subtle Monday sarcasm"),
    ("Not like I had better things to do anyway", True, "'Not like I' dismissive"),
    
    # Tricky non-sarcastic
    ("This is actually a great idea, let's implement it!", False, "Genuine enthusiasm"),
    ("I'm genuinely impressed by your progress", False, "Sincere compliment"),
    ("The sunset was absolutely beautiful", False, "Nature appreciation"),
    ("Congratulations on your promotion! 🎉", False, "Sincere congratulations"),
    
    # Emojis can flip meaning
    ("Best day ever! 😍", False, "Positive with heart eyes"),
    ("Best day ever 🙄", True, "Sarcastic with eye roll"),
]

def run_tests():
    print("\n" + "="*80)
    print("SARCASM DETECTION TEST - Loading models...")
    print("="*80)
    
    text_analyzer = TextAnalyzer()
    emoji_analyzer = EmojiAnalyzer()
    fusion = FusionLayer()
    
    all_cases = TEST_CASES + COMPLEX_CASES
    
    print("\n" + "="*80)
    print(f"RUNNING {len(all_cases)} TEST CASES (10 basic + {len(COMPLEX_CASES)} complex)")
    print("="*80 + "\n")
    
    correct = 0
    total = len(all_cases)
    results = []
    
    for i, (text, expected, desc) in enumerate(all_cases, 1):
        scores = {}
        details = {}
        
        # Text analysis
        print(f"\n--- Test {i}: {desc} ---")
        text_result = text_analyzer.analyze(text)
        scores['text'] = text_result['score']
        details['text'] = text_result
        
        # Emoji analysis
        emoji_result = emoji_analyzer.analyze(text)
        if emoji_result.get('confidence', 0) > 0:
            scores['emoji'] = emoji_result['score']
            details['emoji'] = emoji_result
        
        # Fusion (without Claude since no API key)
        result = fusion.fuse(scores, source_text=text)
        predicted = result['is_sarcastic']
        confidence = result['confidence']
        weighted_score = result['weighted_score']
        
        # Check if correct
        is_correct = predicted == expected
        if is_correct:
            correct += 1
            status = "✓ PASS"
        else:
            status = "✗ FAIL"
        
        results.append({
            'test': i,
            'text': text,
            'expected': expected,
            'predicted': predicted,
            'confidence': confidence,
            'correct': is_correct,
            'scores': scores,
            'weighted_score': weighted_score,
        })
        
        print(f"\nTest {i}: {status}")
        print(f"  Text: \"{text[:65]}{'...' if len(text) > 65 else ''}\"")
        print(f"  Expected:  {'SARCASTIC' if expected else 'NOT SARCASTIC'}")
        print(f"  Predicted: {'SARCASTIC' if predicted else 'NOT SARCASTIC'} "
              f"(score: {weighted_score:.3f}, confidence: {confidence:.1f}%)")
        print(f"  Modality Scores: text={scores.get('text', 0):.3f}", end="")
        if 'emoji' in scores:
            print(f", emoji={scores.get('emoji', 0):.3f}", end="")
        print()
        
        if text_result.get('matched_phrases'):
            print(f"  Matched Phrases: {text_result['matched_phrases'][:3]}")
    
    # Summary
    print("\n" + "="*80)
    print(f"SUMMARY: {correct}/{total} tests passed ({100*correct/total:.0f}%)")
    print("="*80)
    
    print("\n--- Results Table ---")
    print(f"{'#':<3} {'Status':<8} {'Expected':<15} {'Predicted':<15} {'Score':<8} {'Conf':<8}")
    print("-"*60)
    for r in results:
        status = "PASS" if r['correct'] else "FAIL"
        exp = "Sarcastic" if r['expected'] else "Not Sarcastic"
        pred = "Sarcastic" if r['predicted'] else "Not Sarcastic"
        print(f"{r['test']:<3} {status:<8} {exp:<15} {pred:<15} {r['weighted_score']:<8.3f} {r['confidence']:<8.1f}%")
    
    print("\n" + "="*80)
    
    if correct < total:
        print("\nFailed tests need investigation:")
        for r in results:
            if not r['correct']:
                print(f"  - Test {r['test']}: \"{r['text'][:50]}...\"")
    
    return correct == total

if __name__ == '__main__':
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nError running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
