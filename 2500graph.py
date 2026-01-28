import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="CSV file: t_us,raw,level")
    ap.add_argument("--save", help="Save plot to file (png/pdf)")
    ap.add_argument("--smooth", type=int, default=15,
                    help="Smoothing window (samples), default=15")
    ap.add_argument("--t-min", type=float, default=None,
                    help="Start time in seconds (e.g. 5.0)")
    ap.add_argument("--t-max", type=float, default=None,
                    help="End time in seconds (e.g. 15.8)")
    args = ap.parse_args()

    df = pd.read_csv(args.csv, header=None, names=["t_us", "raw", "level"])

    t0 = df["t_us"].iloc[0]
    df["t_s"] = (df["t_us"] - t0) / 1_000_000.0

    if args.t_min is not None:
        df = df[df["t_s"] >= args.t_min]
    if args.t_max is not None:
        df = df[df["t_s"] <= args.t_max]

    df["level_smooth"] = df["level"].rolling(
        window=args.smooth, center=True, min_periods=1
    ).mean()

    plt.figure(figsize=(10, 5))

    # Smoothed curve
    plt.plot(df["t_s"], df["level_smooth"], linewidth=1.2, label="Smoothed")

    # Raw faint curve
    plt.plot(df["t_s"], df["level"], linewidth=0.5, alpha=0.25, label="Raw")

    plt.xlabel("Time (s)")
    plt.ylabel("Level (ADC counts)")
    plt.title("Level vs Time")

    plt.ylim(2100, 2400)
    plt.yticks(np.arange(2100, 2401, 25))

    if len(df) > 0:
        t_min = df["t_s"].min()
        t_max = df["t_s"].max()
        plt.xticks(np.arange(np.floor(t_min), np.ceil(t_max) + 1, 1.0))

    plt.grid(True, which="both", alpha=0.3)
    plt.legend()

    if args.save:
        plt.savefig(args.save, dpi=200, bbox_inches="tight")
    else:
        plt.show()

if __name__ == "__main__":
    main()
