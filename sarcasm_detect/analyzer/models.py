from django.db import models
import uuid

class SarcasmAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    text_content = models.TextField(blank=True)
    has_image = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Analysis {self.id} @ {self.created_at:%Y-%m-%d %H:%M}'


class ImageInput(models.Model):
    analysis = models.OneToOneField(SarcasmAnalysis, on_delete=models.CASCADE, related_name='image_input')
    image_file = models.ImageField(upload_to='images/')

class ModalityResult(models.Model):
    MODALITY_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('emoji', 'Emoji'),
        ('claude', 'Claude AI'),
    ]
    analysis = models.ForeignKey(SarcasmAnalysis, on_delete=models.CASCADE, related_name='modality_results')
    modality = models.CharField(max_length=10, choices=MODALITY_CHOICES)
    score = models.FloatField()   # 0.0 = not sarcastic, 1.0 = sarcastic
    confidence = models.FloatField(default=0.0)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('analysis', 'modality')

class SarcasmResult(models.Model):
    analysis = models.OneToOneField(SarcasmAnalysis, on_delete=models.CASCADE, related_name='result')
    is_sarcastic = models.BooleanField()
    confidence = models.FloatField()   # 0–100 %
    reasoning = models.TextField(blank=True)
    text_score = models.FloatField(default=0.0)
    image_score = models.FloatField(default=0.0)
    emoji_score = models.FloatField(default=0.0)
    claude_score = models.FloatField(default=0.0)

    def __str__(self):
        verdict = 'Sarcastic' if self.is_sarcastic else 'Not Sarcastic'
        return f'{verdict} ({self.confidence:.1f}%)'
