# =============================================================
#  PIXEL ART GENERATOR - Colab Prototip
#  SDXL + pixel-art-xl LoRA + LCM (hız) + post-processing
# =============================================================
#  Kullanim: Her "# %% CELL" blogunu Colab'da ayri bir hucreye
#  yapistir. Runtime > Change runtime type > GPU (T4 yeter, L4/A100 daha iyi).
# =============================================================


# %% CELL 1 - Kurulum
# -------------------------------------------------------------
# !pip install -q diffusers transformers accelerate safetensors
# !pip install -q -U "peft>=0.17.0" "torchao>=0.16.0"   # diffusers peft>=0.17, o da torchao>=0.16 ister
# Kurulumdan sonra: Runtime > Restart session (bir kez) sonra Cell 2'den devam et.


# %% CELL 2 - Modeli ve LoRA'lari yukle (bir kez calisir, ~1-2 dk)
# -------------------------------------------------------------
import torch
from diffusers import DiffusionPipeline, LCMScheduler

BASE_MODEL   = "stabilityai/stable-diffusion-xl-base-1.0"
LCM_LORA     = "latent-consistency/lcm-lora-sdxl"      # 8 adimda uretim icin
PIXEL_LORA   = "nerijs/pixel-art-xl"                   # pixel art stili

pipe = DiffusionPipeline.from_pretrained(
    BASE_MODEL,
    variant="fp16",
    torch_dtype=torch.float16,
)
# LCM scheduler = az adim, hizli uretim
pipe.scheduler = LCMScheduler.from_config(pipe.scheduler.config)

# Onemli: LoRA'lari GPU'ya tasimadan ONCE yukle
pipe.load_lora_weights(LCM_LORA, adapter_name="lcm")
pipe.load_lora_weights(
    PIXEL_LORA,
    weight_name="pixel-art-xl.safetensors",
    adapter_name="pixel",
)
# Iki LoRA'yi birlikte aktif et. pixel agirligini 1.2-1.4 arasi dene.
pipe.set_adapters(["lcm", "pixel"], adapter_weights=[1.0, 1.2])

pipe.to("cuda")
print("Hazir.")


# %% CELL 3 - Post-processing: gercek pixel art'in olustugu yer
# -------------------------------------------------------------
# LoRA tek basina "pixel gibi" gorunen ama teknik olarak pixel OLMAYAN
# (bulanik kenarli, yuzlerce renkli) bir goruntu uretir.
# Asagidaki adim onu gercek pixel art'a cevirir:
#   1) hedef native cozunurluge kucult (blok boyutu = pixel_size)
#   2) paleti sinirla (renk sayisini kis)
#   3) goruntuleme icin nearest-neighbor ile buyut
from PIL import Image

def pixelate(img: Image.Image, target_res: int = 128, num_colors: int = 32):
    """
    target_res : cikti pixel art'in gercek genisligi/yuksekligi ( or. 64, 128)
                 kucuk = daha 'chunky' retro gorunum
    num_colors : palet buyuklugu (16-64 arasi pixel art icin tipik)
    """
    w, h = img.size
    # 1) kucultme: LANCZOS ile alt-piksel gurultusunu ortala
    small = img.resize((target_res, target_res), Image.LANCZOS)
    # 2) palet quantization (sinirli renk = pixel art hissi)
    small = small.quantize(colors=num_colors, method=Image.MEDIANCUT).convert("RGB")
    # 3) net kenarli buyutme (ekranda gormek icin)
    display = small.resize((w, h), Image.NEAREST)
    return small, display   # small = kaydedilecek gercek asset, display = onizleme


# %% CELL 4 - Uretim fonksiyonu
# -------------------------------------------------------------
# Genel amacli: karakter, tileset, ikon, sahne icin ipuclari
# Anahtar: "pixel" kelimesi stili tetikler. Negatif prompt cok onemli.
NEGATIVE = "3d render, realistic, photo, blurry, anti-aliased, smooth gradient, soft shading"

def generate(prompt, target_res=128, num_colors=32, steps=8, seed=None):
    full_prompt = f"pixel, {prompt}"
    gen = torch.Generator("cuda").manual_seed(seed) if seed is not None else None
    raw = pipe(
        prompt=full_prompt,
        negative_prompt=NEGATIVE,
        num_inference_steps=steps,   # LCM ile 8 yeterli
        guidance_scale=1.5,          # LCM icin dusuk tutulur
        generator=gen,
    ).images[0]
    small, display = pixelate(raw, target_res, num_colors)
    return raw, small, display


# %% CELL 5 - Dene: farkli asset tipleri (genel amacli test)
# -------------------------------------------------------------
import matplotlib.pyplot as plt

TESTS = {
    "karakter":  ("a brave knight character sprite, side view", 96, 24),
    "tileset":   ("grass and stone dungeon floor tileset, top down", 128, 16),
    "ikon":      ("a red health potion item icon", 48, 16),
    "sahne":     ("a cozy pixel town at sunset, landscape", 160, 48),
}

fig, axes = plt.subplots(1, len(TESTS), figsize=(4 * len(TESTS), 4))
for ax, (name, (p, res, cols)) in zip(axes, TESTS.items()):
    _, small, display = generate(p, target_res=res, num_colors=cols, seed=42)
    small.save(f"/content/{name}.png")   # gercek asset (kucuk, temiz pixel)
    ax.imshow(display)
    ax.set_title(f"{name}\n{res}px / {cols} renk")
    ax.axis("off")
plt.tight_layout()
plt.show()
print("Asset'ler /content/ altina kaydedildi.")


# %% CELL 6 - Tek uretim (kendi promptunla oyna)
# -------------------------------------------------------------
# raw, small, display = generate(
#     "a wizard casting a spell, character sprite",
#     target_res=96, num_colors=24, seed=7,
# )
# display  # Colab'da son satir olarak yazarsan onizleme cikar