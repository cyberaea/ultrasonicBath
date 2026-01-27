import argparse
import pandas as pd
import numpy as np

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="CSV file: t_us,raw,level")
    args = ap.parse_args()

    df = pd.read_csv(args.csv, header=None, names=["t_us", "raw", "level"])

    level = df["level"].astype(float).to_numpy()

    rms = np.sqrt(np.mean(level**2))

    print(f"RMS(level) = {rms:.3f}")
    print(f"Rounded     = {int(round(rms))}")

if __name__ == "__main__":
    main()
