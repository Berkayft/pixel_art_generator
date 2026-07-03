"""Otomatik pixel-art kalite metrikleri (ground-truth gerektirmez, GPU'suz).

Bu paket, "iyi pixel art nedir" sorusunu ölçülebilir kılar — bir demo'yu
gerçek ML projesinden ayıran şey budur. Regresyonları CI'da yakalamak ve
experiment'leri (W&B/MLflow) kıyaslamak için kullanılır.
"""

from pixelforge.eval.metrics import (
    color_count,
    edge_sharpness,
    evaluate_asset,
    grid_alignment_score,
    palette_adherence,
)

__all__ = [
    "color_count",
    "palette_adherence",
    "grid_alignment_score",
    "edge_sharpness",
    "evaluate_asset",
]
