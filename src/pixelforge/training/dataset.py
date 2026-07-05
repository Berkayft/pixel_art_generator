"""Manifest → (görsel, caption) yükleme. Saf & test edilebilir (torch'suz).

Ağır torch `Dataset` sarmalayıcısı train_lora.py'de; buradaki fonksiyonlar veriyi
hazırlayan deterministik çekirdek. RGBA→RGB flatten burada (SD RGB'de eğitir).
"""

from __future__ import annotations

import csv as _csv
import random
import zipfile
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
        img = _finalize(Image.open(root / rec.path), background, resolution)
        out.append((img, rec.caption(manifest.trigger)))
    return out


def _finalize(img: Image.Image, background: str, resolution: int) -> Image.Image:
    """RGBA flatten + (gerekiyorsa) NEAREST resize → eğitim tensörüne hazır RGB."""
    img = flatten_rgba(img, background)
    if img.size != (resolution, resolution):
        img = img.resize((resolution, resolution), Image.NEAREST)
    return img


def _build_from_zip_csv(
    csv_path: str | Path,
    zip_path: str | Path,
    *,
    subsample: int | None = None,
    seed: int = 42,
    background: str = "white",
    resolution: int = 512,
    image_col: str = "image_path",
    text_col: str = "text",
) -> list[tuple[Image.Image, str]]:
    """captions.csv + images.zip → (RGB, caption). LPC-tarzı captioned dataset çekirdeği.

    Caption zaten stil çıpasını içerir (ör. 'hard edges, no anti-aliasing') → trigger eklenmez.
    """
    with open(csv_path, encoding="utf-8") as fh:
        rows = list(_csv.DictReader(fh))
    if subsample and subsample < len(rows):
        rows = random.Random(seed).sample(rows, subsample)   # seed → reproducible alt-örnek

    out: list[tuple[Image.Image, str]] = []
    with zipfile.ZipFile(zip_path) as zf:
        names = {Path(n).name: n for n in zf.namelist() if n.lower().endswith(".png")}
        for r in rows:
            entry = names.get(Path(r[image_col]).name)
            if entry is None:
                continue
            with zf.open(entry) as fh:
                img = Image.open(fh)
                img.load()
            out.append((_finalize(img, background, resolution), r[text_col]))
    return out


def load_hf_zip_captioned(
    repo: str,
    *,
    caption_csv: str,
    images_zip: str = "images/train.zip",
    revision: str = "main",
    subsample: int | None = None,
    seed: int = 42,
    background: str = "white",
    resolution: int = 512,
) -> list[tuple[Image.Image, str]]:
    """HF dataset'ten (csv+zip) captioned örnekler. LPC 4-view için ([data] extra)."""
    from huggingface_hub import hf_hub_download

    csv_path = hf_hub_download(repo, caption_csv, repo_type="dataset", revision=revision)
    zip_path = hf_hub_download(repo, images_zip, repo_type="dataset", revision=revision)
    return _build_from_zip_csv(
        csv_path, zip_path, subsample=subsample, seed=seed,
        background=background, resolution=resolution,
    )
