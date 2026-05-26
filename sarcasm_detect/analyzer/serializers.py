from rest_framework import serializers
from .models import SarcasmAnalysis, SarcasmResult, ModalityResult

class ModalityResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModalityResult
        fields = ['modality', 'score', 'confidence', 'details']

class SarcasmResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SarcasmResult
        fields = ['is_sarcastic', 'confidence', 'reasoning',
                  'text_score', 'image_score', 'emoji_score', 'claude_score']

class SarcasmAnalysisSerializer(serializers.ModelSerializer):
    result = SarcasmResultSerializer(read_only=True)
    modality_results = ModalityResultSerializer(many=True, read_only=True)

    class Meta:
        model = SarcasmAnalysis
        fields = ['id', 'created_at', 'text_content',
                  'has_image', 'result', 'modality_results']
