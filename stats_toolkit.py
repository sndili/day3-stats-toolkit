"""
Day 3 - Statistical Analysis Toolkit
Squad Python Specialization - Data Science, AI & Analytics

RULE: implement every calculation yourself with plain Python.
NumPy may be imported ONLY in compare_with_numpy(), to verify your results.
Do not use the statistics module.
"""
import csv
import math
from pathlib import Path
import subprocess
import sys
import re

DATA_PATH = Path("data") / "agent_deposits.csv"


def load_column(path: Path, column: str) -> tuple[list[float], list[tuple[int, str]]]:
    """Return (valid_values, rejected) where rejected holds (row_number, raw_value) pairs."""
    values = []
    rejected = []

    with open(path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if column not in reader.fieldnames:
            raise ValueError(f"Column not found: {column}")

        for row_number, row in enumerate(reader, start=2):
            raw_value = row[column].strip()

            try:
                value = float(raw_value.replace(",", ""))

                if not math.isfinite(value):
                    raise ValueError

                values.append(value)

            except ValueError:
                rejected.append((row_number, row[column]))

    return values, rejected


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot calculate mean of an empty list")

    return sum(values) / len(values)


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot calculate median of an empty list")

    sorted_values = sorted(values)
    middle = len(sorted_values) // 2

    if len(sorted_values) % 2 == 1:
        return sorted_values[middle]

    return (sorted_values[middle - 1] + sorted_values[middle]) / 2


def mode(values: list[float]) -> list[float]:
    """Return every value that occurs most often (a list, because there can be ties or none)."""
    if not values:
        raise ValueError("Cannot calculate mode of an empty list")

    counts = {}

    for value in values:
        counts[value] = counts.get(value, 0) + 1

    highest_count = max(counts.values())

    if highest_count == 1:
        return []

    return sorted(
        [value for value, count in counts.items() if count == highest_count]
    )


def variance(values: list[float], sample: bool = True) -> float:
    """Sample variance (n - 1) by default; population variance (n) when sample is False."""
    if not values:
        raise ValueError("Cannot calculate variance of an empty list")

    if sample and len(values) < 2:
        raise ValueError("Sample variance requires at least two values")

    average = mean(values)
    squared_differences = [(value - average) ** 2 for value in values]

    if sample:
        return sum(squared_differences) / (len(values) - 1)

    return sum(squared_differences) / len(values)


def std_dev(values: list[float], sample: bool = True) -> float:
    return math.sqrt(variance(values, sample))


def quartiles(values: list[float]) -> tuple[float, float, float]:
    """Return (Q1, Q2, Q3). Document which quartile method you chose."""
    if not values:
        raise ValueError("Cannot calculate quartiles of an empty list")

    sorted_values = sorted(values)
    middle = len(sorted_values) // 2

    q2 = median(sorted_values)

    if len(sorted_values) == 1:
        return sorted_values[0], q2, sorted_values[0]

    if len(sorted_values) % 2 == 0:
        lower_half = sorted_values[:middle]
        upper_half = sorted_values[middle:]
    else:
        lower_half = sorted_values[:middle]
        upper_half = sorted_values[middle + 1:]

    q1 = median(lower_half)
    q3 = median(upper_half)

    return q1, q2, q3


def iqr_outliers(values: list[float], k: float = 1.5) -> dict:
    """Return the IQR, the lower and upper fences, and the values outside them."""
    if not values:
        raise ValueError("Cannot detect outliers in an empty list")

    if k < 0:
        raise ValueError("The IQR multiplier cannot be negative")

    q1, _, q3 = quartiles(values)
    iqr = q3 - q1
    lower_fence = q1 - k * iqr
    upper_fence = q3 + k * iqr

    outliers = [
        value for value in values
        if value < lower_fence or value > upper_fence
    ]

    return {
        "iqr": iqr,
        "lower_fence": lower_fence,
        "upper_fence": upper_fence,
        "outliers": outliers,
    }


class StatisticsAnalyzer:
    """Wraps one numeric column and exposes every statistic above as a method."""

    def __init__(self, values: list[float], name: str = "values") -> None:
        self.values = list(values)
        self.sorted_values = sorted(self.values)
        self.name = name
        self.rows_read = len(self.values)
        self.rejected = []
        self.records = []

    @classmethod
    def from_csv(cls, path: Path, column: str) -> "StatisticsAnalyzer":
        values, rejected = load_column(path, column)
        analyzer = cls(values, column)

        rejected_rows = {row_number for row_number, _ in rejected}
        analyzer.rejected = [
            (
                row_number,
                raw_value,
                "Missing value" if not raw_value or not raw_value.strip()
                else "Invalid number",
            )
            for row_number, raw_value in rejected
        ]

        with open(path, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):
                if row_number in rejected_rows:
                    continue

                value = float(row[column].strip().replace(",", ""))

                analyzer.records.append({
                    "value": value,
                    "date": row["date"],
                    "agent_id": row["agent_id"],
                })

        analyzer.rows_read = len(analyzer.records) + len(analyzer.rejected)

        return analyzer

    def summary(self) -> dict:
        if not self.values:
            raise ValueError("Cannot summarize an empty list")
    
        q1, q2, q3 = quartiles(self.sorted_values)
        outlier_info = iqr_outliers(self.sorted_values)

        return {
        "count": len(self.values),
        "mean": mean(self.values),
        "median": q2,
        "mode": mode(self.values),
        "variance": variance(self.values),
        "std_dev": std_dev(self.values),
        "min": self.sorted_values[0],
        "max": self.sorted_values[-1],
        "q1": q1,
        "q3": q3,
        "iqr": outlier_info["iqr"],
        }

    def without_outliers(self) -> "StatisticsAnalyzer":
        outlier_info = iqr_outliers(self.values)
        outliers = outlier_info["outliers"]
                
        filtered_values = [
        value for value in self.values
        if value not in outliers
        ]
        
        analyzer = StatisticsAnalyzer(filtered_values, self.name)
        analyzer.rows_read = self.rows_read
        analyzer.rejected = self.rejected.copy()
        analyzer.records = [
        record for record in self.records
        if record["value"] not in outliers
        ]

        return analyzer

    def report(self) -> str:
        all_stats = self.summary()
        filtered_analyzer = self.without_outliers()
        filtered_stats = filtered_analyzer.summary()
        outlier_info = iqr_outliers(self.values)

        def format_number(value):
            return f"{value:.2f}"

        def format_mode(values):
            if not values:
                return "none"
            return ", ".join(format_number(value) for value in values)

        lines = [
            f"=== Statistics report: {self.name} ===",
            f"Rows read         : {self.rows_read}",
            f"Valid values      : {len(self.values)}",
            f"Rejected values   : {len(self.rejected)}",
        ]

        for row_number, raw_value, reason in self.rejected:
            lines.append(f"  row {row_number}: '{raw_value}' ({reason})")

        lines.extend([
            "",
            "                    all data      outliers removed",
            f"count               {all_stats['count']:<14}{filtered_stats['count']}",
            f"mean                {format_number(all_stats['mean']):<14}{format_number(filtered_stats['mean'])}",
            f"median              {format_number(all_stats['median']):<14}{format_number(filtered_stats['median'])}",
            f"mode                {format_mode(all_stats['mode']):<14}{format_mode(filtered_stats['mode'])}",
            f"variance (sample)   {format_number(all_stats['variance']):<14}{format_number(filtered_stats['variance'])}",
            f"std dev (sample)    {format_number(all_stats['std_dev']):<14}{format_number(filtered_stats['std_dev'])}",
            f"min / max           {format_number(all_stats['min'])} / {format_number(all_stats['max'])}    {format_number(filtered_stats['min'])} / {format_number(filtered_stats['max'])}",
            f"Q1 / Q3             {format_number(all_stats['q1'])} / {format_number(all_stats['q3'])}    {format_number(filtered_stats['q1'])} / {format_number(filtered_stats['q3'])}",
            f"IQR                 {format_number(all_stats['iqr']):<14}{format_number(filtered_stats['iqr'])}",
            "",
            f"Outlier fences      : lower {format_number(outlier_info['lower_fence'])}, upper {format_number(outlier_info['upper_fence'])}",
            "Outliers            :",
        ])

        outlier_values = outlier_info["outliers"]
        if outlier_values:
            for record in self.records:
                if record["value"] in outlier_values:
                    lines.append(
                        f"  {format_number(record['value'])} "
                        f"({record['date']}, {record['agent_id']})"
                    )
        else:
            lines.append("  none")

        verification = compare_with_numpy(self)

        lines.extend([
            "",
            "=== NumPy verification ===",
            f"mean      {'MATCH' if verification['mean'] else 'MISMATCH'}",
            f"median    {'MATCH' if verification['median'] else 'MISMATCH'}",
            f"variance  {'MATCH' if verification['variance'] else 'MISMATCH'}  (ddof=1)",
            f"std dev   {'MATCH' if verification['std_dev'] else 'MISMATCH'}",
            f"Q1 / Q3   {'MATCH' if verification['q1'] and verification['q3'] else 'MISMATCH'}  (method=median-of-halves)",
            "",
            "Risk team notes:",
            "Values outside the IQR fences may indicate unusual deposit activity or data-entry errors.",
            "Large deposits should be checked against transaction records before being treated as suspicious.",
            "Reviewing these cases alongside agent history can help distinguish legitimate peaks from activity requiring investigation.",
        ])

        return "\n".join(lines)


def compare_with_numpy(analyzer: StatisticsAnalyzer) -> dict[str, bool]:
    """Import numpy HERE, recompute each statistic and return {name: matches}."""
    import numpy as np

    values = analyzer.values
    sorted_values = sorted(values)

    numpy_mean = float(np.mean(values))
    numpy_median = float(np.median(values))
    numpy_variance = float(np.var(values, ddof=1))
    numpy_std_dev = float(np.std(values, ddof=1))

    middle = len(sorted_values) // 2

    if len(sorted_values) % 2 == 0:
        lower_half = sorted_values[:middle]
        upper_half = sorted_values[middle:]
    else:
        lower_half = sorted_values[:middle]
        upper_half = sorted_values[middle + 1:]

    numpy_q1 = float(np.median(lower_half))
    numpy_q3 = float(np.median(upper_half))

    q1, _, q3 = quartiles(values)

    def matches(ours, theirs):
        return math.isclose(
            ours, theirs, rel_tol=1e-9, abs_tol=1e-9
        )

    return {
        "mean": matches(mean(values), numpy_mean),
        "median": matches(median(values), numpy_median),
        "variance": matches(variance(values), numpy_variance),
        "std_dev": matches(std_dev(values), numpy_std_dev),
        "q1": matches(q1, numpy_q1),
        "q3": matches(q3, numpy_q3),
    }


if __name__ == "__main__":
    analyzer = StatisticsAnalyzer.from_csv(
        DATA_PATH, "daily_deposits_kes"
    )

    report_text = analyzer.report()

    test_result = subprocess.run(
        [sys.executable, "-m", "unittest", "-v"],
        capture_output=True,
        text=True,
    )

    test_output = test_result.stderr + test_result.stdout
    match = re.search(
        r"Ran (\d+) tests? in ([\d.]+)s",
        test_output,
    )

    if match:
        test_section = (
            "=== Unit tests ===\n"
            f"Ran {match.group(1)} tests in {match.group(2)}s\n"
            + ("OK" if test_result.returncode == 0 else "FAILED")
        )
    else:
        test_section = (
            "=== Unit tests ===\n"
            "Test results could not be determined.\n"
            + test_output
        )

    report_text += "\n\n" + test_section

    output_path = Path("output") / "stats_report.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_text + "\n", encoding="utf-8")

    print(report_text)
    print(f"\nReport saved to: {output_path}")

    if test_result.returncode != 0:
        sys.exit(test_result.returncode)