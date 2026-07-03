"""Guard the build invariants of the Strix Halo (gfx1151) Dockerfile.

These are config tests, not a build: they assert the exact things that make the
image actually use the GPU on gfx1151, so a careless edit (floating torch, the
wrong base image, a mismatched ROCm ABI set, a dropped stability env) fails the
test suite instead of failing silently on the box. They need only pytest, no Docker.
"""
import re
from pathlib import Path

DOCKERFILE = Path(__file__).resolve().parent.parent / "Dockerfile"
TEXT = DOCKERFILE.read_text()

# Active (non-comment) lines only, so prose in comments never satisfies an assert.
CODE = "\n".join(
    ln for ln in TEXT.splitlines() if ln.strip() and not ln.lstrip().startswith("#")
)


def test_base_is_ubuntu_2604_lts_not_rolling():
    assert re.search(r"^FROM\s+ubuntu:26\.04\b", CODE, re.MULTILINE), "base must be ubuntu:26.04"
    assert "ubuntu:rolling" not in CODE, "must not use the old ubuntu:rolling base"


def test_uses_therock_nightly_index_not_amd_prerelease():
    assert "https://rocm.nightlies.amd.com/v2/gfx1151/" in CODE, "must pin TheRock gfx1151 index"
    assert "rocm.prereleases.amd.com" not in CODE, "must drop the old AMD prerelease index"


def test_torch_triple_is_pinned_and_abi_coherent():
    # No floating prerelease install: versions must be pinned with ==, not `--pre torch ...`.
    assert "--pre" not in CODE, "must not float a prerelease torch; pin exact versions"

    def ver(arg):
        m = re.search(rf"^ARG\s+{arg}=(\S+)", CODE, re.MULTILINE)
        assert m, f"missing ARG {arg}"
        return m.group(1)

    torch, vision, audio = ver("TORCH_VER"), ver("VISION_VER"), ver("AUDIO_VER")
    assert torch.startswith("2.9.1+rocm7.13.0a"), torch
    assert vision.startswith("0.24.0+rocm7.13.0a"), vision
    assert audio.startswith("2.9.0+rocm7.13.0a"), audio

    # The +rocm tag (the reproducible invariant) must be identical across all three.
    def tag(v):
        return v.split("+", 1)[1]

    assert tag(torch) == tag(vision) == tag(audio), (
        f"ABI mismatch: torch={tag(torch)} vision={tag(vision)} audio={tag(audio)}"
    )

    # The install line consumes the exclusive index and the pinned versions.
    assert "--index-url ${ROCM_INDEX}" in CODE
    for arg in ("TORCH_VER", "VISION_VER", "AUDIO_VER"):
        assert f"${{{arg}}}" in CODE, f"install must use ${{{arg}}}"


def test_build_fails_on_cpu_only_torch():
    # The guard line turns a silent CPU fallback into a hard build failure.
    assert "assert 'rocm' in torch.__version__" in CODE


def test_python_312_via_uv():
    assert re.search(r"uv venv .* --python 3\.12", CODE), "must build a 3.12 venv with uv"


def test_strix_halo_runtime_env_present():
    assert "HSA_OVERRIDE_GFX_VERSION=11.5.1" in CODE, "ISA override for Strix Halo"
    assert "HSA_ENABLE_SDMA=0" in CODE, "unified-memory stability fix"
    assert "HSA_USE_SVM=0" in CODE, "unified-memory stability fix"
