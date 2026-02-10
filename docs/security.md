# Security notes

- Treat downloaded models as untrusted. Prefer running ARIV inside a container or VM.
- Avoid running arbitrary GGUF files from unknown sources.
- Use read-only volumes for model files when possible.
