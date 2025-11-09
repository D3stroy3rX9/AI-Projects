#!/usr/bin/env python3
"""
Download and verify Whisper models

Usage:
    python download_models.py --model base
    python download_models.py --model tiny
    python download_models.py --all
"""
import argparse
import sys
import time
import os


def download_whisper_model(model_name: str):
    """
    Download Whisper model

    Args:
        model_name: Model size (tiny, base, small, medium, large)
    """
    try:
        import whisper

        print("=" * 60)
        print(f"📥 Downloading Whisper model: {model_name}")
        print("=" * 60)

        # Model sizes
        model_sizes = {
            "tiny": "39 MB",
            "base": "74 MB",
            "small": "244 MB",
            "medium": "769 MB",
            "large": "1550 MB"
        }

        if model_name in model_sizes:
            print(f"   Size: ~{model_sizes[model_name]}")
            print(f"   Cache: {os.path.expanduser('~/.cache/whisper/')}")
            print()

        start_time = time.time()

        # Download model (automatically cached)
        model = whisper.load_model(model_name)

        download_time = time.time() - start_time

        print()
        print("=" * 60)
        print(f"✅ Model '{model_name}' downloaded successfully!")
        print(f"   Time: {download_time:.2f} seconds")
        print("=" * 60)

        # Verify model
        print("\n🔍 Verifying model...")
        model_info = {
            "model_name": model_name,
            "dims": model.dims,
            "loaded": model is not None
        }
        print(f"   Model dimensions: {model.dims}")
        print(f"   Status: {'✅ Ready' if model_info['loaded'] else '❌ Failed'}")

        return True

    except Exception as e:
        print(f"\n❌ Error downloading model '{model_name}': {e}")
        return False


def check_dependencies():
    """
    Check if required dependencies are installed
    """
    print("🔍 Checking dependencies...")

    dependencies = {
        "whisper": "openai-whisper",
        "torch": "torch",
        "numpy": "numpy"
    }

    all_installed = True

    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} - Install with: pip install {package}")
            all_installed = False

    if not all_installed:
        print("\n❌ Missing dependencies. Install with:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

    print()


def list_models():
    """
    List all available Whisper models
    """
    print("\n📋 Available Whisper Models:")
    print("=" * 60)

    models = [
        {
            "name": "tiny",
            "size": "39 MB",
            "speed": "⚡⚡⚡ Very Fast",
            "accuracy": "⭐⭐ Good",
            "use_case": "Fast, resource-constrained"
        },
        {
            "name": "base",
            "size": "74 MB",
            "speed": "⚡⚡ Fast",
            "accuracy": "⭐⭐⭐ Better",
            "use_case": "Recommended (balanced)"
        },
        {
            "name": "small",
            "size": "244 MB",
            "speed": "⚡ Medium",
            "accuracy": "⭐⭐⭐⭐ Best",
            "use_case": "High accuracy needed"
        },
        {
            "name": "medium",
            "size": "769 MB",
            "speed": "🐌 Slow",
            "accuracy": "⭐⭐⭐⭐⭐ Excellent",
            "use_case": "Quality over speed"
        },
        {
            "name": "large",
            "size": "1550 MB",
            "speed": "🐌🐌 Very Slow",
            "accuracy": "⭐⭐⭐⭐⭐ Best",
            "use_case": "Maximum quality"
        }
    ]

    for model in models:
        print(f"\n{model['name'].upper()}")
        print(f"   Size: {model['size']}")
        print(f"   Speed: {model['speed']}")
        print(f"   Accuracy: {model['accuracy']}")
        print(f"   Use case: {model['use_case']}")

    print("\n" + "=" * 60)
    print("\n💡 Recommended: 'base' model (best balance of speed and accuracy)")


def check_ffmpeg():
    """
    Check if ffmpeg is installed
    """
    import subprocess

    print("\n🔍 Checking ffmpeg installation...")

    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"   ✅ {version_line}")
            return True

    except FileNotFoundError:
        print("   ⚠️  ffmpeg not found")
        print("\n   ffmpeg is required for audio conversion.")
        print("   Install instructions:")
        print("   - macOS: brew install ffmpeg")
        print("   - Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("   - Windows: https://ffmpeg.org/download.html")
        print("\n   Note: The app can still work with pydub as a fallback")
        return False

    return False


def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(
        description="Download Whisper models for audio translation"
    )
    parser.add_argument(
        "--model",
        type=str,
        choices=["tiny", "base", "small", "medium", "large"],
        help="Model to download"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all models"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available models"
    )

    args = parser.parse_args()

    # Show banner
    print("\n" + "=" * 60)
    print("🎤 Whisper Model Downloader")
    print("   Audio Auto-Translator")
    print("=" * 60 + "\n")

    # List models if requested
    if args.list:
        list_models()
        sys.exit(0)

    # Check dependencies
    check_dependencies()

    # Check ffmpeg
    check_ffmpeg()

    # Download models
    if args.all:
        # Download all models
        models = ["tiny", "base", "small", "medium"]
        print(f"\n📥 Downloading {len(models)} models...")
        print("   This may take a while...\n")

        for model_name in models:
            success = download_whisper_model(model_name)
            if not success:
                print(f"\n⚠️  Failed to download {model_name}, continuing...")
                continue
            print()

    elif args.model:
        # Download specific model
        download_whisper_model(args.model)

    else:
        # No arguments - download recommended model
        print("ℹ️  No model specified. Downloading recommended 'base' model...")
        print("   Use --model <name> to download a specific model")
        print("   Use --list to see all available models\n")

        download_whisper_model("base")

    # Final message
    print("\n" + "=" * 60)
    print("✅ Download complete!")
    print("\nNext steps:")
    print("1. Create .env file: cp .env.example .env")
    print("2. Set WHISPER_MODEL=base in .env")
    print("3. Start server: uvicorn main:app --reload")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
