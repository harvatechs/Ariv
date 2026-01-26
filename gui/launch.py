#!/usr/bin/env python3
"""
Ariv GUI Launcher - Simple launcher for the Web GUI
"""

import sys
import subprocess
import http.server
import socketserver
import threading
import time
import webbrowser
from pathlib import Path

def find_free_port(start_port=8080):
    """Find a free port starting from start_port"""
    import socket
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError("No free port found")

def main():
    """Launch the Ariv GUI"""
    print("🎵 Launching Ariv GUI - Indian AI Orchestra")
    print("=" * 60)
    
    # Check if we're in the right directory
    gui_dir = Path(__file__).parent
    index_file = gui_dir / "index.html"
    
    if not index_file.exists():
        print(f"❌ GUI index.html not found at: {index_file}")
        print("Please make sure you're running this from the gui directory")
        sys.exit(1)
    
    # Find a free port
    try:
        port = find_free_port(8080)
        print(f"✅ Found free port: {port}")
    except RuntimeError:
        print("❌ No free port found")
        sys.exit(1)
    
    # Change to GUI directory
    original_dir = Path.cwd()
    os.chdir(gui_dir)
    
    # Start HTTP server in a separate thread
    def start_server():
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"🚀 HTTP server running on port {port}")
            httpd.serve_forever()
    
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait a moment for server to start
    time.sleep(1)
    
    # Open browser
    url = f"http://localhost:{port}"
    print(f"🌐 Opening browser: {url}")
    
    try:
        webbrowser.open(url)
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print(f"Please manually open: {url}")
    
    print("\n✅ GUI is running!")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 GUI server stopped by user")
        os.chdir(original_dir)
        sys.exit(0)

if __name__ == "__main__":
    import os
    main()
