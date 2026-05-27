from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

EXCEL_FILE = Path("beam_size_BLEU.xlsx")

BLEU= "beam_size_vs_detok_bleu.png"
TIME= "beam_size_vs_generation_time.png"

def main():
    if not EXCEL_FILE.exists():
        raise FileNotFoundError(f"Cannot find Excel file: {EXCEL_FILE}")

    df = pd.read_excel(EXCEL_FILE)
    #print(df)

    x=df['beam_size']
    y1=df['detok_BLEU']
    y2=df['generation_time/sec']

    # Figure 1: beam size vs detok BLEU
    plt.figure()
    plt.plot(x, y1, marker="o")
    plt.xlabel("Beam size")
    plt.ylabel("Detok BLEU")
    plt.title("Impact of beam size on detok BLEU")
    plt.xticks(x)
    plt.grid(True)
    plt.savefig(BLEU, dpi=300, bbox_inches="tight")
    plt.close()

    # Figure 2: beam size vs generation time
    plt.figure()
    plt.plot(x, y2, marker="o")
    plt.xlabel("Beam size")
    plt.ylabel("Generation time (sec)")
    plt.title("Impact of beam size on generation time")
    plt.xticks(x)
    plt.grid(True)
    plt.savefig(TIME, dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved figures:")
    print(BLEU)
    print(TIME)


if __name__ == "__main__":
    main()