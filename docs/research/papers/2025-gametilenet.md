---
title: "GameTileNet: A Semantic Dataset for Low-Resolution Game Art in Procedural Content Generation"
authors: "(doğrula)"
year: 2025
venue: "arXiv 2507.02941"
url: "https://arxiv.org/html/2507.02941v1"
code: "(ara)"
topic: data
status: skimmed
rating: ⭐⭐
tags: [dataset, game-art, low-resolution, semantic-labels]
bibkey: gametilenet2025
---

## TL;DR
Düşük çözünürlüklü oyun sanatı (tile/sprite) için **semantik etiketli** bir dataset;
procedural content generation odaklı.

## Yöntem — anahtar fikir
Pixel-art'ın CV modelleri için zor olduğunu (düşük çöz., ince varyasyon) vurgular;
etiketli veri boşluğunu bir dataset ile doldurur.

## Bize alaka  ⟵ EN ÖNEMLİ
**Faz 1 dataset adayı.** Kenney/CC0 dışında ikinci bir kaynak olabilir. Lisansını +
stil tutarlılığını (ADR-8: "tutarlı stil") doğrula. Semantik etiketleri, ADR-5
taksonomi etiketlemesi için başlangıç olabilir.

## Sınırlar / şüpheler
Lisans? Stil karışıksa (çok kaynaklı) tek-LoRA için uygun olmayabilir → alt-küme seç.

## Takip
Lisans + örnekleri incele; Kenney ile kıyasla (hangisi daha tutarlı stil).
