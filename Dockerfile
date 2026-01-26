# Ariv Docker Container
# Multi-stage build for production deployment

FROM python:3.10-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy \
    textual[dev]

# Copy source code
COPY . .

# Install package in development mode
RUN pip install -e .

# Expose ports
EXPOSE 8000 8080

# Default command for development
CMD ["python", "maha_system.py", "--interactive", "--lang", "hindi"]

# Production stage
FROM base as production

# Create non-root user
RUN useradd --create-home --shell /bin/bash ariv \
    && chown -R ariv:ariv /app
USER ariv

# Copy source code
COPY --chown=ariv:ariv . .

# Install package
RUN pip install --no-cache-dir -e .

# Create directories
RUN mkdir -p /app/models /app/logs /app/data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; print('Python version:', sys.version); sys.exit(0)"

# Expose ports
EXPOSE 8000  # API port
EXPOSE 8080  # GUI port

# Environment variables
ENV ARIV_ENV=production \
    ARIV_LOG_LEVEL=INFO \
    ARIV_MODELS_DIR=/app/models \
    ARIV_DATA_DIR=/app/data

# Default command
CMD ["python", "deploy/api_wrapper.py", "--host", "0.0.0.0", "--port", "8000"]

# GUI stage
FROM base as gui

# Copy GUI files
COPY gui/ /app/gui/
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install simple HTTP server
RUN pip install --no-cache-dir fastapi uvicorn

# Create startup script
RUN echo '#!/bin/bash\n\
cd /app/gui\n\
echo "🎵 Starting Ariv GUI..."\n\
python -m http.server 8080 &\n\
echo "GUI running on http://localhost:8080"\n\
wait' > /app/start-gui.sh && chmod +x /app/start-gui.sh

EXPOSE 8080
CMD ["/app/start-gui.sh"]

# TUI stage
FROM base as tui

# Install TUI dependencies
RUN pip install --no-cache-dir textual>=0.44.0

# Copy source code
COPY . .

# Install package
RUN pip install -e .

# Set TERM for proper TUI display
ENV TERM=xterm-256color

CMD ["python", "tui/launch.py"]
