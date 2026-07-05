---
title: "Deep Unsupervised Pixelization"
authors: "Han et al. (doğrula)"
year: 2018
venue: "ACM TOG / SIGGRAPH Asia 2018"
url: "https://dl.acm.org/doi/10.1145/3272127.3275082"
code: "(ara — resmi repo var)"
topic: postprocess
status: skimmed
rating: ⭐⭐⭐
tags: [pixelization, unsupervised, gridnet, division-of-labor]
bibkey: han2018pixelization
---

## TL;DR
Normal görüntüyü pixel art'a çeviren **öğrenilmiş** (unsupervised) yöntem. Eşli veri
gerektirmez; pixelization ↔ depixelization ikiliğini tek ağda çift yönlü kurar.

## Yöntem — anahtar fikir
Üç aşamalı kaskad: **GridNet** (çok-ölçekli grid yapısı) → **PixelNet** (keskin kenarlı,
lokal-optimal pixel art) → **DepixelNet** (geri kurtarma, öz-denetim sinyali). Eşli
veri yokluğunu bu döngüsel kurulum çözüyor.

## Bize alaka  ⟵ EN ÖNEMLİ
**RQ-P1 + RQ-X1'in kalbi.** Bizim `pixelate` deterministik (küçült+quantize). Bu makale
gösteriyor ki pixelization **öğrenilebilir** de. Yani "sorumluluk dağılımı"nda bir üçüncü
seçenek: post-process *öğrenilmiş bir model* olabilir. Ama: bizim hedefimiz üretim→asset,
onların ki foto→pixel. Bizde model zaten pixel-benzeri üretiyor; deterministik post-process
muhtemelen yeterli. **Karar adayı:** baseline deterministik kalsın; öğrenilmiş pixelization'ı
ancak deterministik yetmezse dene (aşırı mühendislik riski).

## Sınırlar / şüpheler
Eğitim + veri yükü getirir; bizim Colab-only kısıtına ağır. Foto→pixel senaryosuna göre
optimize, bizim generation→pixel akışımıza birebir oturmayabilir.

## Takip
Resmi repo + DepixelNet fikri (depixelization bizim eval'de "gerçek pixel mi" testine ilham).
