import argparse
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="CSV file: t_us,raw,level")
    args = ap.parse_args()

    df = pd.read_csv(args.csv, header=None, names=["t_us", "raw", "level"])

    mean_raw = df["raw"].mean()
    std_raw  = df["raw"].std()

    print(f"Mean raw = {mean_raw:.2f}")
    print(f"Std  raw = {std_raw:.2f}")
    print(f"Suggested baseline constant = {int(round(mean_raw))}")

if __name__ == "__main__":
    main()
