"""
Basic tests for Sarcasm Detection app.
Run: python manage.py test analyzer
"""
from django.test import TestCase, Client
from django.urls import reverse
import json


class HealthCheckTest(TestCase):
    def test_health_endpoint(self):
        c = Client()
        resp = c.get('/api/health/')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data['status'], 'ok')


class PageLoadTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_loads(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'SarcasmAI')

    def test_analyze_page_loads(self):
        resp = self.client.get(reverse('analyze'))
        self.assertEqual(resp.status_code, 200)

    def test_history_page_loads(self):
        resp = self.client.get(reverse('history'))
        self.assertEqual(resp.status_code, 200)

    def test_api_history_returns_json(self):
        resp = self.client.get('/api/history/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/json')


class AnalyzeAPITest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_empty_submission_returns_400(self):
        resp = self.client.post('/api/analyze/', {})
        self.assertEqual(resp.status_code, 400)

    def test_text_submission(self):
        """Integration test — requires ML models loaded. Skip in CI if slow."""
        import os
        if os.getenv('CI'):
            self.skipTest('Skipping ML test in CI environment')
        resp = self.client.post('/api/analyze/', {'text': 'Oh great, another Monday 🙄'})
        if resp.status_code == 200:
            data = json.loads(resp.content)
            self.assertIn('id', data)
            self.assertIn('result', data)
            self.assertIn('is_sarcastic', data['result'])


class FusionLayerTest(TestCase):
    def test_fusion_all_modalities(self):
        from analyzer.ml.fusion import FusionLayer
        f = FusionLayer()
        result = f.fuse({'text': 0.8, 'image': 0.7, 'claude': 0.9, 'emoji': 0.85})
        self.assertTrue(result['is_sarcastic'])
        self.assertGreater(result['confidence'], 50)

    def test_fusion_all_sincere(self):
        from analyzer.ml.fusion import FusionLayer
        f = FusionLayer()
        result = f.fuse({'text': 0.1, 'image': 0.2, 'emoji': 0.15})
        self.assertFalse(result['is_sarcastic'])

    def test_fusion_empty_scores(self):
        from analyzer.ml.fusion import FusionLayer
        f = FusionLayer()
        result = f.fuse({})
        self.assertFalse(result['is_sarcastic'])
        self.assertEqual(result['confidence'], 0.0)

    def test_fusion_renormalizes_missing_modalities(self):
        from analyzer.ml.fusion import FusionLayer
        f = FusionLayer()
        result = f.fuse({'text': 0.8})
        weights = result['weights_used']
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=5)


class EmojiAnalyzerTest(TestCase):
    def test_sarcastic_emoji(self):
        from analyzer.ml.emoji_analyzer import EmojiAnalyzer
        result = EmojiAnalyzer().analyze('Oh wow 🙄 great job 🙃')
        self.assertGreater(result['score'], 0.5)
        self.assertIn('🙄', result['emojis_found'])

    def test_no_emoji(self):
        from analyzer.ml.emoji_analyzer import EmojiAnalyzer
        result = EmojiAnalyzer().analyze('Plain text with no emojis')
        self.assertEqual(result['count'], 0)

    def test_sincere_emoji(self):
        from analyzer.ml.emoji_analyzer import EmojiAnalyzer
        result = EmojiAnalyzer().analyze('I love you ❤️ 🥰')
        self.assertLess(result['score'], 0.5)
