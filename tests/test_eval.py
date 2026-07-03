"""eval.metrics testleri: metriklerin 'iyi' ve 'kötü' pixel art'ı ayırt ettiğini doğrular."""

import numpy as np
from PIL import Image

from pixelforge.eval import (
    color_count,
    edge_sharpness,
    evaluate_asset,
    grid_alignment_score,
    palette_adherence,
)


def _blocky(block_size: int = 8, blocks: int = 8, colors: int = 4) -> Image.Image:
    """Kusursuz grid-hizalı, sınırlı paletli 'gerçek' pixel art."""
    rng = np.random.default_rng(0)
    palette = rng.integers(0, 256, size=(colors, 3), dtype=np.uint8)
    idx = rng.integers(0, colors, size=(blocks, blocks))
    small = palette[idx]                                   # (blocks, blocks, 3)
    arr = np.kron(small, np.ones((block_size, block_size, 1), dtype=np.uint8))
    return Image.fromarray(arr, "RGB")


def _noisy(size: int = 64) -> Image.Image:
    """Grid-hizasız, çok renkli 'sahte' pixel art (gürültü)."""
    rng = np.random.default_rng(1)
    arr = rng.integers(0, 256, size=(size, size, 3), dtype=np.uint8)
    return Image.fromarray(arr, "RGB")


def test_color_count_dogru_sayar():
    assert color_count(_blocky(colors=4)) <= 4
    assert color_count(_noisy()) > 100


def test_palette_adherence_hedefi_odullendirir():
    blocky = _blocky(colors=4)
    assert palette_adherence(blocky, target_colors=16) == 1.0     # altında → 1.0
    noisy = _noisy()
    assert palette_adherence(noisy, target_colors=16) < 0.5       # çok aşıyor


def test_grid_alignment_hizali_vs_gurultu():
    aligned = grid_alignment_score(_blocky(block_size=8), block_size=8)
    noisy = grid_alignment_score(_noisy(), block_size=8)
    assert aligned > 0.95        # kusursuz bloklar → ~1.0
    assert noisy < aligned       # gürültü belirgin şekilde daha düşük


def test_edge_sharpness_keskin_vs_bulanik():
    sharp = edge_sharpness(_blocky(block_size=8))
    # yumuşak geçişli görüntü: LANCZOS ile büyütülmüş küçük görsel
    blurry = _blocky(block_size=1, blocks=8).resize((256, 256), Image.LANCZOS)
    assert sharp > edge_sharpness(blurry)


def test_evaluate_asset_beklenen_anahtarlar():
    m = evaluate_asset(_blocky(), target_colors=16)
    assert set(m) == {"color_count", "palette_adherence", "edge_sharpness"}
    assert all(isinstance(v, float) for v in m.values())
