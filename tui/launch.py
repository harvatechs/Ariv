#!/usr/bin/env python3
"""
Ariv TUI Launcher - Simple launcher for the Terminal UI
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Ariv TUI"""
    print("🎵 Launching Ariv TUI - Indian AI Orchestra")
    print("=" * 60)
    
    # Check if textual is installed
    try:
        import textual
        print(f"✅ Textual version: {textual.__version__}")
    except ImportError:
        print("❌ Textual not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "textual"])
            print("✅ Textual installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Textual")
            print("Please install manually: pip install textual")
            sys.exit(1)
    
    # Launch the TUI
    tui_path = Path(__file__).parent / "main.py"
    
    if tui_path.exists():
        print(f"🚀 Starting TUI from: {tui_path}")
        try:
            subprocess.run([sys.executable, str(tui_path)])
        except KeyboardInterrupt:
            print("\n👋 TUI closed by user")
        except Exception as e:
            print(f"❌ Error launching TUI: {e}")
    else:
        print(f"❌ TUI main.py not found at: {tui_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
