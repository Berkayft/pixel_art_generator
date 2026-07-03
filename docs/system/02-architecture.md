# 02 — Mimari

## Katmanlar ve bağımlılık yönü

Bağımlılık **tek yönlüdür**. `pipeline` üsttedir, aşağıdakileri çağırır; alt katmanlar
asla yukarı bakmaz. Bu, `postprocess` ve `eval`'i torch'suz ve bağımsız test edilebilir tutar.

```mermaid
flowchart TD
    subgraph pipeline["pipeline/ 🟣 ağır (torch, diffusers)"]
        GEN[generate.py<br/>PixelArtPipeline]
        CFG[config.py<br/>GenerationRequest/Result]
    end
    subgraph postprocess["postprocess/ 🟢 hafif (PIL)"]
        PIX[pixelate.py]
    end
    subgraph eval["eval/ 🟢 hafif (numpy, PIL)"]
        MET[metrics.py]
    end

    GEN --> PIX
    GEN --> MET
    GEN -.kullanır.-> CFG
    PIX -.üretir.-> CFG
    MET -.üretir.-> CFG

    classDef heavy fill:#3b2f5e,stroke:#8b7fd6,color:#fff
    classDef light fill:#1f3d2f,stroke:#6fd69a,color:#fff
    class GEN,CFG heavy
    class PIX,MET light
```

**Kural:** `postprocess` ve `eval` **asla `torch` import etmez.** Bu sınır bozulursa
yerel testler (GPU'suz) çöker — CI bunu yakalar.

## Modül sorumlulukları

| Modül | Girdi | Çıktı | Bağımlılık |
|-------|-------|-------|------------|
| `pipeline/config` | — | tip tanımları | pydantic |
| `pipeline/generate` | `GenerationRequest` | `GenerationResult` | torch, diffusers `[ml]` |
| `postprocess/pixelate` | ham `Image` | `(asset, preview)` | PIL |
| `eval/metrics` | asset `Image` | `dict[str,float]` | numpy, PIL |

## Kontrat: sistemin bel kemiği

Her şey iki tip üzerinden akar (`pipeline/config.py`):

```mermaid
classDiagram
    class GenerationRequest {
        +str prompt
        +str negative_prompt
        +int steps
        +float guidance_scale
        +int seed
        +int target_res
        +int num_colors
        +full_prompt() str
    }
    class GenerationResult {
        +GenerationRequest request
        +Image raw
        +Image asset
        +Image preview
        +dict metrics
    }
    GenerationResult --> GenerationRequest : içerir
```

`GenerationRequest` serileştirilebilir → config/queue/log'a yazılabilir, reprodüksiyon
için seed'le birlikte saklanır. Bir agent yeni bir parametre eklerken **buradan başlar**,
sonra tüm çağıranları günceller.

## Fiziksel yerleşim

```
src/pixelforge/
├── __init__.py          # torch'suz güvenli import yüzeyi
├── pipeline/
│   ├── config.py        # KONTRATLAR (hafif)
│   ├── generate.py      # inference (ağır, lazy torch)
│   └── __init__.py      # PixelArtPipeline lazy-export
├── postprocess/
│   └── pixelate.py
└── eval/
    └── metrics.py
```

`pipeline/__init__.py`, `PixelArtPipeline`'ı **lazy** export eder (`__getattr__` ile):
`import pixelforge` torch olmadan çökmez; torch ancak gerçekten üretim yapınca yüklenir.
