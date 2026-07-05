"""Dataset hazırlık fonksiyonları — saf, deterministik, GPU'suz.

ADR bağları:
- ADR-11: augmentation'da rotation/keyfi-scale YASAK. Sadece flip + int-kat scale burada.
- ADR-8: kalite > nicelik → validate_pixel_asset ile "temiz pixel art mı" QA.
- eval/ reuse: dataset QA'sı için üretim metriklerini tekrar kullanırız.
"""

from __future__ import annotations

import hashlib

from PIL import Image

from pixelforge.eval.metrics import color_count, edge_sharpness


def image_hash(img: Image.Image) -> str:
    """Dedup için içerik hash'i (mod-bağımsız, ham piksel baytları)."""
    return hashlib.sha1(img.convert("RGB").tobytes()).hexdigest()


def dedup(images: list[Image.Image]) -> list[int]:
    """Benzersiz görsellerin indekslerini döndürür (ilk görüleni tutar)."""
    seen: set[str] = set()
    keep: list[int] = []
    for i, img in enumerate(images):
        h = image_hash(img)
        if h not in seen:
            seen.add(h)
            keep.append(i)
    return keep


def validate_pixel_asset(
    img: Image.Image,
    *,
    max_colors: int = 64,
    min_sharpness: float = 0.5,
) -> tuple[bool, dict[str, float]]:
    """Kaynak görsel 'temiz pixel art' mı? (ADR-8 kalite kapısı, eval/ reuse).

    Bulanık/anti-aliased veya aşırı-renkli görselleri eğitime sokmadan eler.
    Returns (geçti_mi, metrikler).
    """
    metrics = {
        "color_count": float(color_count(img)),
        "edge_sharpness": edge_sharpness(img),
    }
    ok = metrics["color_count"] <= max_colors and metrics["edge_sharpness"] >= min_sharpness
    return ok, metrics


def normalize(img: Image.Image, native_res: int, train_res: int) -> Image.Image:
    """Görseli eğitim çözünürlüğüne getir: kare'ye pad + NEAREST int-kat upscale.

    ADR-11: interpolasyonsuz (NEAREST) ve tam-sayı-kat → pixel grid korunur.
    """
    if train_res % native_res != 0:
        raise ValueError("train_res, native_res'in tam katı olmalı (ADR-11)")
    img = img.convert("RGBA")
    # kare değilse şeffaf pad (grid'i bozmadan ortala)
    w, h = img.size
    side = max(w, h)
    if (w, h) != (side, side):
        canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        canvas.paste(img, ((side - w) // 2, (side - h) // 2))
        img = canvas
    # önce native_res'e (gerekiyorsa) NEAREST küçült/büyüt, sonra int-kat upscale
    if img.size != (native_res, native_res):
        img = img.resize((native_res, native_res), Image.NEAREST)
    return img.resize((train_res, train_res), Image.NEAREST)


def hflip(img: Image.Image) -> Image.Image:
    """İzinli augmentation (ADR-11): yatay flip. Grid'i bozmaz."""
    return img.transpose(Image.FLIP_LEFT_RIGHT)


def prepare_tile(img: Image.Image, target_res: int = 512) -> Image.Image:
    """Değişken boyutlu bir tile'ı target_res kareye getir (ADR-11 uyumlu).

    Boyutu algılar → kareye şeffaf pad → NEAREST **integer-kat** upscale → target_res'e
    şeffaf pad. Hiçbir adımda interpolasyon yok, tam-sayı-kat dışında ölçekleme yok →
    pixel grid korunur. 16px → 32×=512 tam; 18px → 28×=504 sonra 512'ye pad.
    """
    img = img.convert("RGBA")
    w, h = img.size
    side = max(w, h)
    if side > target_res:
        raise ValueError(f"tile ({side}px) target_res ({target_res}) üstünde")
    if (w, h) != (side, side):
        sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        sq.paste(img, ((side - w) // 2, (side - h) // 2))
        img = sq
    factor = max(1, target_res // side)
    up = side * factor
    img = img.resize((up, up), Image.NEAREST)
    if up != target_res:
        canvas = Image.new("RGBA", (target_res, target_res), (0, 0, 0, 0))
        canvas.paste(img, ((target_res - up) // 2, (target_res - up) // 2))
        img = canvas
    return img
