from django import forms

ALLOWED_IMAGE = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
MAX_SIZE = 100 * 1024 * 1024  # 100 MB

class AnalyzeForm(forms.Form):
    text = forms.CharField(required=False, max_length=5000, widget=forms.Textarea)
    image = forms.ImageField(required=False)

    def clean_image(self):
        f = self.cleaned_data.get('image')
        if f:
            if f.content_type not in ALLOWED_IMAGE:
                raise forms.ValidationError('Unsupported image format.')
            if f.size > MAX_SIZE:
                raise forms.ValidationError('Image file too large (max 100 MB).')
        return f

    def clean(self):
        data = super().clean()
        if not data.get('text') and not data.get('image'):
            raise forms.ValidationError('Please provide at least one input (text or image).')
        return data
