# pixelforge

AI ile **pixel art asset** üretimi — pipeline + otomatik eval + (LoRA) training.
Statik asset'lerle başlar, animasyona doğru genişler. Compute hedefi: Colab.

## Neden bir demo değil?

`notebooks/demo.py` çalışan bir prototipti. Bu repo onu **test edilebilir, ölçülebilir,
reprodüksiyonu mümkün** bir sisteme dönüştürür:

- **postprocess** — ham diffusion çıktısını gerçek pixel art'a çevirir (grid + palet).
- **eval** — "iyi pixel art nedir"i ölçer: palet uyumu, grid-hizası, kenar keskinliği.
  Bu metrikler regresyonları CI'da yakalar ve experiment'leri kıyaslar.
- **pipeline** — SDXL + LoRA üretimini tek kontrata (`GenerationRequest`) bağlar.

## Kurulum

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"      # yerel geliştirme (GPU'suz): postprocess + eval + testler
pytest -q
```

Üretim için (Colab / GPU):

```python
!pip install -q "git+https://github.com/<sen>/pixelforge.git#egg=pixelforge[ml]"

from pixelforge.pipeline import PixelArtPipeline, GenerationRequest
pipe = PixelArtPipeline.from_pretrained_default()          # LCM: hızlı
res  = pipe.generate(GenerationRequest(prompt="a brave knight sprite", seed=42))
res.asset.save("knight.png")                               # gerçek pixel asset
print(res.metrics)                                         # otomatik kalite skorları

# Prompt sadakati önemliyse LCM'i kapat, guidance'ı yükselt:
pipe = PixelArtPipeline.from_pretrained_default(use_lcm=False)
res  = pipe.generate(GenerationRequest(
    prompt="a multi-armed monster", steps=30, guidance_scale=7.5, seed=7))
```

## Yapı

```
src/pixelforge/
├── pipeline/     # inference + kontratlar (config.py)  [ml] ister
├── postprocess/  # pixelate: küçült → palet → büyüt
└── eval/         # metrics: color_count, grid_alignment, edge_sharpness
tests/            # postprocess + eval (golden guardrail'ler)
notebooks/        # ince Colab notebook'ları (demo.py burada)
configs/          # üretim/eğitim ayarları (yaml)
```

Ayrıntılı konvansiyonlar ve yol haritası: [CLAUDE.md](CLAUDE.md).
