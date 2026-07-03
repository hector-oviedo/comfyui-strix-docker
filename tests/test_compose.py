"""Sanity-check docker-compose.yml: the GPU wiring Strix Halo needs is present.

Text-based so it runs with only pytest. If Docker is available, also run
`docker compose config -q` locally, which fully validates interpolation/schema.
"""
from pathlib import Path

COMPOSE = (Path(__file__).resolve().parent.parent / "docker-compose.yml").read_text()


def test_passes_both_gpu_device_nodes():
    assert "/dev/kfd:/dev/kfd" in COMPOSE, "ROCm/HIP needs the KFD node"
    assert "/dev/dri:/dev/dri" in COMPOSE, "needs the DRI render node"


def test_maps_gpu_group_ids_from_env():
    assert "${VIDEO_GID}" in COMPOSE
    assert "${RENDER_GID}" in COMPOSE


def test_exposes_comfyui_port():
    assert "8188:8188" in COMPOSE


def test_mounts_models_from_env_path():
    assert "${MODELS_PATH}:/app/ComfyUI/models" in COMPOSE
