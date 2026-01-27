import argparse
import pandas as pd
import numpy as np

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="CSV file: t_us,raw,level")
    ap.add_argument("--level-th", type=float, default=50,
                    help="Level threshold for idle detection (default=50)")
    ap.add_argument("--min-idle-s", type=float, default=5,
                    help="Minimum idle duration in seconds (default=5)")
    args = ap.parse_args()

    df = pd.read_csv(args.csv, header=None, names=["t_us", "raw", "level"])

    t0 = df["t_us"].iloc[0]
    df["t_s"] = (df["t_us"] - t0) / 1_000_000.0

    idle_mask = df["level"] < args.level_th

    dt = np.median(np.diff(df["t_s"]))

    min_idle_samples = int(args.min_idle_s / dt)

    idle_segments = []
    i = 0
    n = len(df)
    while i < n:
        if not idle_mask.iloc[i]:
            i += 1
            continue
        j = i + 1
        while j < n and idle_mask.iloc[j]:
            j += 1
        if (j - i) >= min_idle_samples:
            idle_segments.append((i, j))
        i = j

    if not idle_segments:
        print("❌ No idle segments detected. Try increasing --level-th")
        return

    raw_vals = []
    for i0, i1 in idle_segments:
        raw_vals.append(df["raw"].iloc[i0:i1])

    raw_vals = pd.concat(raw_vals)

    baseline = raw_vals.mean()
    std = raw_vals.std()

    print("Detected idle segments:", len(idle_segments))
    print(f"Baseline raw = {baseline:.2f} ± {std:.2f}")
    print(f"Suggested baseline constant: {int(round(baseline))}")

if __name__ == "__main__":
    main()
