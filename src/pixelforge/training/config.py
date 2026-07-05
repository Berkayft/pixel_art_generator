"""Eğitim kontratı — bir LoRA run'ının TAM tanımı.

MLOps: reproducibility'nin temeli. Bir run bu config + seed ile tekrar üretilebilir.
Serileştirilebilir → W&B'ye loglanır, çıktıyla birlikte kaydedilir, HF Hub'a gider.
Şema değişince notebook + train_lora güncellenmeli (kontrat kuralı).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class TrainingConfig(BaseModel):
    """SD1.5 LoRA eğitim ayarları. Varsayılanlar ADR-6 (SD1.5, düz LoRA) uyumlu."""

    # ---- veri ----
    dataset: str = "BerkayFT/pixelforge-kenney-tiny-v1"   # HF id veya yerel dizin
    dataset_revision: str = "main"                        # reproducibility: versiyon sabitle
    trigger: str = "pxforge"
    resolution: int = 512
    background: str = "white"                             # RGBA flatten arka planı

    # ---- model (ADR-6: önce SD1.5) ----
    base_model: str = "runwayml/stable-diffusion-v1-5"

    # ---- LoRA (ADR-6: baseline düz LoRA) ----
    rank: int = Field(16, ge=1)
    lora_alpha: int = 16

    # ---- optimizasyon ----
    learning_rate: float = 1e-4
    train_steps: int = Field(1000, ge=1)
    batch_size: int = 1
    grad_accum: int = 4
    seed: int = 42

    # ---- çıktı + tracking ----
    output_dir: str = "outputs/lora"
    sample_prompts: list[str] = Field(
        default_factory=lambda: [
            "pxforge, dungeon, a treasure chest",
            "pxforge, town, a small house",
        ]
    )
    sample_every: int = 250                               # N adımda bir örnek + eval
    wandb_project: str | None = None                      # None → tracking kapalı
    push_to_hub_repo: str | None = None                   # None → Hub'a push yok

    @property
    def run_name(self) -> str:
        return f"sd15-lora-r{self.rank}-lr{self.learning_rate:g}-s{self.train_steps}"
