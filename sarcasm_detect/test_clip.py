import os, sys

# Test 1: CLIP loading with separate components
print('=== Test 1: CLIP loading ===')
try:
    from transformers import CLIPModel, CLIPTokenizer, CLIPImageProcessor
    print('Imports OK')
    tokenizer = CLIPTokenizer.from_pretrained('openai/clip-vit-base-patch32')
    print('Tokenizer: OK')
    processor = CLIPImageProcessor.from_pretrained('openai/clip-vit-base-patch32')
    print('Image Processor: OK')
except Exception as e:
    print(f'CLIP FAILED: {e}')

# Test 2: Pytesseract
print()
print('=== Test 2: Pytesseract ===')
try:
    import pytesseract
    print(f'pytesseract path: {pytesseract.pytesseract.tesseract_cmd}')
    version = pytesseract.get_tesseract_version()
    print(f'Tesseract version: {version}')
except Exception as e:
    print(f'Tesseract FAILED: {e}')

# Test 3: Check common Tesseract paths
print()
print('=== Test 3: Tesseract binary ===')
import shutil
paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Users\arati\AppData\Local\Programs\Tesseract-OCR\tesseract.exe',
]
for p in paths:
    print(f'{p}: {os.path.exists(p)}')
tesseract_in_path = shutil.which('tesseract')
print(f'tesseract in PATH: {tesseract_in_path}')
