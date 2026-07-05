# Kaynak Günlüğü

Taranan HER kaynak buraya bir satır — dahil ya da elendi + **neden**. Bu iz,
taramayı tekrarlanabilir kılar (aynı reproducibility ilkesi).

Durum: `INCLUDE` (→ papers/'a not) · `SKIM` (künye + 1 cümle) · `EXCLUDE` (elendi).

| # | Kaynak (başlık / url) | Topic | Durum | Neden |
|---|-----------------------|-------|-------|-------|
| 1 | TIFA: Faithfulness via QA ([2303.11897](https://arxiv.org/pdf/2303.11897)) | eval | INCLUDE | VQA ile prompt-sadakati/counting → RQ-E2 ("8 kol" sorunu) |
| 2 | Evaluating the Evaluators: Compositional T2I ([2509.21227](https://arxiv.org/html/2509.21227v1)) | eval | INCLUDE | "tek metrik yetmez" → çoklu-metrik + RQ-E6 doğruluyor |
| 3 | ImageReward ([2304.05977](https://arxiv.org/html/2304.05977v4)) | eval | INCLUDE | insan-tercihi reward model; FID/CLIP sınırları → RQ-E1 |
| 4 | Deep Unsupervised Pixelization, TOG'18 ([ACM](https://dl.acm.org/doi/10.1145/3272127.3275082)) | postprocess | INCLUDE | öğrenilmiş pixelization (GridNet+PixelNet) → RQ-P1, X1 |
| 5 | Pixel VQ-VAE ([2203.12130](https://arxiv.org/pdf/2203.12130)) | eval | INCLUDE | pixel-art embedding → stil-koşullu eval adayı → RQ-E5 |
| 6 | Pixel Art Bench (HF blog) | eval | SKIM | "Pixel Art Quality" = grid+palet geçerliliği; ama LLM/yapısal üretim odaklı |
| 7 | GLIPS: perceptual photorealism ([2405.09426](https://arxiv.org/html/2405.09426v2)) | eval | EXCLUDE | fotogerçekçilik metriği, pixel-art'a ters |
| 8 | Learning the Artness of AI images ([2305.04923](https://arxiv.org/pdf/2305.04923)) | eval | SKIM | "sanatsallık" ölçümü — stil-eval için ilham, doğrudan değil |
| 9 | PixelRL ([1912.07190](https://arxiv.org/pdf/1912.07190)) | postprocess | EXCLUDE | genel görüntü işleme RL, pixel-art'a özgü değil |
| 10 | HPS v2 / PickScore / MPS (survey içi) | eval | SKIM | insan-tercihi reward ailesi; künye takip → RQ-E1 |
| 11 | Rethinking FID → CMMD, CVPR'24 ([2401.09603](https://arxiv.org/abs/2401.09603)) | eval | INCLUDE | FID önyargılı/örneklem-duyarlı; CMMD küçük-örneklem-dostu → RQ-E1/E5 |
| 12 | Pixel VQ-VAE repo ([fusion-dance](https://github.com/akashsara/fusion-dance)) | eval | INCLUDE | açık kod + Pokémon sprite eğitimi → pixel-art-CMMD mümkün |
| 13 | Pixel Art (Wikipedia) | eval | SKIM | taksonomi: isometric/non-iso, çözünürlük katmanları |
| 14 | 2D Pixel Art Style Guide, Sprite-AI | eval | SKIM | stil eksenleri: 8-bit→HD, palet/AA/dithering katmanları |
| 15 | Dithering Guide (Pixnote / drububu) | postprocess | SKIM | dithering desenleri → RQ-P2 (quantization+dither) |
| 16 | Navigating T2I Customization: LyCORIS→Eval ([2309.14859](https://arxiv.org/html/2309.14859v2)) | lora | INCLUDE | LyCORIS yöntemleri + eval köprüsü → RQ-L1/L3 |
| 17 | LyCORIS repo ([KohakuBlueleaf](https://github.com/KohakuBlueleaf/LyCORIS)) | lora | SKIM | LoCon/LoHa/LoKr/DoRA implementasyonu → RQ-L3 |
| 18 | Block-wise LoRA ([2403.07500](https://arxiv.org/pdf/2403.07500)) | lora | SKIM | stilizasyon için blok-bazlı LoRA → RQ-L4 (nerede öğreniyor) |
| 19 | SDXL LoRA + captioning guide'ları (Multic/viewcomfy/RunDiffusion) | lora | SKIM | dataset boyutu + tag caption + trigger → RQ-L2 |
| 20 | Personalization karşılaştırması (andyhtu / bosonbrain) | lora | SKIM | LoRA vs DreamBooth vs TI trade-off → RQ-L1 |
