#!/usr/bin/env bash
# scripts/install_wan.sh
set -e

echo "=== GenOTT WAN Backend Dependency Detector & Installer ==="

# Check Python
if command -v python3 &>/dev/null; then
    echo "[✓] Python 3 present: $(python3 --version)"
else
    echo "[!] Python 3 not found. Please install Python 3.10+."
    exit 1
fi

# Check PyTorch & CUDA
python3 -c "
import torch
print(f'[✓] PyTorch version: {torch.__version__}')
if torch.cuda.is_available():
    print(f'[✓] CUDA available: {torch.cuda.get_device_name(0)}')
else:
    print('[!] CUDA acceleration not detected. CPU fallback will be utilized.')
" 2>/dev/null || echo "[!] PyTorch not installed in environment."

# Check Flash Attention & xFormers
python3 -c "
try:
    import flash_attn
    print('[✓] Flash Attention installed.')
except ImportError:
    print('[i] Flash Attention not installed (optional performance boost).')

try:
    import xformers
    print('[✓] xFormers installed.')
except ImportError:
    print('[i] xFormers not installed (optional memory optimization).')
" 2>/dev/null || true

echo "=== System check completed. Preparing third_party/wan workspace ==="
mkdir -p third_party/wan models/wan
echo "[✓] WAN environment setup finished."
