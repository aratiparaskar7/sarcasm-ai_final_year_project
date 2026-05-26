from django.apps import AppConfig
import threading

class AnalyzerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analyzer'

    def ready(self):
        # Warm up ML models in a background thread (only if torch is available)
        def warmup():
            try:
                import torch  # noqa — check torch available before loading models
                from analyzer.ml.text_analyzer import TextAnalyzer
                from analyzer.ml.image_analyzer import ImageAnalyzer
                TextAnalyzer()
                ImageAnalyzer()
                print('[Warmup] ML models loaded.')
            except ImportError:
                print('[Warmup] ML packages not installed; models will load on first request.')
            except Exception as e:
                print(f'[Warmup] Warning: {e}')
        threading.Thread(target=warmup, daemon=True).start()
