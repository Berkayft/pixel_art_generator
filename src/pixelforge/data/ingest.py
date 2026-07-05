"""Ham Kenney pack'lerini → temiz training dataset + manifest.

Akış (ADR-5/7/8/11):
    kaynak dizin(ler) → PNG'leri topla → dedup → QA validate → prepare_tile
    → kategori tag'i (alt-klasör) → processed/ + manifest.json

Mantık burada (test edilebilir); notebook/CLI sadece çağırır. torch import etmez.

CLI:
    python -m pixelforge.data.ingest --src data/raw/kenney_tiny-dungeon/Tiles \
        --out data/processed/kenney-v1 --trigger pxforge --name kenney-lora-v1
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from pixelforge.data.prepare import dedup, image_hash, prepare_tile, validate_pixel_asset
from pixelforge.data.schema import DatasetManifest, ImageRecord


@dataclass
class IngestStats:
    found: int = 0
    duplicates: int = 0
    rejected_qa: int = 0
    kept: int = 0


def _category_tag(png: Path, root: Path, default_tag: str = "tile") -> str:
    """İçerik tag'i (ADR-7): alt-klasör adı (ör. characters/backgrounds); kökteyse default_tag.

    default_tag pack temasını taşır (dungeon/town) — dosya adları anlamsız (tile_0000) olduğu
    ve pack'ler alt-klasörsüz olduğu için tek çeşitlilik kaynağı.
    """
    return png.parent.name.lower() if png.parent != root else default_tag


def build_dataset(
    source_dirs: list[Path],
    out_dir: Path,
    *,
    trigger: str,
    name: str,
    target_res: int = 512,
    source_label: str = "",
    default_tags: list[str] | None = None,
    max_colors: int = 64,
    min_sharpness: float = 0.0,   # kapalı: edge_sharpness palet-rampasını yanlış eler
) -> tuple[DatasetManifest, IngestStats]:
    """Kaynak dizinleri işleyip processed görselleri + manifest'i yazar.

    default_tags: her source_dir için kök-tile tag'i (ör. ["dungeon", "town"]). Verilmezse "tile".
    """
    out_dir = Path(out_dir)
    (out_dir / "images").mkdir(parents=True, exist_ok=True)
    if default_tags is not None and len(default_tags) != len(source_dirs):
        raise ValueError("default_tags uzunluğu source_dirs ile eşleşmeli")

    # 1) topla — (png, root, default_tag, image)
    entries: list[tuple[Path, Path, str, Image.Image]] = []
    for i, root in enumerate(source_dirs):
        root = Path(root)
        tag = default_tags[i] if default_tags else "tile"
        for png in sorted(root.rglob("*.png")):
            try:
                entries.append((png, root, tag, Image.open(png).copy()))
            except OSError:
                continue

    stats = IngestStats(found=len(entries))

    # 2) dedup (içerik hash'i)
    keep_idx = set(dedup([e[3] for e in entries]))
    stats.duplicates = len(entries) - len(keep_idx)

    # 3) QA + prepare + kaydet
    records: list[ImageRecord] = []
    native_sizes: dict[int, int] = {}
    for i, (png, root, tag, img) in enumerate(entries):
        if i not in keep_idx:
            continue
        ok, _ = validate_pixel_asset(img, max_colors=max_colors, min_sharpness=min_sharpness)
        if not ok:
            stats.rejected_qa += 1
            continue
        native_sizes[max(img.size)] = native_sizes.get(max(img.size), 0) + 1
        tile = prepare_tile(img, target_res=target_res)
        fname = f"{image_hash(img)[:12]}.png"
        tile.save(out_dir / "images" / fname)
        records.append(
            ImageRecord(
                path=f"images/{fname}", content_tags=[_category_tag(png, root, tag)]
            )
        )

    stats.kept = len(records)
    native_res = max(native_sizes, key=native_sizes.get) if native_sizes else target_res

    manifest = DatasetManifest(
        name=name,
        trigger=trigger,
        source=source_label,
        native_res=native_res,
        train_res=target_res,
        records=records,
    )
    (out_dir / "manifest.json").write_text(manifest.model_dump_json(indent=2))
    return manifest, stats


def main(argv: list[str] | None = None) -> None:
    import argparse

    p = argparse.ArgumentParser(description="Kenney pack → training dataset")
    p.add_argument("--src", nargs="+", required=True, help="kaynak dizin(ler)")
    p.add_argument(
        "--tags", nargs="*", default=None,
        help="her --src için kök-tile tag'i (ör. dungeon town). Sırayla eşleşir.",
    )
    p.add_argument("--out", required=True, help="çıktı dizini (data/processed/...)")
    p.add_argument("--trigger", default="pxforge")
    p.add_argument("--name", default="kenney-lora-v1")
    p.add_argument("--target-res", type=int, default=512)
    p.add_argument("--source-label", default="Kenney (CC0)")
    p.add_argument("--max-colors", type=int, default=64, help="QA: üst renk sınırı")
    p.add_argument(
        "--min-sharpness",
        type=float,
        default=0.0,
        help="QA: alt kenar-keskinliği. Güvenilir kaynakta 0 (kapalı) tut — "
        "edge_sharpness palet-rampası gölgelemeyi yanlışlıkla eler.",
    )
    args = p.parse_args(argv)

    manifest, stats = build_dataset(
        [Path(s) for s in args.src],
        Path(args.out),
        trigger=args.trigger,
        name=args.name,
        target_res=args.target_res,
        source_label=args.source_label,
        default_tags=args.tags,
        max_colors=args.max_colors,
        min_sharpness=args.min_sharpness,
    )
    print(
        f"bulundu={stats.found} tekrar={stats.duplicates} QA-elendi={stats.rejected_qa} "
        f"→ tutuldu={stats.kept} | native={manifest.native_res}px | {args.out}/manifest.json"
    )


if __name__ == "__main__":
    main()
