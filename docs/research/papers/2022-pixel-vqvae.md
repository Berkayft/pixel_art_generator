---
title: "Pixel VQ-VAEs for Improved Pixel Art Representation"
authors: "(doğrula)"
year: 2022
venue: "arXiv 2203.12130"
url: "https://arxiv.org/pdf/2203.12130"
code: "https://github.com/akashsara/fusion-dance"
topic: eval
status: skimmed
rating: ⭐⭐⭐
tags: [representation, vq-vae, embedding, style-conditional-eval]
bibkey: pixelvqvae2022
---

## TL;DR
Pixel art'a **özgü** bir VQ-VAE: pixel art'ın temsilini (embedding) öğrenir, genel
modellerden daha iyi embedding + downstream performans verir.

## Yöntem — anahtar fikir
Pixel art'ın kendine has yapısını (sınırlı palet, keskin grid) hesaba katan bir
vektör-nicemlenmiş autoencoder. Genel ImageNet-tabanlı özelliklerin pixel art'ta zayıf
kaldığı varsayımından yola çıkıyor.

## Bize alaka  ⟵ EN ÖNEMLİ
**RQ-E5 (stil-koşullu eval) için anahtar.** FID, ImageNet Inception özellikleri kullanır →
pixel art'ta anlamsızlaşır (survey de FID sınırını doğruluyor). **Pixel-art'a özgü bir
embedding** ile "stil-referans dağılımına uzaklık" ölçülebilir = *pixel-art FID*'i. H1
hipotezimizin (stil-koşullu eval) somut aracı bu olabilir.

## Sınırlar / şüpheler
Açık repo var (fusion-dance) ama **Pokémon sprite** ile eğitilmiş → bizim stillerimize
(karakter/tileset/ikon) genelleme testi şart. Hazır checkpoint erişimi doğrulanmalı.

## Takip
- Encoder'ı embedding çıkarıcı olarak kullan → CMMD ([[2024-cmmd-rethinking-fid]]) ile
  birleştir = *pixel-art-aware MMD*. H1'in aracı.
- Genelleme yetmezse: kendi küçük dataset'imizle fine-tune (Faz 1 sonrası).
