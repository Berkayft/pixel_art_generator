"""Generation pipeline. Ağır bağımlılıklar (torch/diffusers) lazy yüklenir."""

from pixelforge.pipeline.config import (
    DEFAULT_NEGATIVE,
    GenerationRequest,
    GenerationResult,
)

__all__ = [
    "DEFAULT_NEGATIVE",
    "GenerationRequest",
    "GenerationResult",
    "PixelArtPipeline",
]


def __getattr__(name: str):
    # PixelArtPipeline'ı yalnızca gerçekten istenince import et → torch'suz
    # ortamda `import pixelforge` çökmESİN.
    if name == "PixelArtPipeline":
        from pixelforge.pipeline.generate import PixelArtPipeline

        return PixelArtPipeline
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
