# Literatür Taraması

Sistematik, hafif tarama. Yöntem: `scope → query → triage → extract → synthesize → decide`.
Kapsam: **topic başına 5-8 derin okuma** + birkaç künye. Referans: markdown + [refs.bib](refs.bib).

## Nasıl çalışır

```
questions.md   → ne öğrenmek istiyoruz (RQ'lar) — arama bunları hedefler
sources.log.md → taranan her kaynak: alındı/elendi + neden (iz bırak)
papers/*.md    → dahil edilen makale başına 1 not (_TEMPLATE.md'den kopyala)
synthesis/*.md → temaya göre sentez: ne öğrendik, çelişki, boşluk
decisions.md   → bulgu → PROJE kararı (ADR)
refs.bib       → BibTeX künyeler
```

**Akış:** kaynak bul → `sources.log`'a yaz → triage (özet) → değerse `papers/`'a tam not →
topic bitince `synthesis/`'te topla → karara değeni `decisions.md`'ye geçir.

## Durum tablosu (canlı)

| Topic | RQ | Hedef | Okundu | Sentez | Karar |
|-------|----|-------|--------|--------|-------|
| LoRA / fine-tune | RQ-L1..L4 | 5-8 | 1 (skim)+guide'lar | 🟢 | 🟢 (ADR-6..8) |
| Evaluation | RQ-E1..E6 | 5-8 | 6 (skim) | 🟢 | 🟢 (ADR-1..5) |
| Post-process | RQ-P1..P3, X1 | 5-8 | 1 (skim) | ⬜ | ⬜ |

## Tarama günlüğü

Her oturum sonunda 2 satır: ne bakıldı, ne çıktı.

- **Tur 1 (eval + postprocess):** 3 sorgu → 10 kaynak triage (5 INCLUDE, 3 SKIM, 2 EXCLUDE).
  Bulgular: (1) pixel-art'a *özgü* akademik eval ince → `eval/metrics.py` özgün katkı;
  (2) "tek metrik yetmez" (comp-eval'25) çoklu-metrik + RQ-E6'yı doğruluyor;
  (3) Pixel VQ-VAE → stil-koşullu eval (RQ-E5) için somut araç; (4) TIFA → counting
  ölçümü ama pixel-art'ta VQA riski; (5) Deep Unsup. Pixelization → öğrenilmiş post-process
  seçeneği (X1). Kalan: RQ-E5/E6 derin okuma, sonra RQ-L1.
- **Tur 2 (eval derinleştirme):** 3 sorgu → CMMD (FID önyargılı, küçük-örneklem-dostu),
  Pixel-VQ-VAE açık repo (fusion-dance), stil taksonomisi eksenleri. **Ana çıktı:**
  *pixel-art-aware CMMD* fikri (Pixel-VQ-VAE embedding + MMD) = stil-koşullu eval aracı.
  Eval sentezi 5 karar adayıyla dolduruldu. Eval tarafı karara hazır → sıradaki: RQ-L1.
- **Tur 3 (RQ-L1 / LoRA):** 3 sorgu → LoRA vs DreamBooth vs TI, LyCORIS ailesi, dataset+caption.
  Bulgular: (1) stil+Colab için **LoRA net kazanan** (DreamBooth 2-7GB ağır); (2) adapter tipi
  **ikinci derece** ("optimal ayarla fark küçük") → baseline düz LoRA, fallback LoKr/DoRA;
  (3) **caption altın kuralı**: stili yazma, gerisini tag'le → ADR-5 taksonomisiyle birleşti.
  ADR-6..8 yazıldı. LoRA tarafı karara hazır.

## Guardrail
- Topic başına hedefi aşma; "ilginç ama alakasız" → `decisions.md` "Kapsam dışı".
- Her makale notunun **"Bize alaka"** alanı dolu olmalı — yoksa not ölü arşiv.
