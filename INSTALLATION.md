# Detailed Installation Guide

This guide provides step-by-step instructions for setting up SarcasmAI on your system.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Windows Installation](#windows-installation)
3. [macOS Installation](#macos-installation)
4. [Linux Installation](#linux-installation)
5. [GPU Setup (NVIDIA)](#gpu-setup-nvidia)
6. [Troubleshooting](#troubleshooting)
7. [Verification](#verification)

---

## System Requirements

### Minimum Specifications

- **OS**: Windows 10+, macOS 10.13+, or Linux (Ubuntu 18.04+)
- **Python**: 3.11 or higher
- **RAM**: 8 GB minimum (16 GB recommended)
- **Disk Space**: 3 GB for ML models + project files
- **Internet**: Required for first-run model downloads

### Recommended Specifications

- **RAM**: 16+ GB
- **GPU**: NVIDIA (2GB+ VRAM) for faster inference
- **SSD**: For faster model loading

### Verify Python Installation

```bash
python --version    # Should show Python 3.11+
pip --version       # Should show pip 20.0+
```

> **Update Python**: Visit https://www.python.org/downloads/ if needed

---

## Windows Installation

### Step 1: Clone Repository

```bash
# Open Command Prompt or PowerShell
git clone https://github.com/YOUR_USERNAME/sarcasm-ai.git
cd sarcasm-ai
```

> **Don't have Git?** Download from https://git-scm.com/

### Step 2: Create Virtual Environment

```cmd
# Create environment
python -m venv venv

# Activate environment
venv\Scripts\activate

# You should see (venv) at the start of command line
```

### Step 3: Navigate to Project

```cmd
cd sarcasm_detect
```

### Step 4: Upgrade pip

```cmd
python -m pip install --upgrade pip
```

### Step 5: Install Dependencies (CPU)

For systems without NVIDIA GPU:

```cmd
pip install torch torchvision
pip install -r requirements.txt
```

**Installation time**: 5-10 minutes (depends on internet speed)

### Step 6: Install Dependencies (GPU)

For NVIDIA GPU systems, check your CUDA version first:

```cmd
nvidia-smi
```

**For CUDA 12.4** (Most common for modern GPUs):
```cmd
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
```

**For CUDA 11.8**:
```cmd
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

### Step 7: Set Up Environment

```cmd
# Copy template
copy .env.example .env

# Edit .env in Notepad or your editor
notepad .env
```

**Minimum configuration for `.env`**:
```ini
SECRET_KEY=your-random-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 8: Initialize Database

```cmd
python manage.py makemigrations analyzer
python manage.py migrate
```

### Step 9: Create Admin Account (Optional)

```cmd
python manage.py createsuperuser
```

Follow the prompts to create your admin account.

### Step 10: Run Development Server

```cmd
python manage.py runserver
```

**Success Message**:
```
Starting development server at http://127.0.0.1:8000/
```

Open **http://localhost:8000** in your browser.

---

## macOS Installation

### Step 1: Install Homebrew (if needed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/sarcasm-ai.git
cd sarcasm-ai
```

### Step 3: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 4: Navigate to Project

```bash
cd sarcasm_detect
```

### Step 5: Upgrade pip

```bash
python -m pip install --upgrade pip
```

### Step 6: Install Dependencies (CPU)

```bash
pip install torch torchvision
pip install -r requirements.txt
```

### Step 7: Install Dependencies (Apple Silicon Macs - M1/M2/M3)

For best performance on Apple Silicon:

```bash
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu
pip install -r requirements.txt
```

### Step 8: Set Up Environment

```bash
# Copy template
cp .env.example .env

# Edit .env in your editor
nano .env
```

Add minimum configuration:
```ini
SECRET_KEY=your-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

Press `Ctrl+O`, then `Enter` to save, then `Ctrl+X` to exit nano.

### Step 9: Initialize Database

```bash
python manage.py makemigrations analyzer
python manage.py migrate
```

### Step 10: Create Admin Account

```bash
python manage.py createsuperuser
```

### Step 11: Run Server

```bash
python manage.py runserver
```

Open **http://localhost:8000** in your browser.

---

## Linux Installation

### Ubuntu/Debian-based Systems

#### Step 1: Install System Dependencies

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev git
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/sarcasm-ai.git
cd sarcasm-ai
```

#### Step 3: Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
```

#### Step 4: Navigate to Project

```bash
cd sarcasm_detect
```

#### Step 5: Upgrade pip

```bash
python -m pip install --upgrade pip
```

#### Step 6: Install Dependencies

For CPU:
```bash
pip install torch torchvision
pip install -r requirements.txt
```

For CUDA 12.4:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
```

#### Step 7: Environment Setup

```bash
cp .env.example .env
nano .env
```

Add required variables, save with `Ctrl+O`, exit with `Ctrl+X`.

#### Step 8: Database Setup

```bash
python manage.py makemigrations analyzer
python manage.py migrate
```

#### Step 9: Create Admin User

```bash
python manage.py createsuperuser
```

#### Step 10: Run Server

```bash
python manage.py runserver 0.0.0.0:8000
```

Access at **http://localhost:8000**

---

## GPU Setup (NVIDIA)

### Prerequisites

- NVIDIA GPU with CUDA Compute Capability 3.5+
- NVIDIA drivers installed (`nvidia-smi` should work)
- CUDA toolkit and cuDNN

### Step 1: Verify GPU

```bash
nvidia-smi
```

**Output should show**:
- GPU name
- Driver version
- CUDA version

### Step 2: Determine CUDA Version

From `nvidia-smi` output, note the CUDA version shown. Common versions:
- CUDA 12.4 (Latest, Recommended)
- CUDA 12.1
- CUDA 11.8

### Step 3: Install PyTorch with GPU Support

**For CUDA 12.4**:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
```

**For CUDA 11.8**:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Step 4: Verify GPU Detection

```bash
python
>>> import torch
>>> torch.cuda.is_available()
True
>>> torch.cuda.get_device_name(0)
'NVIDIA GeForce GTX 1660'
>>> exit()
```

If `True`, GPU setup is successful!

### Step 5: Continue with Standard Setup

Follow regular installation steps. Models will automatically use GPU for inference.

---

## Troubleshooting

### Issue: "Python command not found"

**Solution**:
- **Windows**: Use `python` or `py`
- **macOS/Linux**: Use `python3`
- Install Python from https://www.python.org/

### Issue: "pip: command not found"

**Solution**:
```bash
python -m pip install --upgrade pip
```

### Issue: Virtual environment not activating

**Windows**:
```cmd
venv\Scripts\activate
```

**macOS/Linux**:
```bash
source venv/bin/activate
```

### Issue: "ModuleNotFoundError" when running server

**Solution**: Ensure virtual environment is activated. You should see `(venv)` in terminal.

```bash
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### Issue: Slow model download on first run

**Solution**: This is normal. Models are ~1.3 GB total.
- Ensure good internet connection
- Be patient (10-30 minutes typical)
- Models are cached after download

### Issue: "CUDA out of memory"

**Solution**:
- Close other applications
- Reduce batch sizes in code
- Use CPU mode: `CUDA_VISIBLE_DEVICES=""` (Linux/macOS) or set `CUDA_VISIBLE_DEVICES=""` in .env
- Restart Python to clear memory

### Issue: Port 8000 already in use

**Solution**:
```bash
# Use different port
python manage.py runserver 8001
```

### Issue: "ImportError: No module named 'analyzer'"

**Solution**: Ensure you're in the `sarcasm_detect/` directory:
```bash
cd sarcasm_detect
python manage.py runserver
```

### Issue: Database migration errors

**Solution**:
```bash
# Reset migrations
python manage.py migrate analyzer zero
python manage.py makemigrations analyzer
python manage.py migrate
```

---

## Verification

### Test 1: Server Starts

```bash
cd sarcasm_detect
python manage.py runserver
```

✅ Should see: `Starting development server at http://127.0.0.1:8000/`

### Test 2: Web Interface Access

1. Open **http://localhost:8000** in browser
2. ✅ Should see landing page

### Test 3: Test API

```bash
curl -X POST http://localhost:8000/api/analyze/ \
  -F "text=Oh great, another meeting"
```

✅ Should return JSON response with `id` and `result` keys

### Test 4: Run Test Suite

```bash
python manage.py test analyzer
```

✅ Should show: `Ran X tests` with no failures

### Test 5: GPU Detection (if applicable)

```bash
python
>>> import torch
>>> print(torch.cuda.is_available())
```

✅ Should print `True` for GPU systems

---

## Next Steps

1. **Read README.md** for project overview
2. **Check API.md** for API documentation
3. **Explore the Web UI** at http://localhost:8000
4. **Review Project Structure** in README.md

---

## Support

For issues not covered here:
- Check GitHub Issues: https://github.com/YOUR_USERNAME/sarcasm-ai/issues
- Review Django docs: https://docs.djangoproject.com/
- Check PyTorch docs: https://pytorch.org/docs/

**Last Updated**: 2026-05-26
