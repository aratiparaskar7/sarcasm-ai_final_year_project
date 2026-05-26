import base64
import json
import traceback
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import SarcasmAnalysis, ImageInput, ModalityResult, SarcasmResult
from .forms import AnalyzeForm

@csrf_exempt
@require_http_methods(['POST'])
def api_analyze(request):
    form = AnalyzeForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({'error': form.errors}, status=400)

    text = form.cleaned_data.get('text', '')
    image_file = form.cleaned_data.get('image')

    analysis = SarcasmAnalysis.objects.create(
        text_content=text,
        has_image=bool(image_file),
    )

    if image_file:
        ImageInput.objects.create(analysis=analysis, image_file=image_file)

    try:
        result_data = _run_analysis(analysis, text, image_file)
    except Exception as e:
        tb = traceback.format_exc()
        print(f'[API Critical Error]\n{tb}')
        analysis.delete()
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'id': str(analysis.id), 'result': result_data})


def _safe_run(name, fn, fallback_score=0.5):
    """Run a modality analyzer and return result, or a safe fallback on error."""
    try:
        return fn()
    except Exception as e:
        tb = traceback.format_exc()
        print(f'[{name}] Error: {e}\n{tb}')
        return {
            'score': fallback_score,
            'confidence': 0.0,
            'error': str(e),
        }


def _run_analysis(analysis, text, image_file):
    from analyzer.ml.claude_analyzer import ClaudeAnalyzer
    from analyzer.ml.text_analyzer import TextAnalyzer
    from analyzer.ml.image_analyzer import ImageAnalyzer
    from analyzer.ml.emoji_analyzer import EmojiAnalyzer
    from analyzer.ml.fusion import FusionLayer

    scores = {}

    # ── Emoji (fast, no model) ─────────────────────────────────────────────
    if text:
        emoji_result = _safe_run('Emoji', lambda: EmojiAnalyzer().analyze(text))
        # Only add to fusion if confidence > 0 (emojis were actually found)
        if emoji_result.get('confidence', 0) > 0 and 'error' not in emoji_result:
            scores['emoji'] = emoji_result['score']
        ModalityResult.objects.update_or_create(
            analysis=analysis, modality='emoji',
            defaults={'score': emoji_result['score'], 'confidence': emoji_result.get('confidence', 0.0),
                      'details': {k: v for k, v in emoji_result.items() if _json_safe(v)}},
        )

    # ── Text (RoBERTa + rule-based fallback) ──────────────────────────────
    if text:
        text_result = _safe_run('Text', lambda: TextAnalyzer().analyze(text))
        # TextAnalyzer always returns a result now (rule-based fallback ensures this)
        # Only exclude if _safe_run itself caught an unexpected exception
        if 'error' not in text_result:
            scores['text'] = text_result['score']
        else:
            # Last resort: run rule-based directly
            from analyzer.ml.rule_based_analyzer import analyze_rule_based
            rb = analyze_rule_based(text)
            scores['text'] = rb['score']
            text_result = rb
        ModalityResult.objects.update_or_create(
            analysis=analysis, modality='text',
            defaults={'score': text_result['score'], 'confidence': text_result.get('confidence', 0.0),
                      'details': {k: v for k, v in text_result.items() if _json_safe(v)}},
        )

    # ── Image (CLIP) ───────────────────────────────────────────────────────
    print(f'[Debug] image_file={image_file}, has_image={analysis.has_image}')
    if image_file:
        try:
            img_path = analysis.image_input.image_file.path
            print(f'[Image] Starting analysis of: {img_path}')
        except Exception as e:
            print(f'[Image] Error getting path: {e}')
            img_path = None

        if img_path:
            image_result = _safe_run('Image', lambda: ImageAnalyzer().analyze(img_path))
            print(f'[Image] result={image_result}')
            if 'error' not in image_result:
                scores['image'] = image_result['score']
            ModalityResult.objects.update_or_create(
                analysis=analysis, modality='image',
                defaults={'score': image_result['score'], 'confidence': image_result.get('confidence', 0.0),
                          'details': {k: v for k, v in image_result.items() if _json_safe(v)}},
            )
    else:
        print('[Debug] No image file received')

    # ── Claude API ─────────────────────────────────────────────────────────
    image_b64 = None
    image_mime = None
    if image_file:
        try:
            with open(analysis.image_input.image_file.path, 'rb') as f:
                image_b64 = base64.b64encode(f.read()).decode()
            image_mime = analysis.image_input.image_file.name.rsplit('.', 1)[-1]
        except Exception:
            pass

    claude_result = _safe_run('Claude', lambda: ClaudeAnalyzer().analyze(text, image_b64, image_mime))
    # Only include Claude in fusion when it actually ran (confidence > 0)
    if claude_result.get('confidence', 0) > 0:
        scores['claude'] = claude_result['score']
    ModalityResult.objects.update_or_create(
        analysis=analysis, modality='claude',
        defaults={'score': claude_result['score'], 'confidence': claude_result.get('confidence', 0.0),
                  'details': {k: str(v) for k, v in claude_result.items()}},
    )

    # ── Fusion ─────────────────────────────────────────────────────────────
    final = FusionLayer().fuse(scores, source_text=text or '')
    confidence = min(final['confidence'], 99.9)

    # Log scores to Django terminal for debugging
    print(f'[Fusion] scores={scores} weighted={final.get("weighted_score")} '
          f'is_sarcastic={final["is_sarcastic"]} confidence={confidence:.1f}%')

    SarcasmResult.objects.update_or_create(
        analysis=analysis,
        defaults={
            'is_sarcastic': final['is_sarcastic'],
            'confidence': confidence,
            'reasoning': claude_result.get('reasoning', ''),
            'text_score': scores.get('text', 0.0),
            'image_score': scores.get('image', 0.0),
            'emoji_score': scores.get('emoji', 0.0),
            'claude_score': scores.get('claude', 0.0),
        }
    )

    return {
        'is_sarcastic': final['is_sarcastic'],
        'confidence': confidence,
        'reasoning': claude_result.get('reasoning', ''),
        'scores': scores,
    }


def _json_safe(v):
    """Return True if value is JSON-serializable."""
    try:
        json.dumps(v)
        return True
    except (TypeError, ValueError):
        return False


@require_http_methods(['GET'])
def api_result(request, analysis_id):
    try:
        from .serializers import SarcasmAnalysisSerializer
        analysis = SarcasmAnalysis.objects.get(id=analysis_id)
        serializer = SarcasmAnalysisSerializer(analysis)
        return JsonResponse(serializer.data)
    except SarcasmAnalysis.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
    except Exception as e:
        # DRF may not be installed; return basic JSON
        analysis = SarcasmAnalysis.objects.get(id=analysis_id)
        result = getattr(analysis, 'result', None)
        return JsonResponse({
            'id': str(analysis.id),
            'text_content': analysis.text_content,
            'result': {
                'is_sarcastic': result.is_sarcastic if result else None,
                'confidence': result.confidence if result else None,
            } if result else None
        })


@require_http_methods(['GET'])
def api_history(request):
    try:
        from .serializers import SarcasmAnalysisSerializer
        analyses = SarcasmAnalysis.objects.select_related('result').all()[:50]
        serializer = SarcasmAnalysisSerializer(analyses, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception:
        analyses = SarcasmAnalysis.objects.select_related('result').all()[:50]
        data = []
        for a in analyses:
            r = getattr(a, 'result', None)
            data.append({
                'id': str(a.id),
                'created_at': a.created_at.isoformat(),
                'text_content': a.text_content[:100],
                'result': {'is_sarcastic': r.is_sarcastic, 'confidence': r.confidence} if r else None,
            })
        return JsonResponse(data, safe=False)


@require_http_methods(['GET'])
def api_ablation(request, analysis_id):
    try:
        from analyzer.ml.fusion import FusionLayer
        analysis = SarcasmAnalysis.objects.get(id=analysis_id)
        modality_results = {mr.modality: mr.score for mr in analysis.modality_results.all()}

        ablation = {}
        fusion = FusionLayer()
        src = analysis.text_content or ''
        for modality in list(modality_results.keys()):
            subset = {k: v for k, v in modality_results.items() if k != modality}
            ablation[f'without_{modality}'] = fusion.fuse(subset, source_text=src)
        for modality in modality_results:
            ablation[f'only_{modality}'] = fusion.fuse({modality: modality_results[modality]}, source_text=src)

        return JsonResponse({'modality_scores': modality_results, 'ablation': ablation})
    except SarcasmAnalysis.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)


@csrf_exempt
@require_http_methods(['POST', 'DELETE'])
def api_delete(request, analysis_id):
    try:
        analysis = SarcasmAnalysis.objects.get(id=analysis_id)
        analysis.delete()
        return JsonResponse({'ok': True})
    except SarcasmAnalysis.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)


@require_http_methods(['GET'])
def api_health(request):
    return JsonResponse({'status': 'ok', 'version': '1.0.0'})
