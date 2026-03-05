from __future__ import annotations

import csv
import re
from pathlib import Path
from statistics import mean, pstdev


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def _normalize_metric(metric: str) -> str:
    # Collapse case-index suffixes (for example _c1, _c2, _case_3) into one metric group.
    metric = re.sub(r"_case_\d+(?=(_|$))", "", metric)
    metric = re.sub(r"_c\d+(?=(_|$))", "", metric)
    return metric


def _write_main_parity_report(out_dir: Path) -> None:
    source_csvs = sorted(out_dir.glob("*_parity_report.csv"))
    source_csvs = [p for p in source_csvs if p.name != "main_parity_report.csv"]
    if not source_csvs:
        return

    grouped: dict[tuple[str, str], dict[str, list[float] | list[bool] | set[str]]] = {}
    for csv_path in source_csvs:
        with csv_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                function = row["function"]
                metric = _normalize_metric(row["metric"])
                key = (function, metric)
                bucket = grouped.setdefault(
                    key,
                    {
                        "max_abs": [],
                        "max_rel": [],
                        "atol": [],
                        "rtol": [],
                        "pass": [],
                        "reports": set(),
                    },
                )
                bucket["max_abs"].append(float(row["max_abs"]))
                bucket["max_rel"].append(float(row["max_rel"]))
                bucket["atol"].append(float(row["atol"]))
                bucket["rtol"].append(float(row["rtol"]))
                bucket["pass"].append(_parse_bool(row["pass"]))
                bucket["reports"].add(csv_path.stem)

    headers = [
        "function",
        "metric",
        "n_rows",
        "n_reports",
        "mean_max_abs",
        "std_dv_max_abs",
        "mean_max_rel",
        "std_dv_max_rel",
        "mean_abs_over_atol",
        "std_dv_abs_over_atol",
        "mean_rel_over_rtol",
        "std_dv_rel_over_rtol",
        "pass_rate",
        "severity_flag",
    ]

    summary_rows: list[dict[str, str | int | float]] = []
    for function, metric in sorted(grouped.keys()):
        bucket = grouped[(function, metric)]
        max_abs = bucket["max_abs"]
        max_rel = bucket["max_rel"]
        atol_vals = bucket["atol"]
        rtol_vals = bucket["rtol"]
        pass_vals = bucket["pass"]
        reports = bucket["reports"]
        n_rows = len(max_abs)

        abs_over_atol = [a / max(t, 1e-30) for a, t in zip(max_abs, atol_vals, strict=True)]
        rel_over_rtol = [r / max(t, 1e-30) for r, t in zip(max_rel, rtol_vals, strict=True)]

        mean_abs = mean(max_abs)
        std_abs = pstdev(max_abs) if n_rows > 1 else 0.0
        mean_rel = mean(max_rel)
        std_rel = pstdev(max_rel) if n_rows > 1 else 0.0
        mean_abs_norm = mean(abs_over_atol)
        std_abs_norm = pstdev(abs_over_atol) if n_rows > 1 else 0.0
        mean_rel_norm = mean(rel_over_rtol)
        std_rel_norm = pstdev(rel_over_rtol) if n_rows > 1 else 0.0
        pass_rate = mean(1.0 if p else 0.0 for p in pass_vals)

        severity_flag = "normal"
        # Absolute errors can look large on huge-magnitude matrices while relative fit is still good.
        if pass_rate == 1.0 and mean_abs_norm > 1e3 and mean_rel_norm < 0.25:
            severity_flag = "scale-driven-high-abs"
        elif pass_rate < 1.0:
            severity_flag = "parity-failure"

        summary_rows.append(
            {
                "function": function,
                "metric": metric,
                "n_rows": n_rows,
                "n_reports": len(reports),
                "mean_max_abs": mean_abs,
                "std_dv_max_abs": std_abs,
                "mean_max_rel": mean_rel,
                "std_dv_max_rel": std_rel,
                "mean_abs_over_atol": mean_abs_norm,
                "std_dv_abs_over_atol": std_abs_norm,
                "mean_rel_over_rtol": mean_rel_norm,
                "std_dv_rel_over_rtol": std_rel_norm,
                "pass_rate": pass_rate,
                "severity_flag": severity_flag,
            }
        )

    csv_path = out_dir / "main_parity_report.csv"
    md_path = out_dir / "main_parity_report.md"

    def write_csv(path: Path) -> None:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in summary_rows:
                writer.writerow(row)

    md_lines = [
        "# main_parity_report",
        "",
        "| function | metric | n_rows | n_reports | mean_max_abs | std_dv_max_abs | "
        "mean_max_rel | std_dv_max_rel | mean_abs_over_atol | std_dv_abs_over_atol | "
        "mean_rel_over_rtol | std_dv_rel_over_rtol | pass_rate | severity_flag |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in summary_rows:
        md_lines.append(
            (
                "| {function} | {metric} | {n_rows} | {n_reports} | {mean_max_abs:.3e} | "
                "{std_dv_max_abs:.3e} | {mean_max_rel:.3e} | {std_dv_max_rel:.3e} | "
                "{mean_abs_over_atol:.3e} | {std_dv_abs_over_atol:.3e} | "
                "{mean_rel_over_rtol:.3e} | {std_dv_rel_over_rtol:.3e} | "
                "{pass_rate:.3f} | {severity_flag} |"
            ).format(
                function=row["function"],
                metric=row["metric"],
                n_rows=int(row["n_rows"]),
                n_reports=int(row["n_reports"]),
                mean_max_abs=float(row["mean_max_abs"]),
                std_dv_max_abs=float(row["std_dv_max_abs"]),
                mean_max_rel=float(row["mean_max_rel"]),
                std_dv_max_rel=float(row["std_dv_max_rel"]),
                mean_abs_over_atol=float(row["mean_abs_over_atol"]),
                std_dv_abs_over_atol=float(row["std_dv_abs_over_atol"]),
                mean_rel_over_rtol=float(row["mean_rel_over_rtol"]),
                std_dv_rel_over_rtol=float(row["std_dv_rel_over_rtol"]),
                pass_rate=float(row["pass_rate"]),
                severity_flag=row["severity_flag"],
            )
        )
    md_content = "\n".join(md_lines) + "\n"
    try:
        write_csv(csv_path)
        md_path.write_text(md_content, encoding="utf-8")
    except PermissionError:
        # On Windows, an open CSV in another process can lock writes.
        write_csv(out_dir / "main_parity_report.pending.csv")
        (out_dir / "main_parity_report.pending.md").write_text(md_content, encoding="utf-8")


def write_parity_report(report_name: str, rows: list[dict[str, str | float | int | bool]]) -> None:
    if not rows:
        return

    out_dir = Path(__file__).resolve().parents[2] / "parity_reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    headers = ["function", "case", "metric", "max_abs", "max_rel", "atol", "rtol", "pass"]
    csv_path = out_dir / f"{report_name}.csv"
    md_path = out_dir / f"{report_name}.md"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    md_lines = [
        f"# {report_name}",
        "",
        "| function | case | metric | max_abs | max_rel | atol | rtol | pass |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        pass_result = "yes" if bool(row["pass"]) else "no"
        md_lines.append(
            (
                "| {function} | {case} | {metric} | {max_abs:.3e} | {max_rel:.3e} | "
                "{atol:.1e} | {rtol:.1e} | {pass_result} |"
            ).format(
                function=row["function"],
                case=row["case"],
                metric=row["metric"],
                max_abs=float(row["max_abs"]),
                max_rel=float(row["max_rel"]),
                atol=float(row["atol"]),
                rtol=float(row["rtol"]),
                pass_result=pass_result,
            )
        )
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    # Keep an always-updated global parity summary across all report CSVs.
    _write_main_parity_report(out_dir)
