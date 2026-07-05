# Sentez — Pre/Post-process

Tur 1 (öğrenilmiş pixelization) + Tur 4 (dithering, downscaling, dataset prep) sonrası.
Kaynaklar: [[2018-deep-unsupervised-pixelization]], dithering rehberleri, adaptive
downscaling, sprite/dataset çalışmaları (sources.log #4, #21-27).

## RQ cevapları

- **RQ-P1 (pixelization SOTA):** Öğrenilmiş yöntem var (GridNet+PixelNet,
  [[2018-deep-unsupervised-pixelization]]) ama bizim akışımız *generation→pixel* (foto→pixel
  değil); model zaten pixel-benzeri üretiyor → **deterministik post-process yeterli**.
  Öğrenilmiş pixelization = yedek, aşırı-mühendislik riski.

- **RQ-P2 (quantization + dithering) — en aksiyon-alınabilir:** `pixelate` quantize ediyor
  (MEDIANCUT) ama **dithering yok**. İki aile:
  - **Error diffusion** (Floyd-Steinberg, Atkinson): organik, sadık tonlama → **statik** için en iyi.
  - **Ordered / Bayer** (2×2..8×8 eşik matrisi): düzenli, tekrarlı desen → **temiz tile'lanır ve
    animasyonda kararlı** (error-diffusion kare-kare titrer/flicker).
  - **⟹ Statik→animasyon köprüsü:** Faz 1 statik'te FS/Atkinson, Faz 4 animasyonda ordered/Bayer.
  - Best practice: önce quantize (median-cut/k-means) sonra dither.

- **RQ-P3 (downscaling):** `pixelate` LANCZOS kullanıyor (makul baseline). Ama **içerik-duyarlı
  downscaling** (naive resample + blok renk örnekleme + kenar tespiti + koşullu değişim,
  [[sources.log]] #23) 2-4×'te kenar/şekil/transparency'yi daha iyi koruyor. Aday iyileştirme.
  (Not: hqx/xBR *upscale* algoritmaları → preview'a değil, asset'e uygun değil.)

- **RQ-P4 (dataset hazırlığı + augmentation):** **Kritik kural — rotation/keyfi scale pixel-art
  grid'ini bozar**, zararlı ([[sources.log]] #26). Güvenli augmentation: yatay flip, palet
  kaydırma, tam-sayı-kat scale. Arka plana kompozisyon (solid/gradient/noise) fg/bg ayrımını
  öğretir → Faz 2 transparency için değerli. → ADR-8'i sıkılaştırır.

- **RQ-P5 (girdi/conditioning ön-işleme):** Taksonomi tag'lerini prompt'a enjeksiyon (ADR-7);
  img2img/ControlNet için siluet/poz hazırlığı (Faz 2). _(derinleşmedi — Faz 2 konusu.)_

## Çelişkiler / tartışmalı noktalar
- Sprite GAN çalışması rotation'ın "daha çok veri" için faydalı olabileceğini de söylüyor
  → bizim stil-saflığı önceliğimizle çelişir; biz rotation'dan kaçınırız (grid > veri hacmi).

## Boşluklar
- Bizim generation→pixel akışına özgü downscale+dither reçetesi yok → deneyle bulunacak.

## Karara aday (→ decisions.md)
9.  `pixelate`'e **opsiyonel dithering** ekle: statik=FS/Atkinson, animasyon=ordered/Bayer.
10. Downscale'i **içerik-duyarlı** varyantla dene (baseline LANCZOS kalsın, A/B eval ile kıyasla).
11. **Augmentation politikası:** rotation/keyfi-scale YASAK (grid bozar); flip + palet + int-scale serbest.
