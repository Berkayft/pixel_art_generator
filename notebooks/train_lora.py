# =============================================================
#  pixelforge — SD1.5 LoRA eğitimi (Colab)
#  İnce notebook: mantık src/pixelforge/training'de. Burası sadece kurulum + çağrı.
#  Runtime > Change runtime type > GPU (T4 yeter).
# =============================================================


# %% CELL 1 - Kurulum (~2-3 dk)
# -------------------------------------------------------------
# PEP 508 sözdizimi (egg fragment değil):
#
# Repo PUBLIC ise:
# !pip install -q "pixelforge[ml,data] @ git+https://github.com/Berkayft/pixel_art_generator.git"
#
# Repo PRIVATE ise (Colab Secret'ta GH_TOKEN tanımla, sol menü 🔑):
# from google.colab import userdata
# tok = userdata.get("GH_TOKEN")
# !pip install -q "pixelforge[ml,data] @ git+https://{tok}@github.com/Berkayft/pixel_art_generator.git"
#
# Kurulumdan sonra: Runtime > Restart session, sonra Cell 2'den devam.


# %% CELL 2 - (opsiyonel) W&B + HF login
# -------------------------------------------------------------
# import wandb; wandb.login()                 # experiment tracking istiyorsan
# from huggingface_hub import notebook_login
# notebook_login()                            # LoRA'yı Hub'a push edeceksen


# %% CELL 3 - Config + eğit
# -------------------------------------------------------------
from pixelforge.training import TrainingConfig, train_lora

cfg = TrainingConfig(
    dataset="BerkayFT/pixelforge-kenney-tiny-v1",   # HF Hub'daki dataset
    trigger="pxforge",
    rank=16,                 # ADR-6 baseline; öğrenmezse LoKr/DoRA'ya geç
    learning_rate=1e-4,
    train_steps=1000,        # T4'te ilk deneme için makul
    batch_size=1,
    grad_accum=4,
    seed=42,
    sample_every=250,        # her 250 adımda örnek + eval metrikleri
    # wandb_project="pixelforge",             # açarsan loss+örnek+metrik loglanır
    # push_to_hub_repo="BerkayFT/pixelforge-lora-kenney-v1",   # açarsan Hub'a push
)

out = train_lora(cfg)
print("bitti →", out)


# %% CELL 4 - Ürettiğini hızlı dene
# -------------------------------------------------------------
# from pixelforge.pipeline import PixelArtPipeline, GenerationRequest
# import torch
# from diffusers import StableDiffusionPipeline
# pipe = StableDiffusionPipeline.from_pretrained(cfg.base_model, torch_dtype=torch.float16).to("cuda")
# pipe.load_lora_weights(out)
# pipe("pxforge, dungeon, a treasure chest", num_inference_steps=25, guidance_scale=7.5).images[0]
