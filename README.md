<h1 align="center">comfyui-strix-docker</h1>

<p align="center">
  <strong>ComfyUI on AMD Strix Halo (RDNA 3.5 / gfx1151) via Docker. Ubuntu Rolling + UV-managed Python 3.12 + ROCm preview wheels. Fixes the silent CPU fallback Debian/Python 3.13 images hit on Strix Halo.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Verified-brightgreen" alt="Status" />
  <img src="https://img.shields.io/badge/AMD-Strix_Halo-ED1C24?logo=amd&logoColor=white" alt="AMD Strix Halo" />
  <img src="https://img.shields.io/badge/ROCm-7.x_Preview-EF5B25?logo=amd&logoColor=white" alt="ROCm" />
  <img src="https://img.shields.io/badge/Base-Ubuntu_Rolling-E95420?logo=ubuntu&logoColor=white" alt="Ubuntu" />
  <img src="https://img.shields.io/badge/Python-3.12_via_uv-3776AB?logo=python&logoColor=white" alt="Python 3.12" />
  <img src="https://img.shields.io/badge/License-MIT-blue" alt="License" />
</p>

---

## What this is

A battle-tested Docker container for running **ComfyUI** on AMD's **Strix Halo (Ryzen AI Max 300)** architecture.

It solves the common "silent failures" where standard containers fallback to CPU mode because they lack the specific preview drivers for `gfx1151`.

## 🚀 Why This Repo Exists
Standard Docker images (Debian/Ubuntu 22.04) fail on Strix Halo for three reasons:
1.  **Permission:** We need precise GID mapping.
2.  **Debian:** `pip` on Debian fails to install ROCm preview wheels and silently falls back to CPU.
3.  **Ubuntu: Python 3.13 Mismatch:** Ubuntu Rolling ships with Python 3.13, which PyTorch doesn't support yet.

**Solution:** use **Ubuntu Rolling** (for driver support) but force **UV** to build an isolated **Python 3.12** environment inside the container. This gives us the best of both worlds: modern drivers + stable Python.

## 🛠️ Prerequisites
* **Host OS:** Ubuntu 25.04+ (Kernel 6.12 or newer recommended)
* **Hardware:** AMD Ryzen AI Max 3xx (Strix Halo / RDNA 3.5)
* **Docker & Compose** installed.

## 📦 Installation

### 1. Clone & Setup
```bash
git clone https://github.com/hec-ovi/comfyui-strix-docker.git
cd comfyui-strix-docker
```

### 2. Configure Permissions (Crucial!)

You must tell Docker your specific GPU group IDs.

```bash
# Find your IDs
getent group video | cut -d: -f3
getent group render | cut -d: -f3
```

Create a `.env` file from the template and paste your numbers:

```bash
cp .envTemplate .env
```

Edit the `.env` file:
```ini
# .env
VIDEO_GID=77    # <--- Replace with YOUR 'video' number
RENDER_GID=666  # <--- Replace with YOUR 'render' number
MODELS_PATH=/path/to/your/models # <--- Path to your models
```

### 3. Launch

```bash
docker compose up -d --build

```

Access the UI at: **http://localhost:8188**

## 📂 Model Management (What I recommend)

Map a local folder to the container so your models persist.
**Recommended Structure:**

```text
~/workspace/models/comfy/
├── checkpoints/  (Standard SD models)
├── unet/         (Flux.2 Diffusion Models)
├── clip/         (Flux.2 Text Encoders / T5)
├── vae/          (Flux.2 VAE)
└── loras/        (LoRAs)

```

*Just drop files here and hit "Refresh" in the UI.*

## 🔧 Technical Details

* **Base Image:** `ubuntu:rolling` (Necessary for Strix Halo glibc)
* **Python Manager:** `uv` (Astral)
* **Python Version:** 3.12 (Pinned via UV)
* **ROCm Target:** `gfx1151` (Strix Halo Native)
* **HSA Override:** Injected automatically via entrypoint.

## ⚠️ Troubleshooting

* **"Torch not compiled with CUDA enabled":** You are likely using an older Kernel or forgot the `.env` GIDs.
* **Permission Denied:** Ensure your user is part of `render` and `video` groups on the host.

---

*Verified Jan 2026 on Ryzen AI Max 300.*

---

## License

[MIT](LICENSE) for the build glue in this repository (Dockerfile, docker-compose.yml, entrypoint.sh, .envTemplate, README, scripts).

This repository does not redistribute ComfyUI source. The Dockerfile clones ComfyUI from `github.com/comfyanonymous/ComfyUI` at build time. ComfyUI is licensed under **GPL-3.0**. Any image built from this repository that bundles ComfyUI is therefore a derivative work of ComfyUI and is subject to GPL-3.0 when distributed. Building locally for personal use is fine; redistributing the resulting image, or any modified version of ComfyUI, requires complying with GPL-3.0.
