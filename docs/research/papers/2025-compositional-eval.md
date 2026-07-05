---
title: "Evaluating the Evaluators: Metrics for Compositional Text-to-Image Generation"
authors: "(doğrula)"
year: 2025
venue: "arXiv 2509.21227"
url: "https://arxiv.org/html/2509.21227v1"
code: ""
topic: eval
status: skimmed
rating: ⭐⭐⭐
tags: [meta-evaluation, compositionality, multi-metric, orthogonality]
bibkey: compeval2025
---

## TL;DR
Metrikleri değerlendiren meta-çalışma: **hiçbir tek metrik** tüm kompozisyon
kategorilerinde insan yargısıyla tutarlı korele değil.

## Yöntem — anahtar fikir
Farklı kompozisyon kategorilerinde (sayı, renk, ilişki, konum) çeşitli metrikleri insan
yargısına karşı kıyaslar. Bulgu: her metrik farklı kategoride güçlü/zayıf.

## Bize alaka  ⟵ EN ÖNEMLİ
**RQ-E6'yı ve bizim çoklu-metrik yaklaşımımızı doğrudan doğruluyor.** "Tek sinyale güvenme"
= bizim color/grid/edge/palette metriklerini *birlikte* kullanma sezgimizin literatür
dayanağı. Ayrıca H3'ü (metrik ortogonalliği) besliyor: metrikler tamamlayıcı olmalı,
gereksiz değil. **Karar adayı:** eval'i tek skora indirgeme; metrik-vektörü + stil-koşullu
yorum tut.

## Sınırlar / şüpheler
Genel T2I odaklı, pixel-art'a özgü değil. Kategoriler bize kısmen uyar.

## Takip
Metrik-agregasyon stratejileri (ağırlıklı mı, Pareto mu?) → eval harness tasarımına gir.
