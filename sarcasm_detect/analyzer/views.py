from django.shortcuts import render, get_object_or_404
from .models import SarcasmAnalysis, SarcasmResult

def index(request):
    total = SarcasmAnalysis.objects.count()
    sarcastic = SarcasmResult.objects.filter(is_sarcastic=True).count()
    return render(request, 'analyzer/index.html', {'total_analyses': total, 'sarcastic_count': sarcastic})

def analyze_view(request):
    return render(request, 'analyzer/analyze.html')

def result_view(request, analysis_id):
    analysis = get_object_or_404(SarcasmAnalysis, id=analysis_id)
    result = get_object_or_404(SarcasmResult, analysis=analysis)
    modality_results = analysis.modality_results.all()
    return render(request, 'analyzer/result.html', {
        'analysis': analysis,
        'result': result,
        'modality_results': modality_results,
    })

def history_view(request):
    analyses = SarcasmAnalysis.objects.select_related('result').all()[:100]
    return render(request, 'analyzer/history.html', {'analyses': analyses})
