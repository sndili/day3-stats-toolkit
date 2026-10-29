# Wakala Plus : Statistical Analysis Toolkit

## Overview

This project implements a descriptive statistics toolkit in Python for analysing daily M-Pesa agent deposits. Wakala Plus runs a network of M-Pesa agents, which needs to understand deposit patterns across Nairobi, Thika, Machakos and Nakuru. The toolkit calculates descriptive statistics from first principles using plain Python. 

> NumPy is used only to verify the results, not to perform the main calculations.

## Project Structure

```text
day3-stats-toolkit/
├── stats_toolkit.py
├── test_stats_toolkit.py
├── data/
│   └── agent_deposits.csv
├── output/
│   └── stats_report.txt
├── requirements.txt
└── README.md
```

## Features

- Loads a selected numeric column from a CSV file.
- Separates valid numeric values from missing or invalid entries.
- Calculates mean, median, mode, variance and standard deviation.
- Supports both sample and population variance and standard deviation.
- Calculates quartiles, the interquartile range (IQR) and outlier fences.
- Identifies outliers using the IQR method.
- Compares statistics calculated with plain Python against NumPy.
- Analyses the dataset with all valid values and again with outliers removed.
- Generates a text report containing statistics, rejected values, outlier details, NumPy verification results and risk-team notes.
- Includes unit tests for the main statistical calculations and data-loading behaviour.

## Approach

### 1. Loading and cleaning the data

The `load_column()` function reads the requested column using Python's built-in `csv` module. Valid values are converted to floats, while rejected values are returned with their CSV row numbers and original raw values.

The toolkit distinguishes missing values from invalid numbers when generating the report. It does not reject a row because another column contains invalid data if the selected deposit value is valid.

### 2. Calculating descriptive statistics

The following functions implement the calculations without using Python's `statistics` module or NumPy:

- `mean()`: calculates the sum of the values divided by their count.
- `median()`: sorts the values and finds the middle value, or averages the two middle values when the count is even.
- `mode()`: counts occurrences and returns every value tied for the highest frequency.
- `variance()`: calculates the average squared deviation from the mean, using either the sample or population denominator.
- `std_dev()`: calculates the square root of the variance.

If every value occurs only once, `mode()` returns an empty list to indicate that there is no mode. Functions that require values raise a `ValueError` for empty input. Sample variance also requires at least two observations.

### 3. Variance and standard deviation

The toolkit supports two approaches:

- **Sample variance:** divides the sum of squared deviations by `n - 1`.
- **Population variance:** divides the sum of squared deviations by `n`.

Sample variance is the default used in the report because the observed daily deposits are treated as a sample for understanding wider deposit patterns. Population variance can be requested by passing `sample=False`.

### 4. Quartiles and outlier detection

The `quartiles()` function uses the **median-of-halves method**. The sorted data is divided into lower and upper halves and the median of each half gives Q1 and Q3. When there is an odd number of observations, the overall median is excluded from both halves.

The interquartile range is calculated as:

`IQR = Q3 - Q1`

The outlier fences use the conventional 1.5 IQR rule:

- Lower fence: `Q1 - 1.5 × IQR`
- Upper fence: `Q3 + 1.5 × IQR`

Values below the lower fence or above the upper fence are flagged as outliers. These are statistical flags for further review, not as proof of errors or suspicious activity.

### 5. Analysis and reporting

The `StatisticsAnalyzer` class brings the analysis together.

- `from_csv()` loads the dataset and prepares the analysis.
- `summary()` returns the calculated statistics in a dictionary.
- `without_outliers()` returns a new analyzer containing the values that remain after the identified outliers are excluded.
- `report()` produces the formatted analysis report.

The report compares the original valid dataset with the dataset after outlier removal. It also lists rejected values with their row numbers and reasons, identifies outliers with their dates and agent IDs and includes exactly three sentences of guidance for the risk team.

### 6. NumPy verification

The `compare_with_numpy()` function is the only place where NumPy is imported. It independently checks the mean, median, sample variance, sample standard deviation and quartiles against the plain-Python results.

Comparisons use a numerical tolerance to account for small floating-point differences. The NumPy quartiles use the same median-of-halves method as the toolkit, so the results are compared consistently. The variance and standard deviation checks use `ddof=1` to match sample calculations.

## Assumptions

The input file is `data/agent_deposits.csv` and the column analysed is `daily_deposits_kes`.

The dataset contains 40 data rows. The current analysis produces 35 valid deposit values and 5 rejected values.

The following assumptions apply:

1. Each CSV data row represents one agent's daily deposit observation.
2. CSV row numbering in the report includes the header row, so the first data row is row 2.
3. Empty values and values that cannot be converted to finite numbers are rejected. Rejected values remain visible in the report for review.
4. The loader removes commas before attempting numeric conversion, allowing comma-separated thousands in numeric strings. Other malformed values are rejected if conversion fails.
5. Only the selected deposit column determines whether a row's deposit value is accepted. Invalid values in unrelated columns do not automatically invalidate a deposit.
6. Sample variance and sample standard deviation are used for the main report, while population calculations remain available through the functions.
7. The median-of-halves quartile method is used consistently for both the toolkit and NumPy verification.
8. The 1.5 IQR rule identifies potential outliers. A flagged value may represent a legitimate deposit, an unusual event or a data-entry problem and should be investigated before drawing conclusions.
9. Removing outliers is used to compare how extreme observations affect the summary statistics. The original observations are retained in the source CSV.
10. NumPy is our verification dependency only. The main statistical calculations use plain Python and the standard library.

## Requirements

- Python 3.10 or later.
- NumPy - for verification.
- Python's standard library modules, including `csv`, `math`, `pathlib`, `unittest` and the modules used to run the test suite.

Install the external dependency from the project root:

```bash
python -m pip install -r requirements.txt
```

The `requirements.txt` file should contain:

```text
numpy
```

## How to Run

Run these commands from the project root directory, where `stats_toolkit.py` is located.

### Generate the report

```bash
python stats_toolkit.py
```

The toolkit prints the report in the terminal and saves it to:

`output/stats_report.txt`

The output directory is created automatically if it does not exist.

### Run the unit tests

```bash
python -m unittest -v
```

The tests cover known mean values, odd and even medians, tied modes, empty inputs, sample and population variance, standard deviation for a single value, outlier detection and missing or invalid CSV values.

The current test suite contains nine tests, all of which passed in the latest test run as highlighted below:

```text
test_empty_input_raises (test_stats_toolkit.TestCentralTendency.test_empty_input_raises) ... ok
test_mean_of_known_values (test_stats_toolkit.TestCentralTendency.test_mean_of_known_values) ... ok
test_median_even_and_odd_lengths (test_stats_toolkit.TestCentralTendency.test_median_even_and_odd_lengths) ... ok
test_mode_with_ties (test_stats_toolkit.TestCentralTendency.test_mode_with_ties) ... ok
test_invalid_and_missing_values_are_rejected (test_stats_toolkit.TestLoading.test_invalid_and_missing_values_are_rejected) ... ok
test_detects_obvious_outlier (test_stats_toolkit.TestOutliers.test_detects_obvious_outlier) ... ok
test_no_outliers_in_uniform_data (test_stats_toolkit.TestOutliers.test_no_outliers_in_uniform_data) ... ok
test_sample_vs_population_variance (test_stats_toolkit.TestSpread.test_sample_vs_population_variance) ... ok
test_std_dev_single_value (test_stats_toolkit.TestSpread.test_std_dev_single_value) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.015s

OK
```


## Results

For the supplied dataset, the toolkit reads 40 rows, accepts 35 deposit values and rejects 5 values. The report identifies four IQR outliers and shows how removing them changes the summary statistics.

All five NumPy verification checks matched the plain-Python results in the latest report.

The detailed numerical results, rejected rows, outlier dates and agent IDs, verification statuses and risk-team notes are available in `output/stats_report.txt`.

## Conclusion

This project demonstrates how to implement descriptive statistics using core Python, validate calculations against NumPy, handle imperfect CSV data and communicate the effect of outliers through a reproducible report. It also uses unit tests to check important calculations and edge cases independently of the main dataset.
