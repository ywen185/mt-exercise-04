from pathlib import Path
import sys

def main():

    hyp_file = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        num_examples = int(sys.argv[2])
    else:
        num_examples = 50

    src_file = Path("data/test.en")
    ref_file = Path("data/test.nl")

    if not hyp_file.exists():
        raise FileNotFoundError(f"Cannot find hypothesis file: {hyp_file}")

    if not src_file.exists():
        raise FileNotFoundError(f"Cannot find source file: {src_file}")

    if not ref_file.exists():
        raise FileNotFoundError(f"Cannot find reference file: {ref_file}")

    src_lines = src_file.read_text(encoding="utf-8").splitlines()
    ref_lines = ref_file.read_text(encoding="utf-8").splitlines()
    hyp_lines = hyp_file.read_text(encoding="utf-8").splitlines()

    n = min(num_examples, len(src_lines), len(ref_lines), len(hyp_lines))

    output_name = hyp_file.name.replace(".hyps.test", ".manual_check.txt")

    output_file = hyp_file.parent / output_name

    lines = []
    lines.append(f"Using hypothesis file: {hyp_file}")
    lines.append(f"Number of examples: {n}")
    lines.append("")

    for i in range(n):
        lines.append(f"Sentence {i + 1}")
        lines.append(f"SRC: {src_lines[i]}")
        lines.append(f"REF: {ref_lines[i]}")
        lines.append(f"HYP: {hyp_lines[i]}")
        lines.append("")

    text = "\n".join(lines)

    output_file.write_text(text, encoding="utf-8")

    print(f"Saved manual check file to: {output_file}")

if __name__ == "__main__":
    main()