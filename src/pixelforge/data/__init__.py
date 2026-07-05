"""Dataset hazırlığı (hafif, GPU'suz). training/ ve eval/ bunu kullanır.

Bağımlılık yönü: data → eval (ikisi de hafif leaf). torch import etmez.
"""

from pixelforge.data.ingest import build_dataset
from pixelforge.data.prepare import (
    dedup,
    hflip,
    image_hash,
    normalize,
    prepare_tile,
    validate_pixel_asset,
)
from pixelforge.data.schema import DatasetManifest, ImageRecord

__all__ = [
    "DatasetManifest",
    "ImageRecord",
    "validate_pixel_asset",
    "normalize",
    "prepare_tile",
    "dedup",
    "hflip",
    "image_hash",
    "build_dataset",
]
