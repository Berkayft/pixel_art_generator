# Kararlar (ADR — Architecture Decision Records)

Literatür bulgularını **proje kararına** çeviren yer. Her karar: ne, neden, hangi
bulguya dayanıyor. Bu dosya taramanın "çıktısı" — geri kalan her şey buna hizmet eder.

## Şablon

```
### ADR-N: <karar başlığı>
- **Durum:** öneri | kabul | reddedildi | değişti
- **Bağlam:** hangi soru/kısıt bunu gerektirdi
- **Karar:** ne yapıyoruz (somut: rank=16, lr=1e-4 gibi)
- **Dayanak:** hangi makale/bulgu ([[papers/...]], synthesis)
- **Sonuç:** neyi mümkün/imkânsız kılar, riski ne
```

---

## Kararlar

### ADR-1: Dağılım metriği FID değil, KID/CMMD
- **Durum:** öneri
- **Bağlam:** Dataset küçük + tek-stil. FID önyargılı ve örneklem boyutuna duyarlı
  ([[papers/2024-cmmd-rethinking-fid]]) → bu koşulda güvenilmez.
- **Karar:** Dağılımsal kalite için **KID** (hazır implementasyon bol) ile başla; **CMMD**'yi
  pixel-art-aware varyant için hedefle. FID'i birincil metrik yapma.
- **Dayanak:** Rethinking FID (CVPR'24).
- **Sonuç:** Küçük örneklemde güvenilir kıyas; FID'in "büyük N" ihtiyacından kurtuluş.

### ADR-2: pixel-art-aware CMMD prototiple (stil-koşullu eval)
- **Durum:** öneri
- **Bağlam:** "İyi pixel art" stile göre değişir (outline var/yok vb. → [[ideas]] H1).
  Evrensel eşik yanlış; stil-referans dağılımına kıyas gerek.
- **Karar:** CMMD'nin MMD'sini **Pixel-VQ-VAE encoder** ([[papers/2022-pixel-vqvae]],
  repo: fusion-dance) embedding'iyle çalıştır → stil-referans dağılımına pixel-art-farkında
  uzaklık. Faz 1 sonrası prototip; önce Pokémon-eğitimli encoder'ın genellemesini test et.
- **Dayanak:** CMMD + Pixel-VQ-VAE sentezi. Literatürde yok → özgün katkı.
- **Sonuç:** Stil bazlı objektif kalite; genelleme yetmezse encoder'ı kendi dataset'le fine-tune.

### ADR-3: Eval'i tek skora indirgeme — metrik-vektörü tut
- **Durum:** kabul
- **Bağlam:** "Hiçbir tek metrik tüm kompozisyon kategorilerinde korele değil"
  ([[papers/2025-compositional-eval]]); kendi korelasyon matrisimiz metriklerin büyük
  ölçüde ortogonal olduğunu gösteriyor ([[ideas]] H3).
- **Karar:** `evaluate_asset` **dict[str,float] döndürmeye devam** (tek skor değil). Ağırlıklı
  toplam yerine stil-koşullu yorum + Pareto bakışı. Yeni metrik eklendikçe korelasyon
  matrisini yeniden üret, |r| yüksek çiftte birini ele (RQ-E6).
- **Dayanak:** Comp-eval'25 + kendi verimiz.
- **Sonuç:** Bilgi kaybı yok; redundant metrik şişkinliği kontrol altında.

### ADR-4: Counting/TIFA zorunlu metrik değil — önce pilot
- **Durum:** öneri
- **Bağlam:** "8 kol tutmuyor" → TIFA/VQA counting ölçebilir ([[papers/2023-tifa]]) ama
  VQA'nın düşük çözünürlük + stilize pixel-art'ta güvenilirliği bilinmiyor.
- **Karar:** TIFA-tarzı counting'i harness'e **zorunlu koyma**. Küçük bir pilotla pixel-art'ta
  VQA doğruluğunu ölç; güvenilirse opsiyonel metrik olarak ekle.
- **Dayanak:** TIFA + pixel-art domain şüphesi.
- **Sonuç:** Gürültülü metriğe erken bağımlılık yok; pilot sonucu kendisi katkı olur.

### ADR-5: Stil taksonomisi = dataset etiketleme + caption şeması
- **Durum:** öneri
- **Bağlam:** Stil-koşullu eval referans grupları ve LoRA caption'ı ortak bir taksonomi ister.
- **Karar:** [[ideas]] H1'deki 5 eksenli taksonomiyi (outline · çözünürlük+karmaşıklık ·
  dithering · projeksiyon · detay) **dataset etiket şeması** olarak benimse; caption
  stratejisi (RQ-L2) bu etiketleri kullansın.
- **Dayanak:** style guide'lar + stil-koşullu eval ihtiyacı.
- **Sonuç:** Eval ↔ training tek taksonomi üzerinden hizalanır; RQ-L1/L2'yi doğrudan besler.

---

## Kapsam dışı
"İlginç ama bu proje için değil" — silme, buraya not düş.

- _(boş)_
