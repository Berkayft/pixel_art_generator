---
title: "Rethinking FID: Towards a Better Evaluation Metric for Image Generation"
authors: "Jayasumana et al. (doğrula)"
year: 2024
venue: "CVPR 2024 / arXiv 2401.09603"
url: "https://arxiv.org/abs/2401.09603"
code: "(Google Research — ara)"
topic: eval
status: skimmed
rating: ⭐⭐⭐
tags: [cmmd, fid, mmd, small-sample, style-conditional]
bibkey: jayasumana2024cmmd
---

## TL;DR
FID kusurlu: **önyargılı tahminci**, örneklem boyutuna duyarlı, kovaryans için büyük
örneklem ister. Alternatif **CMMD** = CLIP embedding + Maximum Mean Discrepancy (MMD):
önyargısız, dağılım varsayımı yok, **küçük örneklemde güvenilir**.

## Yöntem — anahtar fikir
Fréchet mesafesi yerine MMD (çekirdek-tabanlı, dağılımsız). Inception yerine CLIP
embedding. KID'e benzer ama CLIP özellikleriyle. İnsan algısıyla tutarlı, kademeli
kalite iyileşmesini yakalıyor.

## Bize alaka  ⟵ EN ÖNEMLİ
İki yönden kritik:
1. **RQ-E1:** Bizim dataset küçük + tek-stil → FID zaten güvenilmez. CMMD/KID doğru seçim.
2. **RQ-E5 (stil-koşullu eval) — asıl fikir:** CMMD'nin embedding'ini CLIP yerine
   **Pixel-VQ-VAE** ([[2022-pixel-vqvae]]) ile değiştir → *pixel-art-aware MMD*. "Bu asset,
   hedef stilin referans dağılımına ne kadar yakın?" sorusunu pixel-art'a özgü ölçer.
   = H1'in ([[ideas]]) somut aracı + özgün katkı.

## Sınırlar / şüpheler
MMD çekirdek seçimi + embedding kalitesine duyarlı. Pixel-VQ-VAE embedding'i Pokémon
sprite'a fit → bizim stillerimize genellenir mi, test gerek.

## Takip
- KID ile kıyas (Inception-tabanlı, hazır implementasyon bol).
- Pixel-VQ-VAE encoder'ını embedding çıkarıcı olarak sarmalayıp mini-CMMD prototiple.
