"""LoRA eğitimi. Config + veri yükleme hafif; eğitim döngüsü ağır (lazy, [ml])."""

from pixelforge.training.config import TrainingConfig
from pixelforge.training.dataset import flatten_rgba, load_examples

__all__ = ["TrainingConfig", "flatten_rgba", "load_examples", "train_lora"]


def __getattr__(name: str):
    # torch/diffusers'ı yalnızca eğitim gerçekten istenince yükle.
    if name == "train_lora":
        from pixelforge.training.train_lora import train_lora

        return train_lora
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
