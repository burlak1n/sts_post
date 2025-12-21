import csv
from datetime import datetime, timedelta
from typing import List

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def read_csv(filename: str) -> List[datetime]:
    timestamps = []
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("confirmed") == "1" and row.get("registered_at"):
                try:
                    ts = datetime.strptime(row["registered_at"], "%Y-%m-%d %H:%M:%S")
                    ts = ts + timedelta(hours=3)
                    timestamps.append(ts)
                except ValueError:
                    continue
    return sorted(timestamps)


def plot_registration_timeline(
    timestamps: List[datetime], output_file: str = "temporal_distribution.png"
):
    if not timestamps:
        print("Нет данных для построения графика")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    cumulative = list(range(1, len(timestamps) + 1))

    ax.plot(timestamps, cumulative, marker="o", linewidth=2, markersize=6)

    if timestamps:
        markers = [
            (14, 14, "14:14 - пост", "red", "yellow"),
            (14, 17, "14:17 - активные соо", "blue", "lightblue"),
            (14, 20, "14:20 - телеграммный соо", "green", "lightgreen"),
        ]

        max_y = max(cumulative) if cumulative else 1
        y_positions = [max_y * 0.95, max_y * 0.85, max_y * 0.75]

        for idx, (hour, minute, label, color, bg_color) in enumerate(markers):
            highlight_time = timestamps[0].replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )
            ax.axvline(
                x=highlight_time,
                color=color,
                linestyle="--",
                linewidth=2,
                alpha=0.7,
            )
            ax.text(
                highlight_time,
                y_positions[idx],
                label,
                rotation=90,
                verticalalignment="top",
                fontsize=9,
                color=color,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor=bg_color, alpha=0.7),
            )

    ax.set_xlabel("Время", fontsize=12)
    ax.set_ylabel("Количество людей", fontsize=12)
    ax.set_title("Временное распределение регистраций", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, linestyle="--")

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    print(f"\nГрафик сохранен: {output_file}")
    plt.close()


def main():
    import sys

    filename = sys.argv[1] if len(sys.argv) > 1 else "input.csv"

    timestamps = read_csv(filename)
    if not timestamps:
        print("Нет подтвержденных пользователей с временными метками")
        return

    print(f"Найдено подтвержденных пользователей: {len(timestamps)}")
    print(
        f"Период: {timestamps[0].strftime('%Y-%m-%d %H:%M')} - {timestamps[-1].strftime('%Y-%m-%d %H:%M')}"
    )

    plot_registration_timeline(timestamps)


if __name__ == "__main__":
    main()
