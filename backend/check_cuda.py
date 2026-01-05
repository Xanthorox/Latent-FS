import torch

print("PyTorch CUDA Check")
print("=" * 50)
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"cuDNN version: {torch.backends.cudnn.version() if torch.cuda.is_available() else 'N/A'}")
print(f"Device count: {torch.cuda.device_count()}")

if torch.cuda.is_available():
    print(f"Current device: {torch.cuda.current_device()}")
    print(f"Device name: {torch.cuda.get_device_name(0)}")
    print(f"Device capability: {torch.cuda.get_device_capability(0)}")
else:
    print("\n⚠️ CUDA is NOT available!")
    print("Possible reasons:")
    print("1. PyTorch CPU-only version is installed")
    print("2. CUDA drivers not installed")
    print("3. GPU not detected")
