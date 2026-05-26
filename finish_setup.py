"""
One-command project finisher.
Run from: c:\\Final yr Project\\sarcasm_detect
  python ..\finish_setup.py
Or from: c:\\Final yr Project
  python finish_setup.py
"""
import subprocess, sys, os

# Work out project root
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.join(HERE, 'sarcasm_detect')
if not os.path.exists(os.path.join(PROJECT, 'manage.py')):
    PROJECT = HERE

os.chdir(PROJECT)
PY = sys.executable


def pip(*args):
    subprocess.run([PY, '-m', 'pip', 'install', '--quiet', *args], check=False)


def manage(*args):
    result = subprocess.run([PY, 'manage.py', *args])
    return result.returncode


print('\n' + '='*55)
print('  SarcasmAI — Project Setup')
print('='*55)

# ── Step 1: Core packages ─────────────────────────────────
print('\n[1/4] Installing core packages...')
pip('django>=4.2,<5.0')
pip('djangorestframework>=3.14')
pip('python-dotenv>=1.0')
pip('Pillow>=10.0')
pip('whitenoise>=6.6')
pip('anthropic>=0.25')
pip('emoji>=2.11')
pip('numpy>=2.0')
pip('protobuf>=4.25')
pip('sentencepiece>=0.1.99')
print('      Core packages done')

# ── Step 2: ML packages ───────────────────────────────────
print('\n[2/4] Installing ML packages (may take a few minutes)...')
pip('torch>=2.6', 'torchvision>=0.21')
pip('transformers>=4.40')
pip('soundfile>=0.12')
pip('opencv-python>=4.9')
pip('librosa>=0.10')
pip('scikit-learn>=1.4')
print('      ML packages done')

# ── Step 3: Database setup ────────────────────────────────
print('\n[3/4] Setting up database...')
mig_dir = os.path.join(PROJECT, 'analyzer', 'migrations')
os.makedirs(mig_dir, exist_ok=True)
init_file = os.path.join(mig_dir, '__init__.py')
if not os.path.exists(init_file):
    open(init_file, 'w').close()
manage('makemigrations', 'analyzer')
manage('migrate')
print('      Database ready')

# ── Step 4: Media/static dirs ─────────────────────────────
print('\n[4/4] Creating required directories...')
for d in ['media/images', 'media/audio', 'media/videos', 'staticfiles']:
    os.makedirs(os.path.join(PROJECT, d), exist_ok=True)
print('      Directories ready')

print('\nRunning Django system check...')
code = manage('check')

print('\n' + '='*55)
if code == 0:
    print('  SETUP COMPLETE!')
else:
    print('  Setup done with warnings (see above)')
print()
print('  Next: run the server with:')
print('    cd "c:\\Final yr Project\\sarcasm_detect"')
print('    python manage.py runserver')
print()
print('  Then open: http://localhost:8000/')
print('='*55 + '\n')
