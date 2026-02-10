# Maha-System Makefile
# Quick commands for common operations

.PHONY: help install test clean docker run-colab download-models

PYTHON := python3
PIP := pip3

help:
	@echo "Maha-System - Available Commands:"
	@echo "  make install        - Install dependencies"
	@echo "  make install-gpu    - Install with CUDA support"
	@echo "  make download       - Download model files"
	@echo "  make test           - Run test suite"
	@echo "  make test-cuda      - Run tests requiring GPU"
	@echo "  make run            - Run interactive CLI"
	@echo "  make api            - Start API server"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo "  make clean          - Clean cache and temp files"
	@echo "  make profile        - Run performance profiler"
	@echo "  make smoke          - Run smoke inference test"

install:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

install-gpu:
	CMAKE_ARGS="-DLLAMA_CUBLAS=on" $(PIP) install llama-cpp-python --force-reinstall --no-cache-dir
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

download:
	$(PYTHON) models/download_models.py all

test:
	pytest tests/ -v -m "not slow and not requires_cuda"

test-cuda:
	pytest tests/ -v -m "requires_cuda"

test-all:
	pytest tests/ -v

run:
	$(PYTHON) maha_system.py --interactive --lang hindi

api:
	$(PYTHON) deploy/api_wrapper.py

docker-build:
	docker build -t maha-system:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

clean:
	rm -rf .cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete

profile:
	$(PYTHON) -c "from utils.profiler import PipelineProfiler; print('Profiler ready')"

benchmark-sanskriti:
	$(PYTHON) benchmarks/sanskriti_eval.py --data data/sanskriti.json --max-samples 100

lint:
	black core/ utils/ benchmarks/ ariv/ --check
	flake8 core/ utils/ benchmarks/ ariv/ --max-line-length=100

format:
	black core/ utils/ benchmarks/ ariv/

smoke:
	ARIV_MOCK_LLAMA=1 $(PYTHON) -c "from ariv.runner.app import app; print('OK')"
