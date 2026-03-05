from __future__ import annotations

import csv
from pathlib import Path


def _to_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return float("nan")


def main() -> None:
    base_dir = Path(__file__).resolve().parents[1]
    reports_dir = base_dir / "parity_reports"
    source_csv = reports_dir / "dx2_value_comparison.csv"
    out_csv = reports_dir / "dx2_hotspot_summary.csv"
    out_md = reports_dir / "dx2_hotspot_summary.md"

    if not source_csv.exists():
        raise FileNotFoundError(
            "Missing parity_reports/dx2_value_comparison.csv. "
            "Generate it first with the DX2 value comparison script."
        )

    with source_csv.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    grouped: dict[tuple[str, str, str], dict[str, float | int]] = {}
    for row in rows:
        key = (row["function"], row["mode"], row["matrix"])
        diff = _to_float(row["difference"])
        pct_m = _to_float(row["difference_over_matlab_value_pct"])
        pct_p = _to_float(row["difference_over_python_value_pct"])
        pct_max = max(pct_m, pct_p)

        bucket = grouped.setdefault(
            key,
            {
                "count": 0,
                "max_difference": 0.0,
                "max_pct": 0.0,
                "sum_pct": 0.0,
            },
        )
        bucket["count"] = int(bucket["count"]) + 1
        bucket["max_difference"] = max(float(bucket["max_difference"]), diff)
        bucket["max_pct"] = max(float(bucket["max_pct"]), pct_max)
        bucket["sum_pct"] = float(bucket["sum_pct"]) + pct_max

    summary_rows: list[dict[str, str | int | float]] = []
    for (function, mode, matrix), bucket in grouped.items():
        count = int(bucket["count"])
        mean_pct = float(bucket["sum_pct"]) / count if count else 0.0
        summary_rows.append(
            {
                "function": function,
                "mode": mode,
                "matrix": matrix,
                "count": count,
                "max_difference": float(bucket["max_difference"]),
                "max_pct": float(bucket["max_pct"]),
                "mean_pct": mean_pct,
            }
        )

    summary_rows.sort(key=lambda r: (float(r["max_pct"]), float(r["max_difference"])), reverse=True)

    headers = [
        "function",
        "mode",
        "matrix",
        "count",
        "max_difference",
        "max_pct",
        "mean_pct",
    ]

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(summary_rows)

    md_lines = [
        "# DX2 Hotspot Summary",
        "",
        "Grouped by `function + mode + matrix`, ranked by `max_pct`.",
        "",
        "| function | mode | matrix | count | max_difference | max_pct | mean_pct |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        md_lines.append(
            (
                "| {function} | {mode} | {matrix} | {count} | {max_difference:.6e} "
                "| {max_pct:.6e} | {mean_pct:.6e} |"
            ).format(
                function=row["function"],
                mode=row["mode"],
                matrix=row["matrix"],
                count=int(row["count"]),
                max_difference=float(row["max_difference"]),
                max_pct=float(row["max_pct"]),
                mean_pct=float(row["mean_pct"]),
            )
        )

    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(out_csv)
    print(out_md)
    print("groups", len(summary_rows))


if __name__ == "__main__":
    main()
