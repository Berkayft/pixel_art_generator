"""data/ modülü testleri: schema kontratı + hazırlık fonksiyonları."""

import numpy as np
import pytest
from PIL import Image

from pixelforge.data import (
    DatasetManifest,
    ImageRecord,
    dedup,
    hflip,
    normalize,
    validate_pixel_asset,
)


def _blocky(block: int = 8, blocks: int = 4, colors: int = 4) -> Image.Image:
    rng = np.random.default_rng(0)
    palette = rng.integers(0, 256, size=(colors, 3), dtype=np.uint8)
    idx = rng.integers(0, colors, size=(blocks, blocks))
    arr = np.kron(palette[idx], np.ones((block, block, 1), dtype=np.uint8))
    return Image.fromarray(arr, "RGB")


# ---- schema / caption (ADR-7) ----

def test_caption_trigger_plus_content_stil_yazilmaz():
    r = ImageRecord(path="a.png", content_tags=["knight", "side view"])
    # caption trigger + içerik; stil (ör. 'pixel art') caption'a girmez
    assert r.caption("pxforge") == "pxforge, knight, side view"


def test_caption_bos_taglerle():
    r = ImageRecord(path="a.png")
    assert r.caption("pxforge") == "pxforge"


def test_upscale_factor_integer_zorunlu_adr11():
    m = DatasetManifest(name="t", trigger="px", native_res=16, train_res=512)
    assert m.upscale_factor == 32
    bad = DatasetManifest(name="t", trigger="px", native_res=16, train_res=500)
    with pytest.raises(ValueError):
        _ = bad.upscale_factor


# ---- prepare ----

def test_validate_temiz_vs_bulanik():
    clean = _blocky()
    ok, m = validate_pixel_asset(clean, max_colors=64)
    assert ok and m["color_count"] <= 64
    # bulanık/çok-renkli: LANCZOS ile büyütülmüş → yumuşak kenar + çok renk
    blurry = _blocky(block=1, blocks=8).resize((256, 256), Image.LANCZOS)
    ok2, _ = validate_pixel_asset(blurry)
    assert not ok2


def test_dedup_ayni_gorseli_teker_tutar():
    a, b = _blocky(), _blocky()          # aynı seed → aynı görsel
    c = _blocky(colors=8)                # farklı
    keep = dedup([a, b, c])
    assert keep == [0, 2]


def test_normalize_int_kat_nearest_ve_kare():
    img = _blocky(block=4, blocks=4)     # 16x16
    out = normalize(img, native_res=16, train_res=512)
    assert out.size == (512, 512)
    # NEAREST int-kat → yeni ara renk oluşmamalı (grid korunur, ADR-11)
    assert len(out.convert("RGB").getcolors(maxcolors=100000)) <= 4 + 1  # +1 pad şeffaflığı


def test_normalize_non_integer_reddeder():
    with pytest.raises(ValueError):
        normalize(_blocky(), native_res=16, train_res=500)


def test_hflip_boyut_korur():
    img = _blocky()
    assert hflip(img).size == img.size
