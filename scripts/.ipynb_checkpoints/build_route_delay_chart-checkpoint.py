"""Build a refined route-level mean-delay bar chart for the report.

Replaces the original `chart_01_average_delay_by_route.png` with:
  - Color palette aligned with charts 05/06 (per-route colors).
  - 95% confidence interval of the mean as error bars.
  - Per-bar N (sample size) annotation.
  - Sorted ascending by mean delay (most early -> most late).
  - Zero reference line and a dual-direction "early / late" subtitle.

Output: visualizations/chart_01_average_delay_by_route.png
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
PROCESSED = REPO_ROOT / "data" / "processed"
VIZ = REPO_ROOT / "visualizations"
VIZ.mkdir(exist_ok=True)

SELECTED_ROUTES: tuple[str, ...] = (
    "22",
    "Rapid 522",
    "23",
    "Rapid 523",
    "25",
    "60",
)

ROUTE_COLORS: dict[str, str] = {
    "22": "#8c2d04",
    "Rapid 522": "#cc4c02",
    "23": "#ec7014",
    "Rapid 523": "#fe9929",
    "25": "#fec44f",
    "60": "#a6611a",
}


@dataclass(frozen=True)
class RouteStats:
    route_id: str
    n: int
    mean: float
    se: float          # standard error of the mean
    ci95: float        # 95% CI half-width


def compute_route_stats(df: pd.DataFrame) -> list[RouteStats]:
    rows: list[RouteStats] = []
    for rid in SELECTED_ROUTES:
        sub = df.loc[df["route_id"].astype(str) == rid, "computed_delay_sec"].dropna()
        if sub.empty:
            continue
        n = int(len(sub))
        mean = float(sub.mean())
        se = float(sub.std(ddof=1) / np.sqrt(n))
        ci95 = 1.96 * se
        rows.append(RouteStats(rid, n, mean, se, ci95))
    rows.sort(key=lambda r: r.mean)
    return rows


def render(stats: list[RouteStats], out_path: Path) -> None:
    labels = [s.route_id for s in stats]
    means = np.array([s.mean for s in stats])
    cis = np.array([s.ci95 for s in stats])
    colors = [ROUTE_COLORS.get(s.route_id, "#888") for s in stats]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.barh(
        labels,
        means,
        xerr=cis,
        color=colors,
        edgecolor="white",
        linewidth=0.6,
        ecolor="#333",
        capsize=4,
        error_kw={"elinewidth": 1.0},
    )

    # N labels at the outboard end of each bar. Offset scales with the
    # full data range so short bars (e.g. Route 60) and long bars
    # (e.g. Rapid 522) both keep the label clearly off the bar.
    full_range = float((means + cis).max() - (means - cis).min())
    label_offset = full_range * 0.025
    for bar, s in zip(bars, stats):
        x = bar.get_width()
        ci = s.ci95
        if x >= 0:
            text_x = x + ci + label_offset
            ha = "left"
        else:
            text_x = x - ci - label_offset
            ha = "right"
        ax.text(
            text_x,
            bar.get_y() + bar.get_height() / 2,
            f"n = {s.n:,}",
            va="center",
            ha=ha,
            fontsize=9,
            color="#333",
        )

    ax.axvline(0, color="black", linewidth=0.9)
    ax.set_xlabel("Mean arrival delay (seconds)   ←  early                late  →",
                  fontsize=11)
    ax.set_ylabel("Route", fontsize=11)
    ax.set_title(
        "Mean arrival delay by VTA study route",
        fontsize=13,
        weight="bold",
        loc="left",
        pad=14,
    )
    ax.text(
        0,
        1.01,
        "Error bars = 95% CI of the mean. Selected 6 routes only "
        "(8 hr Mon 5/4 sample).",
        transform=ax.transAxes,
        fontsize=9,
        color="#555",
        ha="left",
        va="bottom",
    )

    # Cosmetics
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle=":", alpha=0.35)
    # Leave room on both sides so the N labels never touch the axes.
    pad = full_range * 0.18
    ax.set_xlim(means.min() - cis.max() - pad, means.max() + cis.max() + pad)

    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def main() -> None:
    delay_path = PROCESSED / "cleaned_delay_data.csv"
    df = pd.read_csv(delay_path)
    stats = compute_route_stats(df)

    print("Route-level mean delay (seconds), 5/4 8-hr sample:")
    for s in stats:
        print(f"  {s.route_id:<10s}  mean={s.mean:+7.1f}  "
              f"95% CI=±{s.ci95:5.1f}  n={s.n:,}")

    out_path = VIZ / "chart_01_average_delay_by_route.png"
    render(stats, out_path)
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    main()
