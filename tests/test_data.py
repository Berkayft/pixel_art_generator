"""data/ modülü testleri: schema kontratı + hazırlık fonksiyonları."""

import numpy as np
import pytest
from PIL import Image

from pixelforge.data import (
    DatasetManifest,
    ImageRecord,
    build_dataset,
    dedup,
    hflip,
    normalize,
    prepare_tile,
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


# ---- prepare_tile (değişken boyut + pad, ADR-11) ----

def test_prepare_tile_16px_tam_kat():
    out = prepare_tile(_blocky(block=4, blocks=4), target_res=512)   # 16px
    assert out.size == (512, 512) and out.mode == "RGBA"


def test_prepare_tile_18px_pad_ile():
    # 18px kaynak → 28×=504 → 512'ye pad. Interpolasyon yok → renk üremez.
    img = Image.fromarray(np.zeros((18, 18, 3), dtype=np.uint8), "RGB")
    img.putpixel((0, 0), (255, 0, 0))
    out = prepare_tile(img, target_res=512)
    assert out.size == (512, 512)


def test_prepare_tile_target_ustu_reddeder():
    big = Image.new("RGB", (600, 600))
    with pytest.raises(ValueError):
        prepare_tile(big, target_res=512)


# ---- build_dataset (uçtan uca) ----

def test_build_dataset_uctan_uca(tmp_path):
    # sentetik "pack": kök tile'lar + characters/ alt-klasörü
    src = tmp_path / "Tiles"
    (src / "characters").mkdir(parents=True)
    _blocky(colors=4).save(src / "tile_0000.png")
    _blocky(colors=6).save(src / "tile_0001.png")
    _blocky(colors=4).save(src / "tile_0002.png")           # tile_0000 ile aynı → dedup
    _blocky(colors=8).save(src / "characters" / "tile_0000.png")

    out = tmp_path / "processed"
    manifest, stats = build_dataset([src], out, trigger="pxforge", name="t")

    assert stats.found == 4 and stats.duplicates == 1        # bir tekrar elendi
    assert stats.kept == len(manifest.records)
    # kategori tag'i alt-klasörden gelir
    cats = {tuple(r.content_tags) for r in manifest.records}
    assert ("characters",) in cats and ("tile",) in cats
    # caption ADR-7: trigger + kategori
    rec = next(r for r in manifest.records if r.content_tags == ["characters"])
    assert rec.caption("pxforge") == "pxforge, characters"
    # manifest.json + görseller yazıldı
    assert (out / "manifest.json").exists()
    assert len(list((out / "images").glob("*.png"))) == stats.kept
