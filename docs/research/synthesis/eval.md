# Sentez — Evaluation

Makale notlarını (`papers/`, topic: eval) burada birleştir. Karara hazır bilgiye çevir.

## RQ cevapları (tur 1-2 sonrası, kısmi)
- **RQ-E1 (standart metrikler + sınırları):** FID önyargılı + küçük örneklemde güvenilmez
  ([[2024-cmmd-rethinking-fid]]). Küçük/tek-stil dataset'imiz için **CMMD veya KID** doğru.
  CLIPScore = referans-gerektirmeyen prompt-uyumu ama kompozisyon/sayı göremez.
- **RQ-E2 (prompt sadakati / counting):** CLIPScore yetmez; **TIFA/DSG** (VQA ile) counting
  ölçer ([[2023-tifa]]) — ama pixel-art'ta VQA güvenilirliği belirsiz (pilot test gerek).
  "Hiçbir tek metrik tüm kategorilerde korele değil" ([[2025-compositional-eval]]).
- **RQ-E3 (pixel-art'a özgü metrik):** akademik literatür **ince** → boşluk = fırsat.
  Var olan tek benzer kavram grid+palet geçerliliği (Pixel Art Bench, LLM odaklı).
  → bizim `eval/metrics.py` özgün.
- **RQ-E5 (stil-koşullu eval):** **pixel-art-aware CMMD** — CMMD'nin MMD'si + Pixel-VQ-VAE
  embedding'i ([[2022-pixel-vqvae]], repo: fusion-dance). Stil taksonomisi eksenleri
  netleşti (outline/çözünürlük/dithering/projeksiyon/detay → [[ideas]] H1).
- **RQ-E4, E6:** açık (E4 human eval derinleşmedi; E6 kendi korelasyon verimizle ilerler).

## Çelişkiler / tartışmalı noktalar
- Reward modelleri (ImageReward/HPS) genel-estetik için eğitilmiş → pixel-art "iyi"si
  onların dağılımında değil; doğrudan güvenilmez, sadece kaba filtre.

## Boşluklar
- Pixel-art'a özgü, stil-koşullu eval metriği **literatürde yok** → özgün katkı alanı.
- VQA'nın pixel-art'ta counting güvenilirliği ölçülmemiş → bizim pilot testimiz katkı olur.

## Karara aday (→ decisions.md)
1. Dağılım metriği olarak **FID DEĞİL, KID/CMMD** kullan (küçük örneklem).
2. **pixel-art-aware CMMD** prototiple (Pixel-VQ-VAE encoder + MMD) — stil-koşullu eval.
3. Eval'i **tek skora indirgeme**; metrik-vektörü + stil-referans yorumu tut (E-comp'25).
4. Counting/TIFA'yı **zorunlu yapma**; pixel-art VQA pilotundan sonra karar ver.
5. Stil taksonomisini dataset etiketleme şemasına bağla (RQ-L2 caption'ı da etkiler).
