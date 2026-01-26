# 📘 Ariv User Guide

This guide will help you get started with Ariv - The Indian AI Orchestra, covering all available interfaces and features.

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [GUI Interface](#gui-interface)
- [TUI Interface](#tui-interface)
- [CLI Interface](#cli-interface)
- [Language Support](#language-support)
- [Settings and Configuration](#settings-and-configuration)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/harvatechs/Ariv.git
cd Ariv

# Install dependencies
pip install -r requirements.txt

# Download models
python models/download_models.py core
```

### 2. Choose Your Interface

**For a graphical interface (recommended for beginners):**
```bash
python gui/launch.py
```

**For a terminal interface (power users):**
```bash
python tui/launch.py
```

**For command-line usage (scripts, automation):**
```bash
python maha_system.py --interactive
```

---

## 🌐 GUI Interface

The GUI provides a modern, user-friendly web interface for interacting with Ariv.

### Launching the GUI

```bash
# Method 1: Using the launcher
python gui/launch.py

# Method 2: Manual HTTP server
python -m http.server 8080 --directory gui/
# Open http://localhost:8080 in your browser
```

### GUI Features

![GUI Interface](./images/gui-screenshot.png)

#### 1. Chat Area
- **Message Input**: Type your questions here
- **Send Button**: Click or press Enter to send
- **Message History**: Scrollable conversation log
- **Typing Indicator**: Shows when Ariv is thinking

#### 2. Language Selector
- Dropdown to select from 12+ Indian languages
- Instantly changes the input placeholder
- Affects response language

#### 3. Settings Panel
- **Enable Critic**: Toggle adversarial verification
- **Deep Reasoning**: Enable multi-step chain-of-thought
- **Self-Consistency**: Enable multiple reasoning paths
- **Enable Tools**: Allow calculator and code execution

#### 4. Statistics Panel
- **Messages**: Total messages sent
- **Avg Response Time**: Average time per response
- **Language**: Currently selected language

### Using the GUI

1. **Select your language** from the dropdown
2. **Type your question** in the input box
3. **Press Enter or click Send**
4. **Wait for Ariv's response** (typing indicator shows thinking)
5. **Continue the conversation** or start a new one

### GUI Keyboard Shortcuts

- `Enter`: Send message
- `Shift+Enter`: New line in input
- `Ctrl+L`: Clear chat (if implemented)
- `Ctrl+S`: Export chat (if implemented)

### GUI Tips

- The interface adapts to your system's dark/light mode
- Hover over settings for tooltips
- Export your chat from the settings panel
- Try different settings to see how responses change

---

## 🖥️ TUI Interface

The TUI (Terminal User Interface) provides a powerful, keyboard-driven interface for power users.

### Launching the TUI

```bash
# Method 1: Using the launcher
python tui/launch.py

# Method 2: Direct execution
python tui/main.py
```

### TUI Layout

![TUI Interface](./images/tui-screenshot.png)

```
┌─────────────────────────────────────────────────────────────┐
│  Ariv - Indian AI Orchestra                    14:32:45     │
├────────────┬────────────────────────────────────────────────┤
│  Language  │  ┌──────────────────────────────────────────┐  │
│  ────────  │  │  [14:32:10] Ariv: Welcome to Ariv!      │  │
│  [Dropdown]│  │  [14:32:15] You: नमस्ते                  │  │
│            │  │  [14:32:17] Ariv: नमस्ते! मैं Ariv हूं। │  │
│  Settings  │  │                                          │  │
│  ────────  │  │  [14:32:25] You: 2+2 कितना होता है?     │  │
│  ✓ Critic  │  │  [14:32:27] Ariv: 2+2 = 4 होता है।      │  │
│  ✓ Deep    │  │                                          │  │
│  ✓ Self    │  └──────────────────────────────────────────┘  │
│  ☐ Tools   │                                                 │
│            │  ┌──────────────────────────────────────────┐  │
│  Statistics│  │  Type your message...                   │  │
│  ───────── │  │  [Send]                                  │  │
│  Messages:5│  └──────────────────────────────────────────┘  │
│  Avg: 2.1s │                                                 │
│  Lang: Hindi│                                                │
├────────────┴────────────────────────────────────────────────┤
│  Ctrl+C:Quit  Ctrl+L:Clear  Ctrl+S:Export  Enter:Send       │
└─────────────────────────────────────────────────────────────┘
```

### TUI Features

#### 1. Settings Sidebar (Left)
- **Language Selector**: Dropdown for language selection
- **Settings Checkboxes**: Toggle various features
- **Statistics**: Real-time stats display
- **Action Buttons**: Clear and Export chat

#### 2. Chat Area (Top-Right)
- **Message History**: Timestamped conversation
- **Color Coding**: User (yellow), Bot (blue), System (dim)
- **Markdown Support**: Basic formatting
- **Scrollable**: Navigate through history

#### 3. Input Area (Bottom-Right)
- **Text Input**: Multi-line input field
- **Send Button**: Click or press Enter
- **Status Bar**: Current state information

### TUI Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Send message |
| `Ctrl+C` | Quit application |
| `Ctrl+L` | Clear chat history |
| `Ctrl+S` | Export chat to file |
| `Ctrl+T` | Toggle settings panel |
| `F1` | Show help |
| `Tab` | Navigate between elements |
| `Up/Down` | Navigate input history |

### Using the TUI

1. **Select Language**: Use the dropdown in the settings panel
2. **Configure Settings**: Toggle checkboxes as needed
3. **Type Message**: Click in the input area or press Tab
4. **Send**: Press Enter or click Send button
5. **View Response**: Watch the chat area for Ariv's reply

### TUI Tips

- The interface is fully keyboard-navigable
- Settings changes take effect immediately
- Chat history persists until cleared
- Export creates a JSON file with timestamp

---

## 💻 CLI Interface

The CLI provides scriptable, command-line access to Ariv.

### Basic Usage

```bash
# Interactive mode
python maha_system.py --interactive --lang hindi

# Single query
python maha_system.py --query "What is 2+2?" --lang english

# With reasoning trace
python maha_system.py --query "एक रस्सी की दो टुकड़े..." --lang hindi --show-trace
```

### CLI Options

```bash
python maha_system.py [OPTIONS]

Options:
  --query TEXT               Input query in vernacular language
  --lang TEXT                Input language (default: hindi)
  --interactive              Interactive mode for continuous queries
  --batch TEXT               Input file for batch processing
  --output TEXT              Output file for batch results
  --benchmark TEXT           Run benchmark with given problem file
  --no-critic                Disable critic phase (faster but less accurate)
  --reasoner TEXT            Reasoning model to use (default: deepseek-r1)
  --show-trace               Show full reasoning trace
  --status                   Show model status and exit
  --log-level TEXT           Logging level (DEBUG, INFO, WARNING, ERROR)
```

### CLI Examples

#### Interactive Session
```bash
$ python maha_system.py --interactive --lang hindi
🎵 Ariv: The Indian AI Orchestra - Interactive Mode
============================================================
Supports all 22 official Indian languages
Type 'exit' to quit, 'trace' to toggle reasoning display
Type 'lang <language>' to change language
Type 'stats' to see pipeline statistics
============================================================

[hindi]> नमस्ते
🔄 Processing...

🎯 FINAL ANSWER (hindi):
============================================================
नमस्ते! मैं Ariv हूं। आपकी कैसे मदद कर सकता हूं?
⏱️  Pipeline time: 2.1s
🔄 Critic iterations: 1
```

#### Batch Processing
```bash
# Create input file
echo "What is 2+2?\nHow are you?" > queries.txt

# Process batch
python maha_system.py --batch queries.txt --output results.json --lang english

# View results
cat results.json
```

#### Benchmark Mode
```bash
# Run benchmark
python maha_system.py --benchmark benchmarks/sample_problems.json
```

### CLI Tips

- Use `--status` to check if models are available
- Use `--no-critic` for faster responses
- Use `--show-trace` to see the full reasoning process
- Use `--log-level DEBUG` for detailed logging

---

## 🌍 Language Support

### Switching Languages

**GUI**: Use the language dropdown in the settings panel

**TUI**: Use the language selector in the settings sidebar

**CLI**: Use the `--lang` flag or type `lang <language>` in interactive mode

```bash
# CLI language switching
python maha_system.py --interactive --lang tamil
[tamil]> வணக்கம்

# Change language during session
[tamil]> lang hindi
Language changed to: hindi
[hindi]> नमस्ते
```

### Supported Languages

All 22 official Indian languages plus Hinglish:
- **Major Languages**: Hindi, Bengali, Telugu, Marathi, Tamil, Urdu, Gujarati, Kannada, Malayalam, Odia, Punjabi
- **Regional Languages**: Assamese, Maithili, Sanskrit, Kashmiri, Konkani, Nepali, Sindhi, Dogri, Manipuri, Bodo, Santali
- **Code-mixed**: Hinglish (Hindi-English)

### Language-Specific Features

- **Script Support**: Proper rendering of Devanagari, Bengali, Tamil, Telugu, etc.
- **Cultural Context**: Preserves cultural nuances and references
- **Regional Variations**: Handles dialectal differences
- **Transliteration**: Supports Romanized input for some languages

---

## ⚙️ Settings and Configuration

### Available Settings

| Setting | Description | Default | Impact |
|---------|-------------|---------|--------|
| **Enable Critic** | Adversarial verification of responses | ✅ On | Higher accuracy, slower |
| **Deep Reasoning** | Multi-step chain-of-thought | ✅ On | Better reasoning, slower |
| **Self-Consistency** | Multiple reasoning paths with voting | ✅ On | More reliable, slower |
| **Enable Tools** | Calculator and code execution | ☐ Off | Extended capabilities |

### Adjusting Settings

**GUI**: Toggle checkboxes in the settings panel

**TUI**: Use checkboxes in the settings sidebar

**CLI**: Use flags or interactive commands
```bash
# Disable critic for faster responses
python maha_system.py --query "2+2?" --lang english --no-critic

# Or in interactive mode
[hindi]> settings critic off
```

### Configuration Files

Settings are saved automatically:
- **GUI**: LocalStorage in browser
- **TUI**: Settings persist for session
- **CLI**: Use environment variables or config files

---

## ⌨️ Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action | Available In |
|----------|--------|--------------|
| `Ctrl+C` | Quit/Cancel | All interfaces |
| `Ctrl+S` | Export chat | TUI, CLI |
| `Ctrl+L` | Clear chat | TUI, CLI |
| `F1` | Show help | TUI |

### GUI Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Shift+Enter` | New line |
| `Ctrl+Enter` | Send message (alternative) |

### TUI Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Tab` | Navigate between elements |
| `Up/Down` | Navigate input history |
| `Ctrl+T` | Toggle settings panel |
| `Ctrl+H` | Show help |

### CLI Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message (interactive mode) |
| `Ctrl+D` | Exit (interactive mode) |
| `Ctrl+C` | Cancel current operation |

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Models Not Found
```
Error: Model file not found: models/translator.gguf
```

**Solution:**
```bash
# Download models
python models/download_models.py core
```

#### 2. GUI Not Loading
```
404: Page not found
```

**Solution:**
```bash
# Make sure you're in the gui directory
cd gui
python -m http.server 8080
# Or use the launcher
python launch.py
```

#### 3. TUI Display Issues
```
Text overlapping or colors wrong
```

**Solution:**
- Use a modern terminal (iTerm2, Windows Terminal, gnome-terminal)
- Set TERM environment variable: `export TERM=xterm-256color`
- Increase terminal size if needed

#### 4. Out of Memory
```
CUDA out of memory
```

**Solution:**
- Close other applications using GPU
- Use smaller models: `python models/download_models.py translator only`
- Enable CPU mode (slower but works)

#### 5. Language Not Supported
```
Error: Language 'xyz' not supported
```

**Solution:**
- Check available languages: `python maha_system.py --status`
- Use supported language code
- Request new language support via GitHub issues

### Getting Help

1. **Check the logs**: Run with `--log-level DEBUG`
2. **Check model status**: `python maha_system.py --status`
3. **Read documentation**: See [docs/](docs/) directory
4. **Search issues**: [GitHub Issues](https://github.com/harvatechs/Ariv/issues)
5. **Ask for help**: [GitHub Discussions](https://github.com/harvatechs/Ariv/discussions)

### Reporting Issues

When reporting issues, please include:
- Operating system and version
- Python version
- Error message (full traceback)
- Steps to reproduce
- Interface used (GUI/TUI/CLI)

---

## 💡 Tips and Best Practices

### For Best Performance

1. **Use appropriate language**: Responses are better in the selected language
2. **Enable Deep Reasoning**: For complex problems
3. **Enable Self-Consistency**: For critical reasoning tasks
4. **Use Tools**: For mathematical or computational problems

### For Speed

1. **Disable Critic**: For faster responses (less accurate)
2. **Disable Deep CoT**: For simple queries
3. **Use CLI**: For batch processing
4. **Pre-download models**: Avoid first-time loading delays

### For Accuracy

1. **Enable all settings**: Critic, Deep CoT, Self-Consistency
2. **Use specific language**: Not English for Indian queries
3. **Provide context**: Give background information
4. **Break down complex queries**: Ask step-by-step

### For Production

1. **Use Docker**: Consistent environment
2. **Monitor resources**: VRAM usage, response times
3. **Implement caching**: For repeated queries
4. **Use API**: For integration with other systems

---

## 🎓 Learning Resources

### For Users

- **[Video Tutorial](https://youtube.com/ariv-tutorial)**: Getting started guide
- **[Example Queries](docs/examples/)**: Sample queries in all languages
- **[FAQ](docs/FAQ.md)**: Frequently asked questions

### For Developers

- **[API Documentation](docs/API.md)**: Complete API reference
- **[Architecture Guide](docs/ARCHITECTURE.md)**: System design details
- **[Contributing Guide](docs/CONTRIBUTING.md)**: How to contribute

---

**Happy chatting with Ariv!** 🎵

For more help, visit our [GitHub repository](https://github.com/harvatechs/Ariv) or join our [Discord community](https://discord.gg/ariv).
