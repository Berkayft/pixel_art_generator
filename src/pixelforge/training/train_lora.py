"""SD1.5 LoRA eğitim döngüsü (AĞIR: torch/diffusers/peft, [ml] extra → Colab/GPU).

Standart diffusers LoRA reçetesi + MLOps katmanı:
- reproducibility: TrainingConfig + seed her şeyi belirler, config loglanır
- experiment tracking: W&B (opsiyonel) — loss + örnek görsel + eval metrikleri
- eval loop kapanışı: periyodik örnek üret → postprocess → eval/ metrikleri
- model registry: LoRA → HF Hub

Yerelde çalışmaz (torch yok); mantık burada, notebook sadece çağırır. İlk Colab
run'ında küçük sürüm-pürüzleri olabilir — çıktıya göre ayarlanır.
"""

from __future__ import annotations

from pathlib import Path

from pixelforge.eval.metrics import evaluate_asset
from pixelforge.postprocess.pixelate import pixelate
from pixelforge.training.config import TrainingConfig
from pixelforge.training.dataset import load_examples

# SD1.5 UNet attention projeksiyonları — LoRA buralara takılır
_LORA_TARGETS = ["to_q", "to_k", "to_v", "to_out.0"]


def train_lora(cfg: TrainingConfig) -> str:
    """Bir SD1.5 LoRA eğitir, kaydeder (ve istenirse Hub'a push eder). Çıktı dizinini döner."""
    import torch
    import torch.nn.functional as F
    from diffusers import (
        AutoencoderKL,
        DDPMScheduler,
        StableDiffusionPipeline,
        UNet2DConditionModel,
    )
    from peft import LoraConfig
    from peft.utils import get_peft_model_state_dict
    from torch.utils.data import DataLoader, Dataset
    from torchvision import transforms
    from transformers import CLIPTextModel, CLIPTokenizer

    device = "cuda" if torch.cuda.is_available() else "cpu"
    weight_dtype = torch.float16 if device == "cuda" else torch.float32
    torch.manual_seed(cfg.seed)
    out_dir = Path(cfg.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- W&B (opsiyonel) ----
    run = None
    if cfg.wandb_project:
        import wandb

        run = wandb.init(project=cfg.wandb_project, name=cfg.run_name, config=cfg.model_dump())

    # ---- veri (hafif çekirdek) → torch Dataset ----
    examples = load_examples(
        cfg.dataset, revision=cfg.dataset_revision,
        background=cfg.background, resolution=cfg.resolution,
    )
    tokenizer = CLIPTokenizer.from_pretrained(cfg.base_model, subfolder="tokenizer")
    img_tf = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize([0.5], [0.5])]  # → [-1, 1]
    )

    class _DS(Dataset):
        def __len__(self):
            return len(examples)

        def __getitem__(self, i):
            img, caption = examples[i]
            ids = tokenizer(
                caption, padding="max_length", truncation=True,
                max_length=tokenizer.model_max_length, return_tensors="pt",
            ).input_ids[0]
            return {"pixel_values": img_tf(img), "input_ids": ids}

    loader = DataLoader(_DS(), batch_size=cfg.batch_size, shuffle=True, drop_last=True)

    # ---- modeller ----
    noise_scheduler = DDPMScheduler.from_pretrained(cfg.base_model, subfolder="scheduler")
    text_encoder = CLIPTextModel.from_pretrained(cfg.base_model, subfolder="text_encoder")
    vae = AutoencoderKL.from_pretrained(cfg.base_model, subfolder="vae")
    unet = UNet2DConditionModel.from_pretrained(cfg.base_model, subfolder="unet")

    # base'i dondur; sadece LoRA eğitilir (ADR-6)
    text_encoder.requires_grad_(False)
    vae.requires_grad_(False)
    unet.requires_grad_(False)
    unet.add_adapter(LoraConfig(
        r=cfg.rank, lora_alpha=cfg.lora_alpha,
        init_lora_weights="gaussian", target_modules=_LORA_TARGETS,
    ))

    text_encoder.to(device, dtype=weight_dtype)
    vae.to(device, dtype=weight_dtype)
    unet.to(device)   # LoRA params fp32 (kararlı optimizasyon)

    lora_params = [p for p in unet.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(lora_params, lr=cfg.learning_rate)
    scaler = torch.cuda.amp.GradScaler(enabled=(device == "cuda"))

    # ---- eğitim döngüsü ----
    unet.train()
    step = 0
    data_iter = _cycle(loader)
    while step < cfg.train_steps:
        optimizer.zero_grad()
        loss_accum = 0.0
        for _ in range(cfg.grad_accum):
            batch = next(data_iter)
            pixel_values = batch["pixel_values"].to(device, dtype=weight_dtype)
            input_ids = batch["input_ids"].to(device)

            with torch.no_grad():
                latents = vae.encode(pixel_values).latent_dist.sample()
                latents = latents * vae.config.scaling_factor
                enc = text_encoder(input_ids)[0]

            noise = torch.randn_like(latents)
            ts = torch.randint(
                0, noise_scheduler.config.num_train_timesteps, (latents.shape[0],),
                device=device,
            ).long()
            noisy = noise_scheduler.add_noise(latents, noise, ts)

            with torch.autocast(device, dtype=weight_dtype, enabled=(device == "cuda")):
                pred = unet(noisy, ts, encoder_hidden_states=enc).sample
                target = noise if noise_scheduler.config.prediction_type == "epsilon" \
                    else noise_scheduler.get_velocity(latents, noise, ts)
                loss = F.mse_loss(pred.float(), target.float()) / cfg.grad_accum

            scaler.scale(loss).backward()
            loss_accum += loss.item()

        scaler.step(optimizer)
        scaler.update()
        step += 1

        if run:
            run.log({"loss": loss_accum, "step": step})
        if step % 50 == 0:
            print(f"step {step}/{cfg.train_steps}  loss={loss_accum:.4f}")

        # ---- periyodik örnek + eval (loop kapanışı) ----
        if step % cfg.sample_every == 0 or step == cfg.train_steps:
            try:
                _sample_and_eval(cfg, unet, vae, text_encoder, tokenizer, device,
                                 weight_dtype, step, run, StableDiffusionPipeline)
            except Exception as e:  # örnekleme eğitimi bozmasın
                print(f"[uyarı] örnekleme/eval atlandı (step {step}): {e}")

    # ---- kaydet + registry ----
    lora_state = get_peft_model_state_dict(unet)
    StableDiffusionPipeline.save_lora_weights(
        save_directory=str(out_dir), unet_lora_layers=lora_state, safe_serialization=True,
    )
    (out_dir / "training_config.json").write_text(cfg.model_dump_json(indent=2))
    print(f"LoRA kaydedildi → {out_dir}")

    if cfg.push_to_hub_repo:
        from huggingface_hub import HfApi

        api = HfApi()
        api.create_repo(cfg.push_to_hub_repo, exist_ok=True)
        api.upload_folder(folder_path=str(out_dir), repo_id=cfg.push_to_hub_repo)
        print(f"Hub'a push → https://huggingface.co/{cfg.push_to_hub_repo}")

    if run:
        run.finish()
    return str(out_dir)


def _cycle(loader):
    while True:
        yield from loader


def _sample_and_eval(cfg, unet, vae, text_encoder, tokenizer, device, dtype, step,
                     run, StableDiffusionPipeline):
    """Mevcut LoRA ile örnek üret → postprocess → eval metrikleri → W&B."""
    import torch

    pipe = StableDiffusionPipeline.from_pretrained(
        cfg.base_model, unet=unet, vae=vae, text_encoder=text_encoder,
        tokenizer=tokenizer, torch_dtype=dtype, safety_checker=None,
    ).to(device)
    pipe.set_progress_bar_config(disable=True)

    logs, images = {}, []
    for prompt in cfg.sample_prompts:
        gen = torch.Generator(device).manual_seed(cfg.seed)
        raw = pipe(prompt, num_inference_steps=25, guidance_scale=7.5, generator=gen).images[0]
        asset, _ = pixelate(raw, target_res=cfg.resolution // 8, num_colors=32)
        m = evaluate_asset(asset, target_colors=32)
        for k, v in m.items():
            logs.setdefault(k, []).append(v)
        images.append((prompt, raw))

    # metrik ortalamaları (ADR-3: tek skora indirgeme, vektör tut)
    avg = {f"eval/{k}": sum(v) / len(v) for k, v in logs.items()}
    print(f"  [eval step {step}] " + "  ".join(f"{k}={v:.3f}" for k, v in avg.items()))
    if run:
        import wandb

        run.log({**avg, "step": step,
                 "samples": [wandb.Image(im, caption=p) for p, im in images]})
    del pipe
    torch.cuda.empty_cache()
