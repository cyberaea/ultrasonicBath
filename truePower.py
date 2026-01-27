import argparse
import re
import numpy as np

def parse_two_cols(path: str):
    t_list = []
    T_list = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = re.split(r"[;\s]+", line)
            if len(parts) < 2:
                continue

            t_str = parts[0].replace(",", ".")
            T_str = parts[1].replace(",", ".")
            try:
                t = float(t_str)
                T = float(T_str)
            except ValueError:
                continue

            t_list.append(t)
            T_list.append(T)

    if len(t_list) < 2:
        raise ValueError("Not enough valid rows parsed. Check file format.")

    return np.array(t_list, dtype=float), np.array(T_list, dtype=float)

def linreg_slope(t, T):
    t_mean = t.mean()
    T_mean = T.mean()
    denom = np.sum((t - t_mean) ** 2)
    if denom == 0:
        raise ValueError("All time values are identical.")
    b = np.sum((t - t_mean) * (T - T_mean)) / denom
    a = T_mean - b * t_mean
    return a, b

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="Text/CSV file with two columns: time_s temperature_C")
    ap.add_argument("--mass-kg", type=float, required=True, help="Water mass in kg (e.g. 0.95)")
    ap.add_argument("--c", type=float, default=4186.0, help="Specific heat capacity J/(kg*K), default 4186")
    ap.add_argument("--t-min", type=float, default=None, help="Use only data with t >= t_min")
    ap.add_argument("--t-max", type=float, default=None, help="Use only data with t <= t_max")
    args = ap.parse_args()

    t, T = parse_two_cols(args.file)

    mask = np.ones_like(t, dtype=bool)
    if args.t_min is not None:
        mask &= (t >= args.t_min)
    if args.t_max is not None:
        mask &= (t <= args.t_max)

    t2 = t[mask]
    T2 = T[mask]
    if len(t2) < 2:
        raise ValueError("After trimming, not enough points remain.")

    a, slope = linreg_slope(t2, T2)  
    P = args.mass_kg * args.c * slope 

    T_fit = a + slope * t2
    ss_res = np.sum((T2 - T_fit) ** 2)
    ss_tot = np.sum((T2 - T2.mean()) ** 2)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else float("nan")

    print("=== Calorimetry power estimate ===")
    print(f"Points used: {len(t2)}  time span: {t2.min():.3f} .. {t2.max():.3f} s")
    print(f"Slope dT/dt: {slope:.6f} °C/s  ({slope*60:.4f} °C/min)")
    print(f"Mass: {args.mass_kg:.4f} kg   c: {args.c:.1f} J/(kg*K)")
    print(f"Effective power P = m*c*dT/dt: {P:.3f} W")
    print(f"Fit R^2: {r2:.4f}")
    if slope < 0:
        print("WARNING: slope is negative (temperature decreasing).")

if __name__ == "__main__":
    main()
