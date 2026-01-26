#!/bin/bash

# Ariv Quick Start Script
# This script helps you get started with Ariv quickly

set -e

echo "🎵 Ariv: The Indian AI Orchestra - Quick Start"
echo "="60

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_step "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_info "Found $PYTHON_VERSION"
        
        # Check if version is >= 3.8
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_info "Python version is compatible (>= 3.8)"
        else
            print_error "Python version must be 3.8 or higher"
            exit 1
        fi
    else
        print_error "Python3 not found. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_step "Checking pip installation..."
    if command -v pip3 &> /dev/null; then
        print_info "pip3 found"
    else
        print_error "pip3 not found. Please install pip."
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_step "Installing dependencies..."
    
    if [ -f "requirements.txt" ]; then
        print_info "Installing from requirements.txt..."
        pip3 install -r requirements.txt
        print_info "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Download models
download_models() {
    print_step "Downloading models..."
    
    if [ -f "models/download_models.py" ]; then
        print_info "Downloading core models (this may take a while)..."
        python3 models/download_models.py core
        print_info "Models downloaded successfully"
    else
        print_error "Model downloader not found"
        exit 1
    fi
}

# Test installation
test_installation() {
    print_step "Testing installation..."
    
    # Test basic import
    if python3 -c "import sys; sys.path.insert(0, '.'); from config import get_supported_languages; print('✅ Config imported successfully')"; then
        print_info "Basic import test passed"
    else
        print_error "Basic import test failed"
        exit 1
    fi
    
    # Test model status
    if python3 -c "import sys; sys.path.insert(0, '.'); from maha_system import main; print('✅ Main module imported successfully')"; then
        print_info "Main module test passed"
    else
        print_error "Main module test failed"
        exit 1
    fi
}

# Show usage options
show_usage() {
    print_step "Installation complete! Here are your options:"
    echo ""
    echo "🌐 GUI Interface (Web Browser):"
    echo "   python gui/launch.py"
    echo "   # Then open http://localhost:8080 in your browser"
    echo ""
    echo "🖥️  TUI Interface (Terminal):"
    echo "   python tui/launch.py"
    echo ""
    echo "💻 CLI Interface (Command Line):"
    echo "   python maha_system.py --interactive --lang hindi"
    echo ""
    echo "🧪 Test the system:"
    echo "   python maha_system.py --status"
    echo "   python test_basic.py"
    echo "   python demo_ariv.py"
    echo ""
    echo "📚 View documentation:"
    echo "   cat README.md"
    echo "   cat docs/USER_GUIDE.md"
    echo ""
    echo "🐳 Use Docker (optional):"
    echo "   docker-compose up"
    echo ""
}

# Main execution
main() {
    echo "Starting Ariv installation..."
    echo ""
    
    check_python
    check_pip
    install_dependencies
    download_models
    test_installation
    show_usage
    
    print_step "🎉 Ariv is ready to use!"
    print_info "Choose your preferred interface and start chatting in any of the 22 Indian languages!"
    echo ""
    echo "For help, visit: https://github.com/harvatechs/Ariv"
    echo "Join our Discord: https://discord.gg/ariv"
}

# Check if script is being run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
