"""Modüller arası kontratlar.

Bu tipler pipeline / postprocess / eval / serving arasındaki *tek* arayüz.
Bir agent tek modülü değiştirdiğinde bu şemalara dokunmadığı sürece
diğer modüller kırılmaz — repo'nun "patlamamasının" temeli budur.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# pixel art için makul negatif prompt (demo'dan taşındı)
DEFAULT_NEGATIVE = (
    "3d render, realistic, photo, blurry, anti-aliased, "
    "smooth gradient, soft shading"
)


class GenerationRequest(BaseModel):
    """Bir asset üretim isteği. Serileştirilebilir → config/queue/log'a yazılır."""

    prompt: str
    negative_prompt: str = DEFAULT_NEGATIVE
    # üretim
    steps: int = Field(8, ge=1, le=100)
    guidance_scale: float = Field(1.5, ge=0.0, le=20.0)
    seed: int | None = None
    # post-processing (gerçek pixel art bu adımda oluşur)
    target_res: int = Field(128, ge=8, le=512, description="native pixel çözünürlük")
    num_colors: int = Field(32, ge=2, le=256, description="palet büyüklüğü")

    @property
    def full_prompt(self) -> str:
        """'pixel' anahtar kelimesi stili tetikler."""
        return f"pixel, {self.prompt}"


class GenerationResult(BaseModel):
    """Üretim çıktısı + ölçülen metrikler. PIL görselleri model dışında tutulur."""

    model_config = {"arbitrary_types_allowed": True}

    request: GenerationRequest
    # PIL.Image nesneleri (serileştirme dışı) — runtime taşıyıcı
    raw: object = None       # ham diffusion çıktısı (büyük, bulanık)
    asset: object = None     # gerçek pixel asset (küçük, temiz) — kaydedilecek olan
    preview: object = None   # nearest-neighbor büyütülmüş önizleme
    metrics: dict[str, float] = Field(default_factory=dict)
