# Gold–TIPS Regime Analysis

A quantitative macro Python toolkit for analyzing structural breaks, model-implied valuation gaps, and technical stretch in the gold–TIPS real yield relationship using synthetic data.

**Synthetic-data demonstration. No results establish actual market behavior, intrinsic fair value, or a trading recommendation.**

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

This is a Python implementation