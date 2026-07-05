"""Manifest → (görsel, caption) yükleme. Saf & test edilebilir (torch'suz).

Ağır torch `Dataset` sarmalayıcısı train_lora.py'de; buradaki fonksiyonlar veriyi
hazırlayan deterministik çekirdek. RGBA→RGB flatten burada (SD RGB'de eğitir).
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from pixelforge.data.schema import DatasetManifest

_BG_COLORS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "gray": (128, 128, 128),
}


def flatten_rgba(img: Image.Image, background: str = "white") -> Image.Image:
    """Şeffaf (RGBA) görseli düz arka plana yapıştırıp RGB'ye çevir.

    Kenney tile'ları şeffaf; SD RGB'de eğitir → şeffaflık bir renge sabitlenmeli.
    (Tur 4 bulgusu: arka plan kompozisyonu fg/bg ayrımına da yardım eder.)
    """
    if background not in _BG_COLORS:
        raise ValueError(f"bilinmeyen background: {background} ({list(_BG_COLORS)})")
    img = img.convert("RGBA")
    bg = Image.new("RGB", img.size, _BG_COLORS[background])
    bg.paste(img, mask=img.split()[3])   # alpha kanalı maske
    return bg


def resolve_dataset_dir(dataset: str, revision: str = "main") -> Path:
    """Yerel dizinse doğrudan döner; HF dataset id'siyse snapshot indirir ([data] extra)."""
    p = Path(dataset)
    if (p / "manifest.json").exists():
        return p
    from huggingface_hub import snapshot_download  # lazy: [data]

    local = snapshot_download(repo_id=dataset, repo_type="dataset", revision=revision)
    return Path(local)


def load_examples(
    dataset: str,
    *,
    revision: str = "main",
    background: str = "white",
    resolution: int = 512,
) -> list[tuple[Image.Image, str]]:
    """(RGB görsel, caption) çiftlerini döndürür. caption = manifest.trigger + içerik (ADR-7)."""
    root = resolve_dataset_dir(dataset, revision)
    manifest = DatasetManifest.model_validate_json((root / "manifest.json").read_text())

    out: list[tuple[Image.Image, str]] = []
    for rec in manifest.records:
        img = Image.open(root / rec.path)
        img = flatten_rgba(img, background)
        if img.size != (resolution, resolution):
            img = img.resize((resolution, resolution), Image.NEAREST)
        out.append((img, rec.caption(manifest.trigger)))
    return out
