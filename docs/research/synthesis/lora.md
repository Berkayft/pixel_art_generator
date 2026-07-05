# Sentez — LoRA / fine-tune

Tur 3 (3 sorgu) sonrası. Kaynaklar: [[2023-lycoris-eval]], LyCORIS repo, SDXL LoRA
guide'ları, personalization karşılaştırmaları (bkz. sources.log #16-20).

## RQ cevapları

- **RQ-L1 (LoRA vs DreamBooth vs TI):** Stil + Colab kısıtı için **LoRA net kazanan**.
  - DreamBooth: güçlü ama **2-7 GB**, yavaş → HF Hub/Colab akışına ağır. Ele.
  - Textual Inversion: ~100 KB ama **kapasite düşük** → tek konsept, stil için zayıf.
  - LoRA: küçük, hızlı, düşük VRAM, stil için ideal (pixel-art-xl zaten kanıt).

- **RQ-L2 (dataset + caption) — en aksiyon-alınabilir:**
  - **Boyut:** azıyla olur; "25 iyi > 75 tutarsız". Kalite > nicelik. Stil için **tutarlılık**
    kritik. Başlangıç: ~30-100 tutarlı görsel.
  - **Caption altın kuralı:** *öğretmek istediğini caption'lama, geri kalanı caption'la.*
    Stil LoRA'sı için stili yazma → trigger word absorbe etsin; içerik/varyasyonu (portrait,
    full-body, top-down...) yaz.
  - **Format:** SDXL'de **virgülle ayrılmış tag** > doğal dil. `<trigger>, tag1, tag2, ...`.
    Oto-annotate + elle düzelt.
  - **Trigger:** benzersiz token (ör. `pxforge-style`). Yapılandırılmış format reprodüksiyon sağlar.

- **RQ-L3 (SD1.5 vs SDXL + hiperparametre):** Adapter *tipi ikinci derece* — "optimal
  ayarla kalite farkı küçük" ([[2023-lycoris-eval]]). Colab/T4 iterasyonu için **önce SD1.5**
  (hızlı), sağlamlaşınca SDXL. LyCORIS repo LoCon/LoHa/LoKr/DoRA'yı tek arayüzde verir.

- **RQ-L4 (tutarlılık ↔ overfit):** Blok-bazlı LoRA ([[sources.log]] #18) *nerede* öğrenildiğini
  kontrol ediyor; stil için bazı bloklar yeterli. Genel araçlar: LoRA ağırlığı ayarı,
  düşük rank, çeşitli caption. _(derinleşmedi — Faz 1 deneyiyle netleşecek)_

## Çelişkiler / tartışmalı noktalar
- "En iyi yöntem" kaynaklara göre değişiyor (kimi DreamBooth der) ama hepsi *bizim kısıtımızda*
  (küçük dosya, Colab, stil) LoRA'ya işaret ediyor. Çelişki bağlam farkından.

## Boşluklar
- Pixel-art'a **özgü** LoRA hiperparametre reçetesi yok → kendi deneyimiz katkı.
- Caption'da **stil taksonomisi eksenlerini** (outline/dithering...) tag olarak kullanma
  fikri literatürde yok → ADR-5 ile özgün bağ.

## Karara aday (→ decisions.md)
6. Baseline: **düz LoRA**, önce **SD1.5**. Fallback: LoKr (öğrenmezse), DoRA (kalite platoda).
7. **Caption şeması:** trigger + tag; stili yazma; içerik + taksonomi eksenlerini tag'le.
8. Dataset: ~30-100 tutarlı görsel, kalite>nicelik; oto-annotate + elle düzelt.
