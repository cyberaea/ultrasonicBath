import argparse
import pandas as pd
import numpy as np

def segments_from_state(t_s: np.ndarray, state: np.ndarray):
    """Return list of (t_start, t_end, i_start, i_end) for contiguous True runs."""
    segs = []
    n = len(state)
    i = 0
    while i < n:
        if not state[i]:
            i += 1
            continue
        j = i + 1
        while j < n and state[j]:
            j += 1
        segs.append((t_s[i], t_s[j-1], i, j-1))
        i = j
    return segs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="CSV file: t_us,raw,level (no header)")
    ap.add_argument("--smooth", type=int, default=51, help="Rolling mean window (samples), default=51")
    ap.add_argument("--off-th", type=float, default=900.0,
                    help="OFF threshold for level (below => OFF), default=900")
    ap.add_argument("--on-th", type=float, default=1200.0,
                    help="ON threshold for level (above => ON), default=1200")
    ap.add_argument("--min-on-s", type=float, default=6.0,
                    help="Minimum ON segment duration (s) to keep, default=6")
    ap.add_argument("--min-off-s", type=float, default=0.5,
                    help="Minimum OFF duration (s) between ON segments (helps debouncing), default=0.5")
    args = ap.parse_args()

    df = pd.read_csv(args.csv, header=None, names=["t_us", "raw", "level"])
    t0 = df["t_us"].iloc[0]
    t_s = ((df["t_us"] - t0) / 1_000_000.0).to_numpy()

    level = df["level"].astype(float)

    w = max(1, int(args.smooth))
    if w > 1:
        level_s = level.rolling(w, center=True, min_periods=1).mean().to_numpy()
    else:
        level_s = level.to_numpy()

    state_on = np.zeros_like(level_s, dtype=bool)
    on = False
    for i, x in enumerate(level_s):
        if (not on) and (x >= args.on_th):
            on = True
        elif on and (x <= args.off_th):
            on = False
        state_on[i] = on

    segs = segments_from_state(t_s, state_on)

    segs = [s for s in segs if (s[1] - s[0]) >= args.min_on_s]

    merged = []
    for s in segs:
        if not merged:
            merged.append(list(s))
            continue
        prev = merged[-1]
        gap = s[0] - prev[1]
        if gap <= args.min_off_s:
            # merge
            prev[1] = s[1]
            prev[3] = s[3]
        else:
            merged.append(list(s))
    segs = [(a,b,c,d) for a,b,c,d in merged]

    if not segs:
        print("No ON segments detected. Try adjusting --on-th/--off-th or --smooth.")
        return

    mask = np.zeros(len(df), dtype=bool)
    for _, _, i0, i1 in segs:
        mask[i0:i1+1] = True

    on_levels = df.loc[mask, "level"].astype(float).to_numpy()
    mean_on = float(np.mean(on_levels))
    std_on  = float(np.std(on_levels))
    n_on    = int(on_levels.size)
    total_on_time = float(np.sum(mask) * np.median(np.diff(t_s)))

    print("Detected ON intervals (seconds from start):")
    for k, (t1, t2, i0, i1) in enumerate(segs, 1):
        print(f"{k}: ON at {t1:.3f}s  OFF at {t2:.3f}s   duration={t2-t1:.2f}s")

    print("\nMean level while ON:")
    print(f"mean={mean_on:.2f}  std={std_on:.2f}  samples={n_on}  approx_on_time={total_on_time:.1f}s")

if __name__ == "__main__":
    main()
