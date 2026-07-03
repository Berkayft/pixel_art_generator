# 05 — Yol Haritası

## Fazlar

```mermaid
flowchart LR
    F0["Faz 0 ✅<br/>Temel iskelet<br/>paket + eval + test"]
    F1["Faz 1<br/>Statik + kendi LoRA'n"]
    F2["Faz 2<br/>Kalite & kontrol"]
    F3["Faz 3<br/>Serving (basit)"]
    F4["Faz 4<br/>Animasyon"]

    F0 --> F1 --> F2 --> F3 --> F4

    classDef done fill:#1f3d2f,stroke:#6fd69a,color:#fff
    classDef next fill:#3b2f5e,stroke:#8b7fd6,color:#fff
    class F0 done
    class F1 next
```

## Faz detayları

| Faz | Amaç | Ana işler | Durum |
|-----|------|-----------|-------|
| **0** | demo → sistem | paket, kontrat, postprocess, eval, test, CI-hazır | ✅ tamam |
| **1** | statik + LoRA | dataset (Kenney/CC0) → HF Hub · CLIP metriği · ilk SD1.5 LoRA eğitimi · W&B takibi | ▶ sırada |
| **2** | kalite & kontrol | transparency/bg-removal · sprite set tutarlılığı · SDXL'e yükseltme · ControlNet (poz) | |
| **3** | serving | Gradio app + CLI · model registry (HF Hub) · basit maliyet/latency izleme | |
| **4** | animasyon | keyframe + interpolasyon · sprite sheet üretimi · temporal tutarlılık | |

## Faz 1 — yakın plan

```mermaid
flowchart TD
    D[1. Dataset curation<br/>Kenney CC0 · 50-300 tutarlı görsel] --> DV[HF Hub'a versiyonla]
    C[2. CLIP prompt-sadakati metriği<br/>eval'e ekle, lazy torch] --> CI[golden test]
    T[3. SD1.5 LoRA eğitim notebook'u<br/>ince · src/training çağırır] --> W[W&B: loss + örnek grid]
    DV --> T
    C --> T
    W --> M[eval harness ile<br/>LoRA v1 skorla]
```

**Neden SD1.5 önce?** T4'te ~1-2 saatte, hızlı iterasyonla eğitilir; training pipeline'ını
ve eval'i öğrenmek için ideal. Sağlamlaşınca SDXL LoRA'ya yükseltilir.

## MLOps katmanları (ücretsiz yığın)

```mermaid
flowchart LR
    subgraph Ücretsiz["hepsi ücretsiz tier"]
        HF[HF Hub<br/>model + dataset registry]
        WB[W&B<br/>experiment tracking]
        GH[GitHub<br/>kod + CI]
    end
    COLAB[Colab<br/>T4/L4 GPU] --> HF
    COLAB --> WB
    GH --> COLAB
```

## "Repo patlamasın" guardrail'leri (her fazda geçerli)

- Ağırlık/dataset/çıktı **git'e girmez** → HF Hub.
- Yeni ML deps **sert pinli**; çekirdek floor.
- Her yeni davranış **test'li**; `eval` metrikleri regresyon kapısı.
- Notebook **ince**; mantık `src/`'de.
- Modüller arası **tipli kontrat**; sınırlar `CLAUDE.md`'de.
