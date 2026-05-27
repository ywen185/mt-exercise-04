from pathlib import Path
import subprocess
import sys

def main():

    hyp_file = Path(sys.argv[1])
    ref_file = Path("data/test.nl")

    if not hyp_file.exists():
        raise FileNotFoundError(f"Cannot find hypothesis file: {hyp_file}")

    if not ref_file.exists():
        raise FileNotFoundError(f"Cannot find reference file: {ref_file}")

    if hyp_file.name.endswith(".hyps.test"):
        detok_name = hyp_file.name.replace(".hyps.test", ".detok")
    else:
        detok_name = hyp_file.name + ".detok"

    detok_file = hyp_file.parent / detok_name

    print(f"Input hypothesis: {hyp_file}")
    print(f"Detok output:     {detok_file}")

    with hyp_file.open("r", encoding="utf-8") as inp, detok_file.open("w", encoding="utf-8") as out:
        for line in inp:
            out.write(line.replace("@@ ", ""))

    print("Computing BLEU...")

    subprocess.run(
        [
            "sacrebleu",
            str(ref_file),
            "-i",
            str(detok_file),
            "-m",
            "bleu",
            "-tok",
            "13a",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()