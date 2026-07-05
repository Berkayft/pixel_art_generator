# Dataset Adayları (LoRA #2)

LoRA #1 (Kenney Tiny) bulgusu: 16px çevre-tile + tek-tip caption → stil aktı ama
içerik/kompozisyon yok. İhtiyaç: **caption'lı**, tutarlı stil, tercihen **obje/karakter
sprite** (çevre-tile değil), makul çözünürlük (32-64px, aşırı upscale yok).

## Adaylar

| Dataset | Ne | Caption | Lisans | Çöz. | Uygunluk |
|---------|-----|---------|--------|------|----------|
| **carlosuperb/lpc-4view-pixel-art-diffusion** | LPC 4-yön karakter sprite + metin | ✅ (kıyafet/ekipman/renk) | CC-BY-SA 3.0 | ~64px | ⭐⭐⭐ karakter + 4-view (sheet fikri + Faz 4) |
| **Limbicnation/pixel-art-character** | 500 karakter sprite | ✅ ("...game sprite, transparent bg") | doğrula | — | ⭐⭐ ama **sentetik** (FLUX üretimi) → model-distilasyonu |
| **sWizad/pokemon-trainer-sprite-pixelart** | Pokémon trainer 96×96 | ✅ BLIP | doğrula | 96px | ⭐⭐ tutarlı ama Pokémon-spesifik |
| **jainr3/diffusiondb-pixelart** | DiffusionDB → pixelator | zayıf | — | değişken | ⭐ sahte-pixel (app ile pikselleştirilmiş) |
| **LPC base (OpenGameArt/GitHub)** | karakter + tile, tutarlı | üretilebilir (generator CSV) | CC-BY-SA/GPL3 | 64px | ⭐⭐⭐ ham kaynak, en çok kontrol |

## LPC (Liberated Pixel Cup) — öne çıkan
2012 CC-yarışması; **kasıtlı olarak stilistik tutarlı** free art (ADR-8'e birebir).
Karakter + harita tile. Universal LPC generator yüzlerce karakter + lisans CSV üretir.
carlosuperb bunu 4-view + caption olarak HF'de paketlemiş.
- **Lisans dikkat:** CC-BY-SA 3.0 + GPL3 (attribution + **share-alike** → türev de aynı
  lisans). Portfolyo için OK ama Kenney'in CC0'ı kadar serbest değil — türevleri paylaşırken
  atıf + aynı lisans şart.

## Kullanıcının "sheet'i tekte üret" fikriyle bağ
Kenney tileset'i tek sheet olarak üretmek → elimizde sadece 3 sheet var, LoRA için çok az.
AMA **LPC 4-view** zaten "tek görselde çok görünüm" formatı ve **yüzlerce örnek + caption**
var → "sheet'i bir arada üret" fikri KARAKTER sprite-sheet'inde gerçekleşebilir (tileset'te
değil). Faz 4 (animasyon/yön) için de temel.

## Öneri
**carlosuperb/lpc-4view** ile LoRA #2 → caption problemi + sheet fikri + tutarlı stil +
Faz 4 yönü tek hamlede. Tek uyarı: CC-BY-SA lisansı (Kenney CC0 değil).
Alternatif: sentetik istemiyorsan Limbicnation'ı ele; kontrol istiyorsan LPC generator'dan
kendi setini üret.
