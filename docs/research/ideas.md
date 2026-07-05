# Hipotezler — kendi verimizden

Literatürden değil, *bizim deneylerimizden* çıkan fikirler. Tarama bunları
doğrular/çürütür; doğrulananlar `decisions.md`'ye geçer.

## H1 — Evaluation stil-koşullu olmalı

**Gözlem:** Farklı pixel art stilleri farklı özellikler taşır — bazısında siyah
kontur (outline) *zorunlu*, bazısında (flat/minimalist) *hata*. Dolayısıyla
`edge_density` gibi bir metrik bir stilde "iyi", başkasında "kötü" demek.

**Hipotez:** Metrikleri pass/fail evrensel eşikle değil, **o stilin referans
dağılımına** göre değerlendirmeli (beklenen aralık → sapma). FID'in stil-bazlı hali.

**Gerekçe:** Tek eşik outline'lı ve outline'sız stili aynı anda cezalandırır/ödüllendirir.

**Sonuç:** Önce bir **pixel-art stil taksonomisi** lazım. Tur 2'de literatürden çıkan
eksenler (senin "siyah kontur" gözlemin literatürde *outline rule* olarak birebir var):

| Eksen | Değerler | Kaynak |
|-------|----------|--------|
| Outline | siyah / renkli / yok (karıştırma kötü durur) | style guide'lar |
| Çözünürlük+karmaşıklık | 8–16px (4-16 renk, AA yok) · 16–32px (16-32 renk, AA+dither, örn. Stardew) · 32–128px+ (zengin palet, sub-pixel) | Sprite-AI guide |
| Dithering | var / yok (+ desen tipi) | Pixnote/drububu |
| Projeksiyon | isometric / non-isometric | Wikipedia |
| Detay seviyesi | minimalist (bold silhouette) / detaylı (palet ramp) | style guide'lar |

Bu eksenler hem stil-koşullu eval'in referans gruplarını, hem de dataset etiketlemesini
tanımlar. → RQ-E5, RQ-E6.

## H2 — Her şey model işi değil (sorumluluk dağılımı)

**Gözlem:** Bazı stil nitelikleri deterministik post-process ile ucuza + kusursuz
sağlanır; modeli bununla yormak yanlış.

| Nitelik | Aday sorumlu | Not |
|---------|--------------|-----|
| Palet sınırı | post-process (quantize) | zaten yapıyoruz |
| Grid hizası | post-process (downscale) | model pixel-perfect olmak zorunda değil |
| Siyah kontur | post-process *veya* model | bilinçli seçim — deney gerektirir |
| Şekil / içerik / oran | model (LoRA) | semantik, post-process üretemez |

**Sonuç:** Bu "sorumluluk matrisi" LoRA'da neyi öğretmeye çalışacağımızı belirler
→ doğrudan RQ-L1'i etkiler, o yüzden ondan önce. → RQ-X1.

## H3 — Metriklerimiz büyük ölçüde ortogonal (ama bazıları gereksiz)

**Kaynak:** ilk korelasyon matrisi (6 metrik, N örnek). Notlar:

- **Grid Valid: varyans ~0** (satır boş) → bu örneklemde bilgi taşımıyor. Muhtemelen
  post-process onu zaten garantiliyor (→ H2'yi destekler). Metrik olarak kalmalı mı,
  yoksa "her zaman geçiyor" bir invariant mı? Karar gerek.
- **Palette Valid ↔ Color Eff. = −0.47** → en güçlü ilişki; kısmen aynı şeyi ölçüyor
  olabilirler → biri elenebilir.
- **Edge Density ↔ Color Eff. (0.42), ↔ Fill Balance (0.40)** → outline/doluluk ekseni.
- Genel: çoğu |r| < 0.3 → metrikler büyük ölçüde bağımsız (iyi haber, gereksiz değiller).

**Aksiyon:** Korelasyon matrisini yeni metrik ekledikçe yeniden üret; |r| yüksek çiftlerde
birini ele. → RQ-E6.

---

_Not: korelasyon görseli git'e girmiyor (.gitignore *.png). Sayılar yukarıda transkript._
