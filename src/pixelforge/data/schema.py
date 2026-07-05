"""Dataset kontratları — training verisi bu tiplerle tanımlanır.

Tasarım ADR'lere dayanır:
- ADR-5: stil taksonomisi (outline/çözünürlük/dithering/projeksiyon/detay) dataset
  seviyesinde metadata; per-record içerik tag'leri ayrı.
- ADR-7: caption = trigger + içerik tag'leri. **Stil caption'lanmaz** (trigger absorbe eder).
- Manifest git'e girebilir (küçük, metin); görseller HF Hub'da (ADR-8).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# ADR-5 taksonomi eksenleri — dataset'in stilini tanımlar (caption'a girmez, metadata).
StyleAxes = dict[str, str]  # ör. {"outline": "none", "resolution": "16px", "dithering": "no"}


class ImageRecord(BaseModel):
    """Tek bir eğitim görseli + içerik tag'leri (stil DEĞİL)."""

    path: str                              # dataset köküne göreli
    split: str = "train"                   # train | val
    content_tags: list[str] = Field(default_factory=list)  # ör. ["knight", "side view"]

    def caption(self, trigger: str) -> str:
        """ADR-7: caption = trigger + içerik tag'leri (virgül-ayrık, doğal dil değil)."""
        parts = [trigger, *self.content_tags]
        return ", ".join(p.strip() for p in parts if p.strip())


class DatasetManifest(BaseModel):
    """Bir LoRA dataset'inin tam tanımı. Reprodüksiyon için versiyonlanır."""

    name: str
    trigger: str                           # benzersiz token, ör. "pxforge"
    source: str = ""                       # ör. "Kenney: Tiny Dungeon (CC0)"
    license: str = "CC0"
    style_axes: StyleAxes = Field(default_factory=dict)   # ADR-5 metadata
    native_res: int = 16                   # kaynak pixel çözünürlüğü
    train_res: int = 512                   # eğitime beslenecek çözünürlük (int-kat upscale)
    records: list[ImageRecord] = Field(default_factory=list)

    @property
    def upscale_factor(self) -> int:
        """train_res / native_res — ADR-11: tam sayı olmalı (grid bozulmasın)."""
        if self.train_res % self.native_res != 0:
            raise ValueError(
                f"train_res ({self.train_res}) native_res ({self.native_res}) "
                "katı olmalı — ADR-11: non-integer scale grid'i bozar"
            )
        return self.train_res // self.native_res
