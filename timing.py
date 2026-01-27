import argparse
import pandas as pd
import numpy as np

def robust_sigma(x: np.ndarray) -> float:
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    return 1.4826 * mad if mad > 0 else np.std(x)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="CSV file: t_us,raw,level (no header)")
    ap.add_argument("--min-gap-s", type=float, default=1.0,
                    help="Minimum time between events (seconds), default=1.0")
    ap.add_argument("--k", type=float, default=8.0,
                    help="Threshold multiplier for derivative (robust sigma), default=8.0")
    ap.add_argument("--smooth", type=int, default=11,
                    help="Rolling mean window (samples) before detection, default=11")
    args = ap.parse_args()

    df = pd.read_csv(args.csv, header=None, names=["t_us", "raw", "level"])
    t0 = df["t_us"].iloc[0]
    df["t_s"] = (df["t_us"] - t0) / 1_000_000.0

    level = df["level"].astype(float)
    if args.smooth and args.smooth > 1:
        level = level.rolling(args.smooth, center=True, min_periods=1).mean()

    d = level.diff().fillna(0.0).to_numpy()
    sig = robust_sigma(d)
    if sig == 0:
        sig = np.std(d) if np.std(d) > 0 else 1.0

    thr = args.k * sig

    cand = np.where(np.abs(d) > thr)[0]

    events = []
    last_t = -1e9
    for idx in cand:
        t = float(df["t_s"].iloc[idx])
        if t - last_t < args.min_gap_s:
            continue

        kind = "ON" if d[idx] > 0 else "OFF"
        amp = float(d[idx])
        events.append((t, kind, idx, amp))
        last_t = t

    print(f"Detected events: {len(events)}")
    print("time_s,type,index,delta_level")
    for t, kind, idx, amp in events:
        print(f"{t:.3f},{kind},{idx},{amp:.1f}")

if __name__ == "__main__":
    main()
