"""Unit tests for the toolkit. Run with:  python -m unittest -v   (or pytest)."""
import csv
import tempfile
import unittest
from pathlib import Path

from stats_toolkit import (mean, median, mode, variance, std_dev, quartiles, iqr_outliers, load_column, StatisticsAnalyzer)


class TestCentralTendency(unittest.TestCase):
    def test_mean_of_known_values(self):
        self.assertEqual(mean([2, 4, 6]), 4)

    def test_median_even_and_odd_lengths(self):
        self.assertEqual(median([1, 3, 5]), 3)
        self.assertEqual(median([1, 2, 3, 4]), 2.5)

    def test_mode_with_ties(self):
        self.assertEqual(mode([1, 1, 2, 2, 3]), [1, 2])

    def test_empty_input_raises(self):
        for function in (mean, median, mode):
            with self.subTest(function=function.__name__):
                with self.assertRaises(ValueError):
                    function([])


class TestSpread(unittest.TestCase):
    def test_sample_vs_population_variance(self):
        self.assertAlmostEqual(variance([2, 4, 6]), 4)
        self.assertAlmostEqual(variance([2, 4, 6], sample=False), 8 / 3)

    def test_std_dev_single_value(self):
        self.assertAlmostEqual(std_dev([5], sample=False), 0)
        with self.assertRaises(ValueError):
            std_dev([5], sample=True)


class TestOutliers(unittest.TestCase):
    def test_no_outliers_in_uniform_data(self):
        result = iqr_outliers([5, 5, 5, 5])
        self.assertEqual(result["outliers"], [])

    def test_detects_obvious_outlier(self):
        result = iqr_outliers([1, 2, 3, 4, 5, 100])
        self.assertEqual(result["outliers"], [100])
        self.assertAlmostEqual(result["iqr"], 3)


class TestLoading(unittest.TestCase):
    def test_invalid_and_missing_values_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.csv"

            with path.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["amount"])
                writer.writerow(["10"])
                writer.writerow([""])
                writer.writerow(["n/a"])
                writer.writerow(["20"])

            values, rejected = load_column(path, "amount")

            self.assertEqual(values, [10.0, 20.0])
            self.assertEqual(
                rejected,
                [(3, ""), (4, "n/a")],
            )


if __name__ == "__main__":
    unittest.main()
