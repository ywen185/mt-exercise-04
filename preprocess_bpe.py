from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

def run_cmd(
    cmd: list[str], input_path: Path | None = None, output_path: Path | None = None
) -> None:
    """
    Run a shell command with optional file input and output.
    This is used for learning bpe and applying bpe.
    """
    print("Running:", " ".join(str(x) for x in cmd))

    stdin = open(input_path, "r", encoding="utf-8") if input_path else None
    stdout = open(output_path, "w", encoding="utf-8") if output_path else None

    try:
        subprocess.run(
            cmd,
            stdin=stdin,
            stdout=stdout,
            stderr=sys.stderr,
            check=True,
            text=True,
        )
    finally:
        if stdin:
            stdin.close()
        if stdout:
            stdout.close()


def concat_files(files: list[Path], output_path: Path) -> None:
    """
    Concatenate several text files into one output file.
    This is used to create train.all from train_new.en and train_new.nl.
    """
    print(f"Creating {output_path}")
    with open(output_path, "w", encoding="utf-8") as out:
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                for line in f:
                    out.write(line)


def apply_bpe(
    input_file: Path,
    codes_file: Path,
    output_file: Path,
    vocab_file: Path | None = None,
    threshold: int | None = None,
) -> None:
    """
    Apply BPE codes to an input file.
    If vocab_file and threshold are given, use vocabulary filtering.
    The vocabulary filter limits the BPE output to subword units that appear in the language-specific vocabulary file with a high enough frequency.
    """
    cmd = ["subword-nmt", "apply-bpe", "-c", str(codes_file)]

    if vocab_file is not None:
        cmd.extend(["--vocabulary", str(vocab_file)])

    if threshold is not None:
        cmd.extend(["--vocabulary-threshold", str(threshold)])

    run_cmd(cmd, input_path=input_file, output_path=output_file)


def get_vocab(input_file: Path, output_file: Path, keep_counts: bool) -> None:
    """
    Create a vocabulary file.

    If keep_counts is True, the output keeps both token and frequency count.
    This is for apply-bpe vocabulary filtering.

    If keep_counts is False, only the token column is kept.
    This is for JoeyNMT's voc_file.
    """
    print(f"Creating vocabulary: {output_file}")

    with open(input_file, "r", encoding="utf-8") as inp:
        proc = subprocess.run(
            ["subword-nmt", "get-vocab"],
            stdin=inp,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            check=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

    with open(output_file, "w", encoding="utf-8") as out:
        for line in proc.stdout.splitlines():
            if not line.strip():
                continue

            if keep_counts:
                out.write(line + "\n")
            else:
                token = line.split()[0]
                out.write(token + "\n")


def get_vocab_from_two_files(
    file1: Path, file2: Path, output_file: Path, keep_counts: bool
) -> None:
    """
    Create one shared vocabulary from two BPE-processed files.

    This is used to build a shared JoeyNMT vocabulary from the English and
    Dutch BPE training files. A temporary concatenated file is created first,
    then removed after the vocabulary is written.
    """
    temp_file = output_file.with_suffix(output_file.suffix + ".tmp_concat")
    concat_files([file1, file2], temp_file)
    get_vocab(temp_file, output_file, keep_counts=keep_counts)
    temp_file.unlink()


def main() -> None:
    """
    Run the full BPE preprocessing pipeline.

    The script learns joint BPE codes for English and Dutch,
    creates language specific vocabulary filter files with counts,
    applies BPE with vocabulary filtering to train/dev/test files and creates the shared JoeyNMT vocabulary files without counts.
    """
    print("Creating joint BPE training file")
    concat_files([DATA / "train_new.en", DATA / "train_new.nl"], DATA / "train.all")

    for size in [2000, 5000]:
        codes_file = DATA / f"bpe_{size}.codes"

        run_cmd(
            ["subword-nmt", "learn-bpe", "-s", str(size), "--total-symbols"],
            input_path=DATA / "train.all",
            output_path=codes_file,
        )
        print(f"Learned BPE {size}")

        en_vocab_filter = DATA / f"vocab.bpe{size}.en.with_counts"
        nl_vocab_filter = DATA / f"vocab.bpe{size}.nl.with_counts"

        temp_en_bpe = DATA / f"train.bpe{size}.en.tmp"
        apply_bpe(DATA / "train_new.en", codes_file, temp_en_bpe)
        get_vocab(temp_en_bpe, en_vocab_filter, keep_counts=True)
        temp_en_bpe.unlink()
        print(f"Created BPE {size} English subword vocabulary filter with counts")

        temp_nl_bpe = DATA / f"train.bpe{size}.nl.tmp"
        apply_bpe(DATA / "train_new.nl", codes_file, temp_nl_bpe)
        get_vocab(temp_nl_bpe, nl_vocab_filter, keep_counts=True)
        temp_nl_bpe.unlink()
        print(f"Created BPE {size} Dutch subword vocabulary filter with counts")

        apply_bpe(
            DATA / "train_new.en",
            codes_file,
            DATA / f"train.bpe{size}.en",
            vocab_file=en_vocab_filter,
            threshold=50,
        )

        apply_bpe(
            DATA / "train_new.nl",
            codes_file,
            DATA / f"train.bpe{size}.nl",
            vocab_file=nl_vocab_filter,
            threshold=50,
        )

        apply_bpe(
            DATA / "dev.en",
            codes_file,
            DATA / f"dev.bpe{size}.en",
            vocab_file=en_vocab_filter,
            threshold=50,
        )

        apply_bpe(
            DATA / "dev.nl",
            codes_file,
            DATA / f"dev.bpe{size}.nl",
            vocab_file=nl_vocab_filter,
            threshold=50,
        )

        apply_bpe(
            DATA / "test.en",
            codes_file,
            DATA / f"test.bpe{size}.en",
            vocab_file=en_vocab_filter,
            threshold=50,
        )

        apply_bpe(
            DATA / "test.nl",
            codes_file,
            DATA / f"test.bpe{size}.nl",
            vocab_file=nl_vocab_filter,
            threshold=50,
        )
        print(f"Apply BPE {size} with vocabulary filtering")

        get_vocab_from_two_files(
            DATA / f"train.bpe{size}.en",
            DATA / f"train.bpe{size}.nl",
            DATA / f"vocab.bpe_{size}",
            keep_counts=False,
        )
        print(f"Created JoeyNMT shared vocabulary for BPE {size} without counts")


if __name__ == "__main__":
    main()