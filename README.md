# Gold–TIPS Regime Analysis

A quantitative macro Python toolkit for analyzing structural breaks, model-implied valuation gaps, and technical stretch in the gold–TIPS real yield relationship using synthetic data.

**Synthetic-data demonstration. No results establish actual market behavior, intrinsic fair value, or a trading recommendation.**

This is a Python implementation.

## Run on Windows

Install Python 3.10 or newer. Open a terminal inside this project folder:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
.venv\Scripts\python.exe -m pytest -q
```

No terminal activation or execution-policy change is needed. If `python` is unavailable, use the full path to your installed Python interpreter for the first command.

Default input: `data/Gold_Model_initial_data_set.xlsx`, sheet `aligned_clean_model_ready`, columns `date`, `gold`, `tips`. I generated the synthetic dataset using Gemini. The workbook is included in this repository, but the data-generation code and random seed are not available.

```powershell
.venv\Scripts\python.exe main.py --input "D:\path\input.xlsx" --output results
```

The default input/output paths are relative to the script, so the program also runs from another working directory. Custom relative paths are relative to the terminal's current directory. Use a dedicated output folder. Generated files are overwritten on reruns.

## Outputs

`results/` contains comparable OLS tables with HAC inference; classical and robust break tests; all 216 monthly candidate records; stationarity and cointegration diagnostics; level-model summary; full transformed series; five charts; a conditional written report; input hash; dependency versions; run log; and a file manifest. Read `results/report.md` after running for calculated results. No numerical findings are hard-coded in this README.

Read `methodology.md` for formulas, window rules, missing-data treatment and limitations. `src/` separates ingestion, break analysis, valuation and indicators; `main.py` orchestrates exports. Tests check numerical identities, a known break, RSI boundaries and initialization, missing values, duplicate rejection, rolling-window behavior, and candidate-month selection.

## Development status

The initial analysis pipeline is implemented and runs end to end. Further development will focus on model robustness, scenario analysis, and usability.

## Roadmap

The following extensions are planned and are not yet implemented.

### Next development priorities

- [ ] **Configurable analysis:** Allow users to change the breakpoint date, rolling windows, and RSI period through command-line options.

- [ ] **Scenario analysis:** Estimate how the historical gold benchmark changes under hypothetical TIPS yield movements of ±25, ±50, and ±100 basis points. These are model-conditional scenarios, not causal forecasts.

- [ ] **Sensitivity analysis:** Compare results across alternative sample periods, breakpoint dates, and rolling-window settings.

- [ ] **Residual diagnostics:** Add checks for serial correlation, heteroskedasticity, and model specification.

- [ ] **Automated testing:** Configure GitHub Actions to run the test suite on repository updates.

### Further research and usability extensions

- [ ] **Out-of-sample evaluation:** Compare models using chronological training and evaluation periods, including simple forecasting baselines.

- [ ] **Uncertainty estimates:** Display confidence and prediction intervals alongside benchmark estimates, subject to model assumptions.

- [ ] **Data-quality reporting:** Flag missing observations, date gaps, repeated prices, and unusual changes for review.

- [ ] **Reproducible simulation:** Add a documented synthetic-data generator with a fixed random seed and known data-generating assumptions.

- [ ] **Real-data support:** Add documented public-data ingestion, including source attribution, units, and alignment rules.

- [ ] **Research dashboard:** Provide interactive charts, scenario controls, and downloadable results.
Real-data support:Add documented public-data ingestion, including source attribution, units, and alignment rules.
Research dashboard: Provide interactive charts, scenario controls, and downloadable results.

Extensions will be implemented incrementally, with tests and documentation updated alongside each feature. New models will be evaluated on their assumptions and performance rather than added solely to increase complexity.
