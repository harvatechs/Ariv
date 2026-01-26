# Deployment Guide

## Production Deployment Options

### 1. Google Colab (Development/Testing)
**Best for**: Quick demos, prototyping, free GPU access

```bash
# Open in Colab
https://colab.research.google.com/github/yourusername/maha-system/blob/main/deploy/colab_entry.ipynb

# Run all cells sequentially
# Note: Session expires after 12 hours
```

**Pros**: Free T4 GPU, no setup required
**Cons**: Ephemeral, limited to 12-hour sessions

---

### 2. Local Server (On-Premise)
**Best for**: Sovereign deployment, data privacy, offline operation

**Requirements**:
- NVIDIA GPU with 8GB+ VRAM (RTX 3070, 3080, 3090, A4000, etc.)
- 32GB RAM recommended
- Ubuntu 20.04/22.04 or Windows with WSL2

**Installation**:
```bash
# 1. Clone and install
git clone https://github.com/yourusername/maha-system.git
cd maha-system
make install-gpu

# 2. Download models
make download

# 3. Start API server
make api

# Server runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

**Pros**: Full control, no internet required after setup, data stays local
**Cons**: Hardware cost, maintenance overhead

---

### 3. Docker Deployment (Recommended for Production)
**Best for**: Scalable, reproducible deployments

**Prerequisites**:
- Docker with nvidia-docker2 support
- NVIDIA GPU drivers

**Quick Start**:
```bash
# Build image
make docker-build

# Run with docker-compose (includes Redis cache)
make docker-run

# Or manual docker run
docker run -d \
  --gpus all \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models:ro \
  -v $(pwd)/.cache:/app/.cache \
  --name maha-system \
  maha-system:latest
```

**Pros**: Portable, scalable, easy CI/CD integration
**Cons**: Requires Docker knowledge, GPU passthrough complexity

---

### 4. Cloud GPU (AWS/GCP/Azure)
**Best for**: High availability, elastic scaling

**AWS EC2 Example**:
```bash
# Launch g4dn.xlarge instance (T4 GPU, 16GB VRAM)
# AMI: Deep Learning AMI (Ubuntu 20.04)

ssh -i key.pem ubuntu@<instance-ip>

# Setup
git clone https://github.com/yourusername/maha-system.git
cd maha-system
make install-gpu
make download
make api

# Use systemd for persistence
sudo nano /etc/systemd/system/maha-system.service
```

**Systemd Service File**:
```ini
[Unit]
Description=Maha-System API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/maha-system
ExecStart=/usr/bin/python3 deploy/api_wrapper.py
Restart=always
Environment="CUDA_VISIBLE_DEVICES=0"

[Install]
WantedBy=multi-user.target
```

**Enable service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable maha-system
sudo systemctl start maha-system
sudo systemctl status maha-system
```

**Pros**: Professional infrastructure, auto-scaling, managed services
**Cons**: Cost ($0.50-2.00/hour for GPU instances), cloud vendor lock-in

---

### 5. Kubernetes (Enterprise Scale)
**Best for**: Multi-GPU clusters, auto-scaling, high availability

See `deploy/k8s/` directory for manifests:
- `deployment.yaml`: GPU pod specification
- `service.yaml`: Load balancer
- `hpa.yaml`: Horizontal pod autoscaler

```bash
kubectl apply -f deploy/k8s/
```

**Pros**: Enterprise-grade, fault-tolerant, massive scale
**Cons**: Complex setup, requires K8s expertise

---

## Performance Optimization

### VRAM Optimization
1. **Use Q4_K_M quantization** (already default)
2. **Reduce context window**: Edit `n_ctx` in config.py (4096 → 2048 saves 1GB)
3. **Enable CPU offloading**: For 7B models on 8GB GPUs
4. **Batch requests**: Process multiple queries in sequence

### Latency Optimization
1. **Enable caching**: Repeated queries served instantly
2. **Keep models loaded**: For high-throughput scenarios
3. **Use streaming**: Return tokens as they're generated
4. **Disable critic**: For speed-critical applications (trade accuracy)

### Throughput Optimization
1. **Multiple workers**: Run multiple API instances behind load balancer
2. **GPU sharing**: Use MIG (Multi-Instance GPU) on A100s
3. **Model parallelism**: Split large models across multiple GPUs

---

## Monitoring & Logging

### Enable Detailed Logging
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('maha-system.log'),
        logging.StreamHandler()
    ]
)
```

### Prometheus Metrics (Optional)
Add to `deploy/api_wrapper.py`:
```python
from prometheus_client import Counter, Histogram

request_count = Counter('maha_requests_total', 'Total requests')
latency_histogram = Histogram('maha_latency_seconds', 'Request latency')
```

### Health Checks
```bash
# Check system health
curl http://localhost:8000/health

# Check model status
curl http://localhost:8000/models

# VRAM status
nvidia-smi
```

---

## Security Considerations

1. **API Authentication**: Add API keys in production
2. **Rate Limiting**: Prevent abuse (use nginx or cloudflare)
3. **Input Sanitization**: Validate query length and content
4. **Model Integrity**: Verify GGUF checksums
5. **Network Isolation**: Run in private VPC for sensitive data

---

## Backup & Recovery

### Model Backup
```bash
# Sync to S3/GCS
aws s3 sync models/ s3://your-bucket/maha-models/

# Or use rclone for other cloud providers
rclone sync models/ remote:backup-bucket
```

### Cache Backup
```bash
# Cache is in .cache/ directory
# Backup regularly for performance
tar -czf cache-backup.tar.gz .cache/
```

---

## Troubleshooting Production Issues

### Issue: OOM (Out of Memory)
**Solution**: 
- Reduce `n_ctx` to 2048
- Enable CPU offloading
- Use smaller models (7B → 2B where possible)
- Add swap space (emergency only, very slow)

### Issue: Slow First Request
**Cause**: Model loading time
**Solution**: 
- Pre-load models on startup
- Use `torch.cuda.empty_cache()` carefully
- Consider keeping models in VRAM (if VRAM permits)

### Issue: High Latency
**Causes**: 
- Model hot-swap overhead
- Critic iterations

**Solution**:
- Disable critic for speed-critical paths
- Use caching for common queries
- Upgrade GPU (T4 → A100 = 5x speedup)

### Issue: Models Not Found
**Solution**:
```bash
# Check paths in config.py
python -c "from config import get_model_paths; print(get_model_paths())"

# Re-download if missing
make download
```

---

## Cost Analysis (Monthly)

| Deployment | Hardware | Cost | Best For |
|------------|----------|------|----------|
| Colab | Free T4 | $0 | Development |
| Local RTX 3090 | 24GB VRAM | $50 (power) | Personal/Small team |
| AWS g4dn.xlarge | T4 16GB | $150-300 | Production |
| AWS g5.xlarge | A10G 24GB | $400-600 | High throughput |
| AWS p3.2xlarge | V100 16GB | $800-1200 | Research |

---

## Support & Community

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Discord**: [Invite Link]
- **Email**: support@maha-system.ai

---

**Last Updated**: 2026-01-26
**Version**: 1.0.0
