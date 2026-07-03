"""pixelforge — AI ile pixel art asset üretimi.

Katmanlar:
    pipeline/    : model yükleme + inference (ağır, [ml] extra ister)
    postprocess/ : ham görseli gerçek pixel art'a çevirir (hafif)
    eval/        : otomatik pixel-art kalite metrikleri (hafif)

Ağır ML bağımlılıkları (torch/diffusers) yalnızca `pipeline` içinde ve
lazy import ile yüklenir; böylece postprocess + eval GPU'suz kullanılabilir.
"""

__version__ = "0.0.1"

from pixelforge.pipeline.config import GenerationRequest, GenerationResult

__all__ = ["GenerationRequest", "GenerationResult", "__version__"]
