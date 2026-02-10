# Troubleshooting

## llama.cpp errors
- `CUDA error: out of memory`: reduce `--num-gpu-layers` or use Q4_K_M.
- `failed to mmap`: disable `--mmap` if running from a network filesystem.

## GPU offload tips
- Start with `num_gpu_layers` around 10–20 for 4–6GB GPUs.
- Use Q4_K_M and test with `verify_model.sh`.

## Windows notes
- Prefer WSL2 + Ubuntu 22.04.
- Ensure GPU drivers are visible to WSL.
