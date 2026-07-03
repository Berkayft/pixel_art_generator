# pixelforge — Sistem Dokümantasyonu

Bu klasör sistemi **kavramsal** olarak anlatır: ne, neden, nasıl akıyor.
Kod ayrıntısı değil, mimari resim. Kod değiştikçe burası da güncellenmeli.

## İçindekiler

| Dosya | Konu |
|-------|------|
| [01-overview.md](01-overview.md) | Sistem ne yapar, ana fikir, tasarım ilkeleri |
| [02-architecture.md](02-architecture.md) | Katmanlar, bağımlılık yönü, modül sınırları |
| [03-data-flow.md](03-data-flow.md) | Bir prompt'un asset'e dönüşme yolculuğu (sequence) |
| [04-evaluation.md](04-evaluation.md) | "İyi pixel art" nasıl ölçülür — metrikler |
| [05-roadmap.md](05-roadmap.md) | Statik → animasyon fazları, MLOps yol haritası |

## Bir bakışta

```mermaid
flowchart LR
    P[Prompt] --> PIPE[pipeline<br/>SDXL + LoRA]
    PIPE -->|ham görsel| POST[postprocess<br/>küçült → palet → büyüt]
    POST -->|asset| EVAL[eval<br/>kalite metrikleri]
    EVAL --> R[GenerationResult<br/>asset + metrics]

    classDef heavy fill:#3b2f5e,stroke:#8b7fd6,color:#fff
    classDef light fill:#1f3d2f,stroke:#6fd69a,color:#fff
    class PIPE heavy
    class POST,EVAL light
```

> 🟣 Ağır (torch/diffusers, sadece Colab/GPU) &nbsp;&nbsp; 🟢 Hafif (PIL/numpy, her yerde)
