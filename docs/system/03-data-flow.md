# 03 — Veri Akışı

## Bir prompt'un asset'e yolculuğu

```mermaid
sequenceDiagram
    actor U as Kullanıcı
    participant P as PixelArtPipeline
    participant SD as SDXL + LoRA
    participant PX as postprocess.pixelate
    participant EV as eval.metrics

    U->>P: generate(GenerationRequest)
    Note over P: full_prompt = "pixel, " + prompt
    P->>SD: infer(prompt, neg, steps, guidance, seed)
    SD-->>P: ham görsel (bulanık, çok renkli)

    P->>PX: pixelate(raw, target_res, num_colors)
    Note over PX: 1) LANCZOS ile küçült<br/>2) palet quantize<br/>3) NEAREST ile büyüt
    PX-->>P: (asset, preview)

    P->>EV: evaluate_asset(asset, num_colors)
    EV-->>P: {color_count, palette_adherence, edge_sharpness}

    P-->>U: GenerationResult(raw, asset, preview, metrics)
```

## Üç aşamalı dönüşüm (postprocess'in kalbi)

```mermaid
flowchart LR
    A["ham görsel<br/>1024×1024<br/>~yüzlerce renk"]
    B["küçült (LANCZOS)<br/>128×128<br/>alt-piksel gürültü ortalanır"]
    C["palet quantize<br/>128×128<br/>≤ num_colors renk"]
    D["büyüt (NEAREST)<br/>1024×1024<br/>net kenarlı önizleme"]

    A -->|"1"| B -->|"2"| C
    C -->|"asset olarak kaydedilir"| SAVE[(knight.png)]
    C -->|"3"| D
    D -->|"preview olarak gösterilir"| SHOW[ekran]
```

- **asset** = küçük, temiz — oyunda kullanılacak gerçek dosya.
- **preview** = büyütülmüş hali — sadece göz kontrolü için.

## Hız vs. sadakat: iki mod

Aynı akış, iki farklı ayarla çalışır:

```mermaid
flowchart TB
    R[GenerationRequest]
    R --> D{use_lcm?}
    D -->|"LCM açık<br/>steps=8, guidance=1.5"| FAST["⚡ Hız modu<br/>~2 sn<br/>prompt sadakati düşük"]
    D -->|"LCM kapalı<br/>steps=30, guidance=7.5"| QUAL["🎯 Kalite modu<br/>yavaş<br/>prompt'a sadık"]
```

"8 kol / 4 göz tutmuyor" sorunu → **kalite modu** + tanımlayıcı prompt ile iyileşir
(ama kesin sayı hiçbir modda garanti değil; diffusion'ın doğal sınırı).
