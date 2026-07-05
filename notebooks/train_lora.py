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
# !pip uninstall -y torchao    # ÖNEMLİ: düz LoRA torchao istemez; kurulu kalırsa peft
#                              # onu import edip 'torch.int1' hatası verir (torch 2.4 uyumsuz)
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

# --- LoRA #2: LPC 4-view (captioned sprite sheet) — ÖNERİLEN ---
# Zengin caption + tutarlı stil + 'sheet'i tekte üret' + Faz 4 yönü.
cfg = TrainingConfig(
    dataset="carlosuperb/lpc-4view-pixel-art-diffusion",
    caption_csv="captions/captions_optimized.csv",   # set → csv+zip yolu (manifest değil)
    images_zip="images/train.zip",
    subsample=800,           # 50k'dan 800 örnek (T4'te makul; seed ile reproducible)
    rank=16,
    learning_rate=1e-4,
    train_steps=1500,        # daha çeşitli veri → biraz daha uzun
    batch_size=1,
    grad_accum=4,
    seed=42,
    sample_every=300,
    sample_prompts=[
        "lpc-style pixel art character, female body, green skin, leather armor, "
        "4-view sprite sheet (front/back/left/right), hard edges, no anti-aliasing",
        "lpc-style pixel art character, male body, blue wizard robe, staff, "
        "4-view sprite sheet (front/back/left/right), hard edges, no anti-aliasing",
    ],
    # wandb_project="pixelforge",
    # push_to_hub_repo="BerkayFT/pixelforge-lora-lpc-v1",   # WRITE token ile
)

# --- LoRA #1: Kenney tiny (manifest yolu) — referans ---
# cfg = TrainingConfig(dataset="BerkayFT/pixelforge-kenney-tiny-v1", trigger="pxforge",
#                      train_steps=1000)

out = train_lora(cfg)
print("bitti →", out)


# %% CELL 4 - Ürettiğini hızlı dene (LPC 4-view)
# -------------------------------------------------------------
# import torch
# from diffusers import StableDiffusionPipeline
# pipe = StableDiffusionPipeline.from_pretrained(
#     cfg.base_model, torch_dtype=torch.float16, safety_checker=None).to("cuda")
# pipe.load_lora_weights(out)
# # prompt'u caption stiline uydur:
# img = pipe(
#     "lpc-style pixel art character, female body, green skin, leather armor, "
#     "4-view sprite sheet (front/back/left/right), hard edges, no anti-aliasing",
#     num_inference_steps=25, guidance_scale=7.5).images[0]
# # gerçek asset için pixelate'ten geçir:
# from pixelforge.postprocess import pixelate
# _, preview = pixelate(img, target_res=128, num_colors=32)
# preview
