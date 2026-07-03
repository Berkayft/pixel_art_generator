# 04 — Değerlendirme (ML Çekirdeği)

Bir demo ile bir ML sistemi arasındaki fark: **kaliteyi ölçebilmek.** Ground-truth
gerektirmeyen, deterministik, GPU'suz metrikler (`eval/metrics.py`).

## Metrik haritası

```mermaid
flowchart TD
    IMG[asset görseli] --> CC[color_count<br/>benzersiz renk sayısı]
    IMG --> PA[palette_adherence<br/>hedefe uyum 0..1]
    IMG --> ES[edge_sharpness<br/>anti-aliasing yokluğu 0..1]
    IMG --> GA[grid_alignment_score<br/>blok düzgünlüğü 0..1]

    CC --> PA
    PA --> AGG[evaluate_asset → dict]
    ES --> AGG
    AGG --> RES[GenerationResult.metrics]
    GA -.ham/preview için ayrı.-> RES

    classDef m fill:#1f3d2f,stroke:#6fd69a,color:#fff
    class CC,PA,ES,GA,AGG m
```

## Her metrik neyi yakalar?

| Metrik | Ölçtüğü | "İyi" | Yakaladığı hata |
|--------|---------|-------|-----------------|
| `color_count` | benzersiz RGB sayısı | ham sayı | — (girdi) |
| `palette_adherence` | renk hedefe uyuyor mu | 1.0 | çok renkli = "sahte" pixel art |
| `grid_alignment_score` | NxN bloklara ayrışıyor mu | ~1.0 | bulanık, grid-dışı görsel |
| `edge_sharpness` | kenarlar keskin mi | →1.0 | anti-aliasing halkaları |

## grid_alignment nasıl çalışır?

```mermaid
flowchart LR
    subgraph İyi["gerçek pixel art"]
        G1["her blok<br/>tek düz renk"] --> G2["blok-içi std ≈ 0"] --> G3["skor ≈ 1.0"]
    end
    subgraph Kötü["sahte / bulanık"]
        B1["blok içinde<br/>renk dalgalanır"] --> B2["blok-içi std yüksek"] --> B3["skor düşük"]
    end
```

Görüntüyü `block_size × block_size` bloklara böler, her bloğun renk **std**'sini ölçer.
Gerçek pixel art'ta bloklar düz → std ~0 → skor ~1. Formül: `1 − ortalama_std / 128`.

## Neden bu, projenin merkezi?

```mermaid
flowchart LR
    E[eval metrikleri] --> R[Regresyon:<br/>bir agent pipeline'ı<br/>bozarsa CI yakalar]
    E --> X[Experiment kıyası:<br/>LoRA-v1 vs v2<br/>hangisi daha iyi?]
    E --> A[Otomasyon:<br/>N seed üret,<br/>en iyi metriği seç]
```

## Sırada ne var (Faz 1)

- **CLIP prompt-sadakati** metriği (torch ister → ayrı modül, lazy). "Prompt'a ne kadar
  uyuyor" sorusunu sayısallaştırır — "8 kol tutmuyor"un ölçülebilir hali.
- **Tileability** (tileset kenar sürekliliği) ve **transparency** (temiz alpha) metrikleri.
