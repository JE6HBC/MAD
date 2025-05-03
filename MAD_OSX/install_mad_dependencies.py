import subprocess
import sys
import os

def ensure_pip():
    try:
        import pip
        print("✔ pip is already available.")
    except ImportError:
        print("⏳ Installing pip...")
        import ensurepip
        ensurepip.bootstrap()
        print("✔ pip installed.")

def install_packages(packages):
    python_exe = sys.executable
    for package in packages:
        try:
            print(f"⏳ Installing: {package}...")
            subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", package])
            print(f"✔ Installed: {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install: {package}")

def main():
    print("🔧 Setting up MAD dependencies for Blender...")

    ensure_pip()

    # You can add more packages here if needed.
    required = [
        "sounddevice",
        "cffi"
    ]

    install_packages(required)

    print("\n✅ All dependencies installed! You can now enable the MAD addon.")

main()