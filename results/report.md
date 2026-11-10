# Gold–TIPS analysis: synthetic-data demonstration

Sample: 2007-01-03–2025-12-31; 4,956 input rows.
Latest figures refer to 2025-12-31, not today's market.

## Structural stability
January 2023 classical Chow F=7.41512, p=0.000608793: reject parameter stability at 5% under the classical assumptions.
HAC joint-break Wald chi-square=14.2567, p=0.000802022: reject stability using lag-5 HAC inference.
DTIPS slopes: pre=-3.01642; post=0.0451117.
This split tests intercept and slope jointly. Rejection does not identify the exact date or establish causality.
Largest exploratory monthly F: 2023-05.
Grid p-values are pointwise and unadjusted for searching many dates; the maximum is not a valid standalone significance test.
Latest 252-row correlation: +0.0496. Pre/post means: -0.1342 / -0.0295.
Post-split windows initially overlap the earlier regime. Correlation is descriptive evidence, not a break test.

## Stationarity and historical benchmark
All reported differenced-series ADF tests reject the unit-root null at 5%.
Differences target short-run changes rather than a potentially spurious levels association. ADF uses an intercept and AIC lag selection; missing rows are omitted for this diagnostic, which assumes equally spaced retained observations.
Pre-2023 Engle–Granger diagnostic p=0.989531; interpretation requires compatible integration orders and is sensitive to specification and gaps. Inspect level ADF evidence too.
The level regression is a descriptive historical benchmark, not an established equilibrium or intrinsic fair value.
Latest benchmark price: +922.7732; log gap: +1.4711;
approximate gap: +147.1131%; exact gap: +335.4158%.
Exponentiating fitted log price gives a geometric benchmark, not a bias-corrected conditional arithmetic mean.

## Technical indicators
MA200=+3682.1791; MA deviation=+9.1175%; RSI14=+76.3926.
MA deviation z=+0.8195; RSI z=+1.4815; composite=+1.1505.
Positive scores indicate readings above their trailing averages; negative scores indicate below-average readings.
The composite averages two z-scores and is not itself standardized to unit variance. No universal trading threshold or reversal forecast is assumed.

## Limitations and reproducibility
All input data are user-supplied synthetic observations. These findings validate a demonstration workflow and provide no empirical evidence about actual gold markets.
The supplied workbook does not establish its generator, seed or data-generating process; retain the original generator separately if available.
Missing values and extreme observations are preserved; invalid values and duplicate dates fail validation. Windows count supplied observations, not calendar days; no holiday calendar or daily rows are fabricated.
OLS standard errors in the comparison table use HAC with five lags. Classical Chow inference additionally assumes homoskedastic independent errors; the robust test is provided as a sensitivity check.
See methodology.md, environment.json, input_sha256.txt and manifest.csv.
