# 🤝 Contributing to Ariv

Thank you for your interest in contributing to Ariv - The Indian AI Orchestra! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Areas for Contribution](#areas-for-contribution)
- [Recognition](#recognition)

---

## 📜 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Examples of behavior that contributes to a positive environment:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Examples of unacceptable behavior:**
- The use of sexualized language or imagery
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team. All complaints will be reviewed and investigated and will result in a response that is deemed necessary and appropriate to the circumstances.

---

## 🚀 Getting Started

### New Contributor Guide

Welcome! Here's how to get started:

1. **Read the documentation**: Start with [README.md](../README.md) and [USER_GUIDE.md](USER_GUIDE.md)
2. **Try the interfaces**: Use GUI, TUI, and CLI to understand the system
3. **Run the examples**: See [examples/](examples/) directory
4. **Join the community**: [Discord](https://discord.gg/ariv) and [GitHub Discussions](https://github.com/harvatechs/Ariv/discussions)

### Your First Contribution

**Good first issues** are labeled with `good first issue` on GitHub. These include:
- Documentation improvements
- Adding examples
- Fixing typos
- Adding tests
- Improving error messages

### Development Workflow

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/Ariv.git
   cd Ariv
   ```
3. **Set up development environment**:
   ```bash
   pip install -e ".[dev]"
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. **Make your changes** and commit them
6. **Push to your fork** and create a pull request

---

## 🛠️ Development Setup

### Prerequisites

- Python 3.8+
- Git
- CUDA-compatible GPU (optional but recommended)
- 16GB+ RAM

### Installation

```bash
# Clone the repository
git clone https://github.com/harvatechs/Ariv.git
cd Ariv

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install in development mode
pip install -e ".[dev]"

# Download models for testing
python models/download_models.py core
```

### Development Dependencies

```bash
# Install all development dependencies
pip install -e ".[dev]"

# This includes:
# - pytest (testing)
# - black (code formatting)
# - flake8 (linting)
# - mypy (type checking)
# - textual[dev] (TUI development)
```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit
pre-commit install
```

This will automatically run:
- Black (code formatting)
- Flake8 (linting)
- MyPy (type checking)

---

## 📝 Coding Standards

### Code Style

We use **Black** for code formatting:

```bash
# Format your code
black .

# Or check formatting
black --check .
```

### Linting

We use **Flake8** for linting:

```bash
# Run linter
flake8 .

# Configuration is in setup.cfg
```

### Type Checking

We use **MyPy** for type checking:

```bash
# Run type checker
mypy core/
mypy tools/
mypy benchmarks/
```

### Documentation

- Use docstrings for all public functions and classes
- Follow Google style docstrings
- Keep documentation up to date

```python
def my_function(param1: str, param2: int) -> bool:
    """Brief description of the function.
    
    Args:
        param1: Description of parameter 1.
        param2: Description of parameter 2.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When param1 is invalid.
    """
    pass
```

---

## 🔄 How to Contribute

### Reporting Issues

Before creating an issue:
- Search existing issues to avoid duplicates
- Check if it's a known problem in the documentation
- Gather all relevant information

When reporting bugs, include:
- Operating system and version
- Python version
- Full error message and traceback
- Steps to reproduce the issue
- Expected behavior vs actual behavior

**Bug Report Template:**
```markdown
## Bug Description
Brief description of the bug.

## Environment
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.9.7]
- Ariv Version: [e.g., 2.0.0]

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Error Messages
```
Paste full error messages here
```

## Additional Context
Any other relevant information.
```

### Suggesting Features

For feature requests:
- Explain the use case and motivation
- Describe the proposed solution
- Consider backward compatibility
- Discuss potential alternatives

**Feature Request Template:**
```markdown
## Feature Description
Clear description of the feature.

## Motivation
Why is this feature needed? What problem does it solve?

## Proposed Solution
How should this feature work?

## Alternatives
What other approaches have you considered?

## Additional Context
Any other relevant information.
```

### Code Contributions

#### Before You Start

1. **Check if the change is needed**:
   - Search existing issues and PRs
   - Discuss large changes in an issue first
   - For bugs, create an issue if one doesn't exist

2. **Understand the scope**:
   - Small fixes: documentation, typos, tests
   - Medium features: new tools, language support
   - Large features: new interfaces, major refactoring

#### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Make your changes**:
   - Write clean, readable code
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: descriptive commit message"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a pull request**:
   - Fill out the PR template
   - Link to relevant issues
   - Request review from maintainers

#### Pull Request Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Added unit tests
- [ ] Added integration tests
- [ ] Manually tested
- [ ] Updated documentation

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass

## Related Issues
Closes #issue_number
```

---

## 🎯 Areas for Contribution

### High Priority

1. **Additional Indian Language Models**
   - Santali specialist model
   - Bodo specialist model
   - Dogri specialist model
   - Manipuri specialist model

2. **Performance Optimizations**
   - Faster model loading
   - Better VRAM management
   - Quantized model support

3. **Tool Integrations**
   - Wikipedia API integration
   - Weather API integration
   - News API integration
   - Wolfram Alpha integration

4. **Mobile/Edge Deployment**
   - Android APK
   - iOS app
   - Raspberry Pi support
   - Browser extension

### Medium Priority

1. **GUI Enhancements**
   - Voice input support
   - File upload/download
   - Chat themes
   - Mobile-responsive design

2. **TUI Enhancements**
   - Better markdown support
   - Chat history navigation
   - Plugin system
   - Custom themes

3. **Testing Infrastructure**
   - Automated benchmarks
   - Performance regression tests
   - Cross-platform testing
   - Load testing

4. **Documentation**
   - Video tutorials
   - Interactive examples
   - API documentation improvements
   - Translation of docs

### Low Priority

1. **Developer Tools**
   - VS Code extension
   - Jupyter notebook integration
   - Debugging utilities
   - Profiling tools

2. **Analytics**
   - Usage statistics
   - Performance metrics
   - Error tracking
   - User feedback system

---

## 🏆 Recognition

### Contributors

We recognize and appreciate all contributors! Contributors are listed in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md) - List of all contributors
- GitHub contributors page
- Release notes for major contributions

### Hall of Fame

Special recognition for:
- **Core Contributors**: Regular, high-quality contributions
- **Language Champions**: Adding new language support
- **Tool Masters**: Creating useful tools and integrations
- **Documentation Heroes**: Improving docs and examples
- **Bug Busters**: Finding and fixing critical bugs

### How to Get Recognized

1. Make consistent, high-quality contributions
2. Help other contributors and users
3. Contribute to documentation and examples
4. Participate in discussions and reviews
5. Spread the word about Ariv!

---

## 📞 Contact

### Maintainers

- Project Lead: [Your Name](mailto:lead@ariv.ai)
- Technical Lead: [Tech Lead](mailto:tech@ariv.ai)
- Community Manager: [Community](mailto:community@ariv.ai)

### Community Channels

- **Discord**: [Join our server](https://discord.gg/ariv)
- **Twitter**: [@ArivAI](https://twitter.com/ArivAI)
- **LinkedIn**: [Ariv AI](https://linkedin.com/company/ariv-ai)
- **Email**: hello@ariv.ai

---

## 📜 Legal

### Contributor License Agreement

By contributing to Ariv, you agree that:
- Your contributions are your original work
- You grant the project a perpetual, worldwide, non-exclusive license
- You have the right to make the contribution
- You understand contributions may be used commercially

### Privacy Policy

We respect your privacy:
- No telemetry or tracking in the core application
- Optional analytics in GUI/TUI (opt-in only)
- Chat data stored locally unless exported
- No data sent to external servers without consent

---

## 🎉 Thank You!

Thank you for contributing to Ariv! Your contributions help make AI accessible to billions of Indians in their native languages.

**Jai Hind!** 🇮🇳

---

## 📚 Additional Resources

- [Development Guide](docs/DEVELOPMENT.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Testing Guide](docs/TESTING.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Style Guide](docs/STYLE_GUIDE.md)
