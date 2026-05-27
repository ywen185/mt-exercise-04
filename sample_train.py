from pathlib import Path
import random
import argparse


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

SRC_FILE = DATA / "train.en"
TRG_FILE = DATA / "train.nl"

OUT_SRC_FILE = DATA / "train_new.en"
OUT_TRG_FILE = DATA / "train_new.nl"

RANDOM_SEED = 42


def main() -> None:
    """
    Randomly sample parallel sentence pairs from the training data.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sample_size",
        type=int,
        required=True,
        help="Number of parallel sentence pairs to sample.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=RANDOM_SEED,
        help="Random seed for reproducible sampling.",
    )
    args = parser.parse_args()

    random.seed(args.seed)

    src_lines = SRC_FILE.read_text(encoding="utf-8").splitlines()
    trg_lines = TRG_FILE.read_text(encoding="utf-8").splitlines()

    if len(src_lines) != len(trg_lines):
        raise ValueError("Source and target files have different numbers of lines.")

    total_lines = len(src_lines)

    if args.sample_size > total_lines:
        raise ValueError(
            f"Sample size {args.sample_size} is larger than total sentence pairs {total_lines}."
        )

    indices = random.sample(range(total_lines), args.sample_size)
    indices.sort()

    with OUT_SRC_FILE.open("w", encoding="utf-8") as src_out, OUT_TRG_FILE.open(
        "w", encoding="utf-8"
    ) as trg_out:
        for i in indices:
            src_out.write(src_lines[i] + "\n")
            trg_out.write(trg_lines[i] + "\n")

if __name__ == "__main__":
    main()