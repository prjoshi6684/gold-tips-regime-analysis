# Methods and conventions

This project uses synthetic data, not historical market observations. The original workbook is retained unchanged. A supplied dataset is reproducible as an input artifact; recreating its simulation additionally requires its original generator and seed.

Inputs: gold is a positive synthetic USD-per-ounce price; tips is a synthetic 10-year real yield in percentage points (2.3 means 2.3%, not 0.023). Confirm these units with the dataset generator. Missing values are retained, infinite/non-numeric data and duplicate dates rejected, and dates sorted chronologically. Dates refer to supplied observation rows; no exchange holiday calendar is assumed.

LOG_GOLD = ln(gold); DLGOLD = 100 × ΔLOG_GOLD; DTIPS = Δtips. Differences are calculated on the original sorted index. A missing level also invalidates the adjacent difference. Regression samples exclude incomplete pairs only after transformations. DTIPS coefficients measure percent log-return per one percentage-point yield change.

Full/pre/post OLS regress DLGOLD on an intercept and DTIPS, with pre < 2023-01-01 and post >= 2023-01-01. The intercept and slope can both change. Comparison inference uses Newey–West/HAC covariance with five lags. Classical Chow F = ((RSS pooled − RSS split)/2)/(RSS split/(N−4)); its p-value uses the F survival function. A separate HAC Wald test of the post dummy and interaction supplies robust sensitivity evidence.

The monthly grid records every candidate month, including unavailable/invalid candidates. Each breakpoint is the first original observation in that month. At least 30 complete observations per side are required. Grid p-values are pointwise, not corrected for multiple searches. This is exploratory profiling, not a calibrated supremum test.

ADF tests use an intercept and AIC lag selection for levels and differences, separately for each regime and pooled data. Their null is a unit root; non-rejection is not proof of nonstationarity. The pre-2023 Engle–Granger diagnostic assumes the integration-order conditions hold. Structural changes and missing-row removal affect interpretation. The historical level benchmark remains descriptive irrespective of a single diagnostic p-value.

Pre-2023 ln(gold) = a + b × tips gives GOLD_FITTED_LOG. GOLD_FITTED = exp(GOLD_FITTED_LOG). DISLOCATION = LOG_GOLD − GOLD_FITTED_LOG; approximate percent gap = 100 × DISLOCATION; exact percent gap = 100 × expm1(DISLOCATION). The exponential is a geometric price benchmark, without a lognormal mean correction. It is calculated wherever tips exists, including rows with missing gold; dislocation then stays missing.

MA200 is a trailing 200-row arithmetic mean requiring 200 nonmissing prices. MA200_DEV = 100 × (gold/MA200−1). Wilder RSI14 initializes average gains/losses using the first 14 changes, then updates each as (13 × previous average + new change)/14. A missing price restarts initialization. RSI is 100 with gains and no losses, 0 with losses and no gains, and 50 for a flat window.

Each trailing 252-row z-score includes the current observation, uses sample standard deviation (ddof=1), and requires a complete window. Zero standard deviation gives missing. TECH_SCORE is the arithmetic mean of MA200_DEV_Z and RSI14_Z, requiring both. It is not itself a standard normal or unit-variance statistic. No reversal prediction follows automatically.

The 252-row correlation requires 252 complete paired returns/yield changes on the original row index. Windows containing missing pairs stay missing. The report explicitly uses the final input date; it does not silently substitute an older complete date for current metrics.
