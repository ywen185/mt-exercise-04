#!/usr/bin/env python3

import argparse
from pathlib import Path
from datasets import load_dataset, get_dataset_config_names


def write_split(dataset, split_name, src, trg, out_dir):
    src_file = out_dir / f"{split_name}.{src}"
    trg_file = out_dir / f"{split_name}.{trg}"

    with src_file.open("w", encoding="utf-8") as fs, trg_file.open("w", encoding="utf-8") as ft:
        for ex in dataset:
            trans = ex["translation"]
            fs.write(trans[src].strip() + "/n")
            ft.write(trans[trg].strip() + "/n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True, help="Source language, e.g. en")
    parser.add_argument("--trg", required=True, help="Target language, e.g. nl")
    parser.add_argument("--out", default="data", help="Output directory")
    parser.add_argument("--max-train", type=int, default=100000)
    args = parser.parse_args()

    if args.src == "de" and args.trg == "en":
        raise ValueError("de-en is not allowed for this exercise.")

    config = f"iwslt2017-{args.src}-{args.trg}"

    available = get_dataset_config_names("IWSLT/iwslt2017")#, trust_remote_code=True)
    if config not in available:
        raise ValueError(
            f"Config {config} not available on Hugging Face. "
            f"Try another direction, e.g. en-nl, en-it, en-ro, nl-en, it-en, ro-en."
        )

    project_root = Path(__file__).resolve().parent.parent
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = project_root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    ds = load_dataset("IWSLT/iwslt2017", config, trust_remote_code=True)

    train = ds["train"]
    if args.max_train:
        train = train.select(range(min(args.max_train, len(train))))

    write_split(train, "train", args.src, args.trg, out_dir)
    write_split(ds["validation"], "dev", args.src, args.trg, out_dir)
    write_split(ds["test"], "test", args.src, args.trg, out_dir)

    print("Created files:")
    for path in sorted(out_dir.glob("*")):
        print(path)

    print("/nLine counts:")
    for path in sorted(out_dir.glob("*")):
        with path.open(encoding="utf-8") as f:
            print(sum(1 for _ in f), path)


if __name__ == "__main__":
    main()