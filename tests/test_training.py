"""training/ hafif katman testleri: config kontratı + veri yükleme (torch'suz)."""

import numpy as np
import pytest
from PIL import Image

from pixelforge.training import TrainingConfig, flatten_rgba, load_examples


def test_config_run_name_ve_varsayilanlar():
    cfg = TrainingConfig()
    assert cfg.base_model.endswith("stable-diffusion-v1-5")   # ADR-6: SD1.5
    assert cfg.rank == 16
    assert "r16" in cfg.run_name and "s1000" in cfg.run_name


def test_flatten_rgba_alfa_kaldirir_arka_plan_uygular():
    img = Image.new("RGBA", (4, 4), (0, 0, 0, 0))          # tamamen şeffaf
    img.putpixel((0, 0), (255, 0, 0, 255))                 # bir opak kırmızı piksel
    out = flatten_rgba(img, "white")
    assert out.mode == "RGB"
    assert out.getpixel((0, 0)) == (255, 0, 0)             # opak piksel korunur
    assert out.getpixel((1, 1)) == (255, 255, 255)         # şeffaf → beyaz


def test_flatten_bilinmeyen_background_reddeder():
    with pytest.raises(ValueError):
        flatten_rgba(Image.new("RGBA", (2, 2)), "purple")


def _write_mini_dataset(tmp_path):
    """manifest.json + 2 RGBA görsel içeren sahte processed dataset."""
    (tmp_path / "images").mkdir()
    for i in range(2):
        arr = np.zeros((512, 512, 4), dtype=np.uint8)
        arr[..., 3] = 255
        Image.fromarray(arr, "RGBA").save(tmp_path / "images" / f"t{i}.png")
    manifest = {
        "name": "mini", "trigger": "pxforge", "native_res": 16, "train_res": 512,
        "records": [
            {"path": "images/t0.png", "split": "train", "content_tags": ["dungeon"]},
            {"path": "images/t1.png", "split": "train", "content_tags": ["town"]},
        ],
    }
    import json
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))


def test_load_examples_yerel_dataset(tmp_path):
    _write_mini_dataset(tmp_path)
    ex = load_examples(str(tmp_path), background="white", resolution=512)
    assert len(ex) == 2
    imgs, caps = zip(*ex)
    assert all(im.mode == "RGB" and im.size == (512, 512) for im in imgs)
    # caption ADR-7: trigger + içerik
    assert "pxforge, dungeon" in caps and "pxforge, town" in caps


def test_build_from_zip_csv_lpc_tarzi(tmp_path):
    """LPC-tarzı captioned csv+zip: subsample, basename eşleme, caption olduğu gibi."""
    import csv as csvmod
    import zipfile

    from pixelforge.training.dataset import _build_from_zip_csv

    # 3 görselli zip (root'ta char_*.png)
    zip_path = tmp_path / "train.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for i in range(3):
            p = tmp_path / f"char_{i}.png"
            arr = np.zeros((64, 64, 4), dtype=np.uint8)
            arr[..., 3] = 255
            Image.fromarray(arr, "RGBA").save(p)
            zf.write(p, f"char_{i}.png")
    # csv (image_path bir alt-yol içerse de basename ile eşleşmeli)
    csv_path = tmp_path / "captions.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csvmod.writer(fh)
        w.writerow(["image_path", "text"])
        for i in range(3):
            w.writerow([f"images/char_{i}.png", f"lpc-style character number {i}"])

    ex = _build_from_zip_csv(csv_path, zip_path, subsample=2, seed=1, resolution=512)
    assert len(ex) == 2                                   # subsample uygulandı
    imgs, caps = zip(*ex)
    assert all(im.mode == "RGB" and im.size == (512, 512) for im in imgs)
    assert all(c.startswith("lpc-style character") for c in caps)   # caption olduğu gibi
