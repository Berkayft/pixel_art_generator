"""postprocess.pixelate testleri."""

from PIL import Image

from pixelforge.postprocess import pixelate


def _gradient(size: int = 256) -> Image.Image:
    """Bulanık, çok renkli bir kaynak (ham diffusion çıktısını taklit eder)."""
    img = Image.new("RGB", (size, size))
    px = img.load()
    for y in range(size):
        for x in range(size):
            px[x, y] = (x % 256, y % 256, (x + y) % 256)
    return img


def test_asset_boyutu_target_res():
    asset, preview = pixelate(_gradient(256), target_res=64, num_colors=16)
    assert asset.size == (64, 64)          # native asset target_res kadar
    assert preview.size == (256, 256)      # preview orijinal boyuta döner


def test_palet_num_colors_asilmaz():
    from pixelforge.eval import color_count

    asset, _ = pixelate(_gradient(256), target_res=64, num_colors=16)
    assert color_count(asset) <= 16        # quantization hedefi tutmalı


def test_gri_tonlamali_giris_rgb_e_donusur():
    gray = Image.new("L", (128, 128), 128)
    asset, preview = pixelate(gray, target_res=32, num_colors=8)
    assert asset.mode == "RGB"
    assert asset.size == (32, 32)
