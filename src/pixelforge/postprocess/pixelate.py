"""Gerçek pixel art'ın oluştuğu adım.

LoRA tek başına "pixel gibi" görünen ama teknik olarak pixel OLMAYAN
(bulanık kenarlı, yüzlerce renkli) bir görüntü üretir. Buradaki adımlar onu
gerçek pixel art'a çevirir:
    1) hedef native çözünürlüğe küçült (blok boyutu = pixel_size)
    2) paleti sınırla (renk sayısını kıs)
    3) görüntüleme için nearest-neighbor ile büyüt
"""

from __future__ import annotations

from PIL import Image


def pixelate(
    img: Image.Image,
    target_res: int = 128,
    num_colors: int = 32,
) -> tuple[Image.Image, Image.Image]:
    """Ham görseli (asset, preview) çiftine çevirir.

    Args:
        img: ham diffusion çıktısı (RGB).
        target_res: çıktı pixel art'ın gerçek genişliği/yüksekliği (ör. 64, 128).
            küçük = daha 'chunky' retro görünüm.
        num_colors: palet büyüklüğü (pixel art için tipik 16-64).

    Returns:
        (asset, preview):
            asset   — küçük, temiz, kaydedilecek gerçek pixel asset (target_res²).
            preview — orijinal boyuta nearest-neighbor büyütülmüş önizleme.
    """
    if img.mode != "RGB":
        img = img.convert("RGB")
    w, h = img.size

    # 1) küçültme: LANCZOS ile alt-piksel gürültüsünü ortala
    small = img.resize((target_res, target_res), Image.LANCZOS)
    # 2) palet quantization (sınırlı renk = pixel art hissi)
    asset = small.quantize(colors=num_colors, method=Image.MEDIANCUT).convert("RGB")
    # 3) net kenarlı büyütme (ekranda görmek için)
    preview = asset.resize((w, h), Image.NEAREST)
    return asset, preview
