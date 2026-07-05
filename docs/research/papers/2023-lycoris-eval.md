---
title: "Navigating Text-To-Image Customization: From LyCORIS Fine-Tuning to Model Evaluation"
authors: "Yeh et al. / KohakuBlueleaf ekibi (doğrula)"
year: 2023
venue: "arXiv 2309.14859 (ICLR'24 doğrula)"
url: "https://arxiv.org/html/2309.14859v2"
code: "https://github.com/KohakuBlueleaf/LyCORIS"
topic: lora
status: skimmed
rating: ⭐⭐⭐
tags: [lycoris, lora, lokr, loha, dora, evaluation, method-comparison]
bibkey: yeh2023lycoris
---

## TL;DR
LyCORIS ailesini (LoCon/LoHa/LoKr/DyLoRA + native FT) sistematik tanıtır ve **fine-tune
yöntemlerini değerlendirme çerçevesiyle** kıyaslar. Yöntem seçimini veriye bağlar.

## Yöntem — anahtar fikir
Farklı düşük-rank ayrıştırmaları (LoRA=toplama, LoHa=Hadamard, LoKr=Kronecker) aynı
çatı altında; kapasite/parametre/kalite dengesi. Ayrıca eval eksenleri (sadakat,
çeşitlilik, kontrol) öneriyor → bizim eval işimizle örtüşür.

## Bize alaka  ⟵ EN ÖNEMLİ
**RQ-L1/L3'ün otoritesi.** Doğruluyor: (1) yöntemler arası kalite farkı optimal ayarla
küçük → adapter tipi ikinci derece; (2) LoKr ince-detay yakalamada güçlü. **Karar:**
baseline **düz LoRA (LoCon)**; "yeterince öğrenmiyor" sinyalinde **LoKr (düşük factor,
full dim)**; DoRA'yı sadece kalite platoda dene (daha pahalı). Repo (LyCORIS) hepsini
tek arayüzde veriyor → deney maliyeti düşük.

## Sınırlar / şüpheler
Pixel-art'a özgü değil; genel stil/karakter senaryoları. LyCORIS ekstra kütüphane
(diffusers-native değil) → kurulum yükü, [ml] extra'ya pinlenmeli.

## Takip
- LyCORIS'i Colab'da diffusers ile entegrasyon pürüzü var mı?
- Önerdikleri eval eksenlerini bizim `eval/` ile eşle.
