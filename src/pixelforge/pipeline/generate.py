"""SDXL + LoRA üretim sarmalayıcısı.

Bu modül torch/diffusers ister → sadece `[ml]` extra kurulu ortamda (Colab/GPU)
çalışır. Demo'daki Cell 2 + Cell 4 mantığı buraya, test edilebilir bir sınıfa taşındı.

Kullanım (Colab):
    from pixelforge.pipeline import PixelArtPipeline, GenerationRequest
    pipe = PixelArtPipeline.from_pretrained_default()
    res = pipe.generate(GenerationRequest(prompt="a brave knight sprite", seed=42))
    res.asset.save("knight.png")
"""

from __future__ import annotations

from pixelforge.eval.metrics import evaluate_asset
from pixelforge.pipeline.config import GenerationRequest, GenerationResult
from pixelforge.postprocess.pixelate import pixelate

BASE_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
LCM_LORA = "latent-consistency/lcm-lora-sdxl"
PIXEL_LORA = "nerijs/pixel-art-xl"


class PixelArtPipeline:
    """Diffusion pipeline + LoRA adapter'ları için ince sarmalayıcı."""

    def __init__(self, pipe):
        self._pipe = pipe

    @classmethod
    def from_pretrained_default(
        cls,
        *,
        use_lcm: bool = True,
        pixel_weight: float = 1.2,
        device: str = "cuda",
    ) -> "PixelArtPipeline":
        """Varsayılan SDXL + pixel-art-xl (+ opsiyonel LCM hız) kurulumu.

        use_lcm=False → LCM'i atlar; prompt sadakati için `steps=30,
        guidance_scale=7.5` gibi değerlerle kullan (bkz. GenerationRequest).
        """
        import torch
        from diffusers import DiffusionPipeline, LCMScheduler

        pipe = DiffusionPipeline.from_pretrained(
            BASE_MODEL, variant="fp16", torch_dtype=torch.float16
        )

        if use_lcm:
            pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)
            # LoRA'ları GPU'ya taşımadan ÖNCE yükle
            pipe.load_lora_weights(LCM_LORA, adapter_name="lcm")
            pipe.load_lora_weights(
                PIXEL_LORA,
                weight_name="pixel-art-xl.safetensors",
                adapter_name="pixel",
            )
            pipe.set_adapters(["lcm", "pixel"], adapter_weights=[1.0, pixel_weight])
        else:
            pipe.load_lora_weights(
                PIXEL_LORA,
                weight_name="pixel-art-xl.safetensors",
                adapter_name="pixel",
            )
            pipe.set_adapters(["pixel"], adapter_weights=[pixel_weight])

        pipe.to(device)
        return cls(pipe)

    def generate(self, req: GenerationRequest, *, device: str = "cuda") -> GenerationResult:
        """İstek → ham üretim → pixelate → metrik. Tam GenerationResult döner."""
        import torch

        gen = (
            torch.Generator(device).manual_seed(req.seed)
            if req.seed is not None
            else None
        )
        raw = self._pipe(
            prompt=req.full_prompt,
            negative_prompt=req.negative_prompt,
            num_inference_steps=req.steps,
            guidance_scale=req.guidance_scale,
            generator=gen,
        ).images[0]

        asset, preview = pixelate(raw, req.target_res, req.num_colors)
        metrics = evaluate_asset(asset, target_colors=req.num_colors)
        return GenerationResult(
            request=req, raw=raw, asset=asset, preview=preview, metrics=metrics
        )
