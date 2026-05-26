from django.contrib import admin
from .models import SarcasmAnalysis, ImageInput, ModalityResult, SarcasmResult

@admin.register(SarcasmAnalysis)
class SarcasmAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'has_image', 'get_verdict')
    list_filter = ('has_image', 'result__is_sarcastic')
    search_fields = ('text_content',)
    readonly_fields = ('id', 'created_at')

    def get_verdict(self, obj):
        try:
            return '🎭 Sarcastic' if obj.result.is_sarcastic else '✅ Sincere'
        except Exception:
            return '—'
    get_verdict.short_description = 'Verdict'

@admin.register(SarcasmResult)
class SarcasmResultAdmin(admin.ModelAdmin):
    list_display = ('analysis', 'is_sarcastic', 'confidence', 'claude_score', 'text_score')
    list_filter = ('is_sarcastic',)

@admin.register(ModalityResult)
class ModalityResultAdmin(admin.ModelAdmin):
    list_display = ('analysis', 'modality', 'score', 'confidence')
    list_filter = ('modality',)

admin.site.register(ImageInput)
