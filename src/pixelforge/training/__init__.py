"""LoRA eğitimi. Config + veri yükleme hafif; eğitim döngüsü ağır (lazy, [ml])."""

from pixelforge.training.config import TrainingConfig
from pixelforge.training.dataset import (
    flatten_rgba,
    load_examples,
    load_hf_zip_captioned,
)

__all__ = [
    "TrainingConfig",
    "flatten_rgba",
    "load_examples",
    "load_hf_zip_captioned",
    "train_lora",
]


def __getattr__(name: str):
    # torch/diffusers'ı yalnızca eğitim gerçekten istenince yükle.
    # NOT: modül adı 'trainer' (fonksiyon 'train_lora' ile çakışmasın diye) —
    # aksi halde `from training import train_lora` submodule'ü döndürür.
    if name == "train_lora":
        from pixelforge.training.trainer import train_lora

        return train_lora
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
