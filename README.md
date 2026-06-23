<h1 align="center">comfyui-strix-docker</h1>

<p align="center">
  <strong>ComfyUI on AMD Strix Halo (RDNA 3.5 / gfx1151) via Docker. Ubuntu 26.04 LTS + UV-managed Python 3.12 + TheRock ROCm 7.13 wheels. Fixes the silent CPU fallback that Debian / Python 3.13 images hit on gfx1151.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/AMD-Strix_Halo-ED1C24?logo=amd&logoColor=white" alt="AMD Strix Halo" />
  <img src="https://img.shields.io/badge/ROCm-7.13_(TheRock)-EF5B25?logo=amd&logoColor=white" alt="ROCm" />
  <img src="https://img.shields.io/badge/Base-Ubuntu_26.04_LTS-E95420?logo=ubuntu&logoColor=white" alt="Ubuntu" />
  <img src="https://img.shields.io/badge/Python-3.12_via_uv-3776AB?logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/License-MIT-blue" alt="License" />
</p>

---

## What this is

A Docker container for running **ComfyUI** on AMD's **Strix Halo (Ryzen AI Max+ 3xx)** APU. It targets `gfx1151` directly so the GPU is actually used, instead of the silent CPU fallback you get from generic images.

## Why this repo exists

Generic images fail on Strix Halo for three reasons:

1. **Permission:** the container needs the host's exact `render` / `video` group IDs to reach `/dev/kfd` and `/dev/dri`.
2. **Debian pip:** plain `pip` on Debian installs a CPU-only torch and silently falls back to CPU.
3. **Python version:** Ubuntu 26.04 ships Python 3.13; the gfx1151 ROCm wheels are built for 3.12.

**Solution:** Ubuntu 26.04 LTS for a stable, current base, with **uv** building an isolated **Python 3.12** venv inside the container, and **TheRock ROCm 7.13** wheels pinned to one coherent build so the install is reproducible.

### About the ROCm pin

There is no stable PyPI index for `gfx1151`, so the Dockerfile pins one same-date build off TheRock's nightly index rather than floating "latest". The three packages must stay on the same line (an ABI set):

| package      | version | tag                   |
| ------------ | ------- | --------------------- |
| torch        | 2.9.1   | `+rocm7.13.0a20260513` |
| torchvision  | 0.24.0  | `+rocm7.13.0a20260513` |
| torchaudio   | 2.9.0   | `+rocm7.13.0a20260513` |

To bump, pick a date present for all three on the same line and update the `ARG`s in the `Dockerfile`:

```bash
for p in torch torchvision torchaudio; do
  curl -fsSL https://rocm.nightlies.amd.com/v2/gfx1151/$p/ | grep rocm7.13.0a<DATE>
done
```

This is the same ROCm stack the [gamentic](https://github.com/hec-ovi/gamentic) project runs on the same gfx1151 box.

## Prerequisites

* **Host OS:** Ubuntu 25.10+ / a recent 6.x kernel with amdgpu
* **Hardware:** AMD Ryzen AI Max+ 3xx (Strix Halo / RDNA 3.5, gfx1151)
* **Docker + Compose**

## Installation

### 1. Clone

```bash
git clone https://github.com/hec-ovi/comfyui-strix-docker.git
cd comfyui-strix-docker
```

### 2. Configure permissions (required)

Tell Docker your GPU group IDs:

```bash
getent group video  | cut -d: -f3   # -> VIDEO_GID
getent group render | cut -d: -f3   # -> RENDER_GID
```

Copy the template and fill in your numbers and model path:

```bash
cp .envTemplate .env
```

```ini
# .env
VIDEO_GID=44       # your 'video' GID
RENDER_GID=990     # your 'render' GID
MODELS_PATH=/path/to/your/models
```

### 3. Launch

```bash
docker compose up -d --build
```

UI: **http://localhost:8188**

## Model management

Map a local folder so models persist across rebuilds. Suggested layout:

```text
~/workspace/models/comfy/
├── checkpoints/  (SD checkpoints)
├── unet/         (FLUX.2 diffusion models)
├── clip/         (FLUX.2 text encoders / T5)
├── vae/          (FLUX.2 VAE)
└── loras/        (LoRAs)
```

Drop files in and hit "Refresh" in the UI.

## Technical details

* **Base image:** `ubuntu:26.04` (LTS)
* **Python:** 3.12, pinned and built by `uv` (ignores the system 3.13)
* **PyTorch:** TheRock ROCm 7.13 wheels for `gfx1151`, pinned (see the table above)
* **GPU runtime env (set in the Dockerfile, overridable from compose):**
  * `HSA_OVERRIDE_GFX_VERSION=11.5.1` pins the ISA for Strix Halo
  * `HSA_ENABLE_SDMA=0` and `HSA_USE_SVM=0` are the community stability fixes for unified memory (avoid GPU ring timeouts / checkerboard artifacts during VAE decode)
* The build runs an `import torch; assert 'rocm' in torch.__version__` check, so a CPU-only torch fails the build instead of failing silently at runtime.

## Troubleshooting

* **"Torch not compiled with CUDA enabled":** the GIDs in `.env` are wrong, or your kernel is too old for amdgpu on gfx1151.
* **Permission denied on the GPU:** add your user to the host `render` and `video` groups.

---

## License

[MIT](LICENSE) for the build glue in this repository (Dockerfile, docker-compose.yml, entrypoint.sh, .envTemplate, README, scripts).

This repository does not redistribute ComfyUI source. The Dockerfile clones ComfyUI from `github.com/comfyanonymous/ComfyUI` at build time. ComfyUI is licensed under **GPL-3.0**. Any image built from this repository that bundles ComfyUI is therefore a derivative work of ComfyUI and is subject to GPL-3.0 when distributed. Building locally for personal use is fine; redistributing the resulting image, or any modified version of ComfyUI, requires complying with GPL-3.0.
