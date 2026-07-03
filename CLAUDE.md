# pixelforge — agent konvansiyonları

AI ile pixel art asset üretimi. Amaç: önce **statik** asset üretimi, sonra **animasyon**.
Strateji: kendi **LoRA fine-tune**'u; hedef **kişisel/portfolyo**; compute **sadece Colab**.

## Mimarî (katmanlar tek yönlü bağımlı)

```
pipeline/    → model yükleme + inference (AĞIR: torch/diffusers, [ml] extra)
postprocess/ → ham görsel → gerçek pixel art (HAFİF: PIL)
eval/        → otomatik kalite metrikleri (HAFİF: numpy/PIL)
```

`pipeline` → `postprocess` + `eval` çağırır. Tersi OLMAZ.
`postprocess` ve `eval` **asla torch import etmez** (GPU'suz/yerelde test edilebilir kalmalı).

## Değişmez kurallar (agent'lar bunları bozmasın)

1. **Kontratlar** `pipeline/config.py`'de: `GenerationRequest` / `GenerationResult`.
   Modüller arası veri bu tiplerle akar. Şemayı değiştirince tüm çağıranları güncelle.
2. **Ağırlık / dataset / çıktı (.png dahil) git'e girmez** — `.gitignore`'a bak. Kayıt: HF Hub.
3. **Ağır ML deps sert pinli** (`[ml]`), hafif çekirdek floor (`>=`). Yeni ML deps eklerken pinle.
   (Neden: torchao/peft sürüm cehennemi — bkz. `notebooks/demo.py` geçmişi.)
4. **Her yeni davranış = test.** `eval`/`postprocess` saf & deterministik → kolay test edilir.
5. **Notebook'lar ince**: mantık `src/`'de, notebook sadece `pip install git+...` + çağrı.

## Geliştirme

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"     # yerel: hafif çekirdek + pytest/ruff (torch YOK)
pip install -e ".[ml]"      # Colab/GPU: üretim yapmak için ağır stack
pytest -q                   # testler
ruff check src tests        # lint
```

## Yol haritası
- **Faz 1 (şimdi):** dataset curation (Kenney/CC0) + ilk SD1.5 LoRA + CLIP prompt-sadakati metriği.
- **Faz 2:** transparency/bg-removal, sprite set tutarlılığı, SDXL'e yükseltme.
- **Faz 4:** animasyon (keyframe + interpolasyon, sprite sheet).
