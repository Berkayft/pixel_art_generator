# Araştırma Soruları (RQ)

Arama bunları hedefler. Her makale notu en az bir RQ'ya cevap vermeli.
Taslak — birlikte kesinleştirilecek.

## LoRA / fine-tune

- **RQ-L1** — Stil (pixel art) öğretmek için LoRA mı, DreamBooth mı, textual inversion mı?
  Hangi durumda hangisi, trade-off nedir?
- **RQ-L2** — Minimum/ideal dataset boyutu ve **caption stratejisi** ne?
  (trigger word kullan/kullanma, otomatik caption, caption granülerliği)
- **RQ-L3** — SD1.5 vs SDXL LoRA: Colab/T4 kısıtında hangisi?
  Tipik hiperparametreler (rank, lr, steps, batch, resolution)?
- **RQ-L4** — Stil tutarlılığı ↔ overfitting dengesi nasıl kurulur?
  (regularization images, early stopping, LoRA ağırlığı)

## Evaluation

- **RQ-E1** — Standart generative metrikler (FID, CLIP score, IS) bize uyar mı, sınırları ne?
  Küçük/tek-stil dataset'te FID anlamlı mı?
- **RQ-E2** — **Prompt sadakati / compositionality / counting** ("8 kol") nasıl ölçülüyor?
  (CLIPScore, VQA-tabanlı, TIFA, ImageReward vb.)
- **RQ-E3** — Pixel-art'a **özgü** kalite (grid hizası, palet, dithering) için metrik var mı?
  Yoksa bizim `eval/metrics.py` özgün katkı mı?
- **RQ-E4** — Küçük ölçekte güvenilir **human eval** protokolü nasıl kurulur?
  (pairwise karşılaştırma, rubrik, kaç değerlendirici)
- **RQ-E5** — **Stil-koşullu eval:** "iyi" tüm stillerde aynı değil (outline var/yok,
  palet katmanı, dithering). Metrikler evrensel eşik yerine **stil-referans dağılımına**
  göre nasıl kalibre edilir? (bkz. FID-per-style mantığı) → [[ideas]]
- **RQ-E6** — **Metrik ortogonalliği:** hangi metrikler gereksiz (yüksek |korelasyon|),
  hangileri bağımsız? Redundant olanları ele. (kendi korelasyon matrisimiz başlangıç) → [[ideas]]

## Cross-cutting (model ↔ pipeline)

- **RQ-X1** — **Sorumluluk dağılımı:** hangi stil nitelikleri deterministik pre/post-process
  ile, hangileri model (LoRA) ile sağlanmalı? (palet/grid/outline → pipeline aday;
  şekil/içerik → model). Bu, LoRA'da *neyi öğretmeye çalışacağımızı* belirler → RQ-L1'i etkiler. → [[ideas]]

## Post-process

- **RQ-P1** — Görüntü → pixel art dönüşümü (pixelization) SOTA ne?
  Öğrenilmiş (GAN/diffusion) vs klasik yaklaşımlar.
- **RQ-P2** — Palet çıkarımı/quantization (median-cut vs k-means vs öğrenilmiş) +
  **dithering** teknikleri? Bizim `pixelate` neyi kaçırıyor?
- **RQ-P3** — Pixel-art-aware downscaling (nearest/lanczos ötesi) yaklaşımları?

## Kesinleştirme notları
- _(RQ eklendi/çıkarıldı ise buraya tarih + neden)_
