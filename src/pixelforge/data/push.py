"""İşlenmiş dataset'i HF Hub'a versiyonlu push (ADR-2/8: kayıt Hub'da, git'te değil).

huggingface_hub gerekir → `pip install -e ".[data]"`. Lazy import: bu dosyayı import
etmek [data] kurulu olmayan ortamı çökertmez.

CLI:
    huggingface-cli login          # bir kez, token gir
    python -m pixelforge.data.push --dir data/processed/kenney-v1 \
        --repo <kullanıcı>/pixelforge-kenney-tiny-v1
"""

from __future__ import annotations

from pathlib import Path


def push_dataset(local_dir: str | Path, repo_id: str, *, private: bool = True) -> str:
    """local_dir'i (images/ + manifest.json) bir HF dataset repo'suna yükler.

    Returns repo URL. Token için önce `huggingface-cli login`.
    """
    from huggingface_hub import HfApi  # lazy: [data] extra

    local_dir = Path(local_dir)
    if not (local_dir / "manifest.json").exists():
        raise FileNotFoundError(f"{local_dir}/manifest.json yok — önce ingest çalıştır")

    api = HfApi()
    api.create_repo(repo_id, repo_type="dataset", private=private, exist_ok=True)
    api.upload_folder(
        folder_path=str(local_dir),
        repo_id=repo_id,
        repo_type="dataset",
        commit_message="pixelforge dataset push",
    )
    return f"https://huggingface.co/datasets/{repo_id}"


def main(argv: list[str] | None = None) -> None:
    import argparse

    p = argparse.ArgumentParser(description="İşlenmiş dataset → HF Hub")
    p.add_argument("--dir", required=True, help="data/processed/... dizini")
    p.add_argument("--repo", required=True, help="<kullanıcı>/<dataset-adı>")
    p.add_argument("--public", action="store_true", help="public yap (varsayılan private)")
    args = p.parse_args(argv)

    url = push_dataset(args.dir, args.repo, private=not args.public)
    print(f"push OK → {url}")


if __name__ == "__main__":
    main()
