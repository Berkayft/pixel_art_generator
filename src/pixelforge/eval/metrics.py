"""Pixel-art kalite metrikleri. Hepsi saf numpy/PIL — hafif ve deterministik.

Her metrik 0..1 aralığında (yüksek = iyi) veya ham sayı döndürür. CLIP tabanlı
prompt-sadakati metriği (torch ister) ileride ayrı bir modüle eklenecek — bkz.
notebooks planı, Faz 1.
"""

from __future__ import annotations

import numpy as np
from PIL import Image


def _to_rgb_array(img: Image.Image) -> np.ndarray:
    if img.mode != "RGB":
        img = img.convert("RGB")
    return np.asarray(img, dtype=np.int16)  # int16: fark hesabında taşma olmasın


def color_count(img: Image.Image) -> int:
    """Görüntüdeki benzersiz RGB renk sayısı."""
    arr = _to_rgb_array(img).reshape(-1, 3)
    return int(np.unique(arr, axis=0).shape[0])


def palette_adherence(img: Image.Image, target_colors: int) -> float:
    """Palet hedefine uyum, 0..1. Renk sayısı hedefin altındaysa 1.0.

    Hedef aşılırsa target/actual ile cezalandırılır (çok renkli = 'sahte' pixel art).
    """
    if target_colors <= 0:
        raise ValueError("target_colors > 0 olmalı")
    n = color_count(img)
    return 1.0 if n <= target_colors else target_colors / n


def grid_alignment_score(img: Image.Image, block_size: int) -> float:
    """Görüntü, block_size × block_size düzgün bloklara ne kadar iyi ayrışıyor? 0..1.

    Gerçek pixel art'ta her blok tek düz renktir → blok-içi varyans ~0 → skor ~1.
    Bulanık/anti-aliased 'sahte' pixel art → yüksek blok-içi varyans → düşük skor.
    Bu metrik ham/preview görselde anlamlıdır (native asset'te block_size=1 → 1.0).
    """
    if block_size < 1:
        raise ValueError("block_size >= 1 olmalı")
    arr = _to_rgb_array(img)
    h, w, _ = arr.shape
    # tam bloklara sığacak şekilde kırp
    h2, w2 = (h // block_size) * block_size, (w // block_size) * block_size
    if h2 == 0 or w2 == 0:
        return 0.0
    arr = arr[:h2, :w2]
    # (bh, block, bw, block, 3) → blok-içi std
    blocks = arr.reshape(h2 // block_size, block_size, w2 // block_size, block_size, 3)
    intra_std = blocks.std(axis=(1, 3))          # her blok, her kanal için std
    mean_std = float(intra_std.mean())
    # 0 std → 1.0; büyük std → 0. 128 = maksimum makul yarı-aralık normalizasyonu.
    return max(0.0, 1.0 - mean_std / 128.0)


def edge_sharpness(img: Image.Image, soft_lo: int = 8, soft_hi: int = 64) -> float:
    """Kenarların keskinliği (anti-aliasing yokluğu), 0..1.

    Komşu piksel farkları ya ~0 (düz alan) ya da büyük (keskin kenar) olmalı.
    Ara değerdeki farklar (soft_lo..soft_hi) anti-aliasing halkalarıdır.
    Skor = sıfır-olmayan geçişler içinde 'yumuşak olmayan' oranı.
    """
    arr = _to_rgb_array(img)
    # yatay + dikey komşu farkları, kanal-ortalaması alınmış büyüklük
    dh = np.abs(arr[:, 1:] - arr[:, :-1]).mean(axis=2).ravel()
    dv = np.abs(arr[1:, :] - arr[:-1, :]).mean(axis=2).ravel()
    diffs = np.concatenate([dh, dv])
    transitions = diffs[diffs > soft_lo]          # sıfır-olmayan geçişler
    if transitions.size == 0:
        return 1.0                                # düz görüntü: yumuşak kenar yok
    soft = np.count_nonzero(transitions < soft_hi)
    return 1.0 - soft / transitions.size


def evaluate_asset(img: Image.Image, target_colors: int) -> dict[str, float]:
    """Bir native asset için metrik özeti. GenerationResult.metrics'e yazılır."""
    return {
        "color_count": float(color_count(img)),
        "palette_adherence": palette_adherence(img, target_colors),
        "edge_sharpness": edge_sharpness(img),
    }
