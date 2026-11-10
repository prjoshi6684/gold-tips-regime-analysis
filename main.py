"""Run with: python main.py --help"""
import argparse
import hashlib
import json
import logging
import platform
from pathlib import Path
from importlib.metadata import version
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from src.data_pipeline import load_and_prepare_data
from src.break_analysis import (run_subsample_ols, compute_chow_test,
    robust_break_test, run_monthly_chow_grid, compute_rolling_correlation,
    stationarity_table, cointegration_diagnostic)
from src.valuation_model import estimate_level_model
from src.technicals import compute_technical_suite

ROOT = Path(__file__).resolve().parent


def save_chart(path, title, series, ylabel):
    fig, ax = plt.subplots(figsize=(11, 5))
    for name, s in series.items():
        ax.plot(s.index, s, label=name, linewidth=1)
    ax.axvline(pd.Timestamp("2023-01-01"), color="gray", linestyle="--", label="January 2023")
    ax.set(title=title + " | SYNTHETIC DATA", ylabel=ylabel, xlabel="Date")
    ax.legend()
    ax.grid(alpha=.2)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def execute(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(out/"gold_run_log.txt", mode="w", encoding="utf-8"), logging.StreamHandler()], force=True)
    logging.info("Starting synthetic-data demonstration")
    df = load_and_prepare_data(args.input)
    logging.info("Loaded %d rows; %s to %s; missing gold=%d tips=%d", len(df),
        df.index[0].date(), df.index[-1].date(), df.gold.isna().sum(), df.tips.isna().sum())
    models = run_subsample_ols(df)
    rows = []
    for name, model in models.items():
        robust = model.get_robustcov_results(cov_type="HAC", maxlags=5)
        for i, term in enumerate(model.params.index):
            ci = robust.conf_int()[i]
            rows.append(dict(sample=name, term="DTIPS" if term == "x" else term,
                n=int(model.nobs), coefficient=float(model.params.iloc[i]),
                hac_se=float(robust.bse[i]), hac_t=float(robust.tvalues[i]),
                hac_p=float(robust.pvalues[i]), ci_low=float(ci[0]), ci_high=float(ci[1]), r_squared=model.rsquared))
    pd.DataFrame(rows).to_csv(out/"ols_comparison.csv", index=False)
    F, p = compute_chow_test(models["full"], models["pre"], models["post"])
    W, wp = robust_break_test(df, "2023-01-01")
    pd.DataFrame([dict(test="Classical Chow F", statistic=F, p_value=p),
                  dict(test="HAC joint-break Wald chi-square", statistic=W, p_value=wp)]).to_csv(out/"break_tests.csv", index=False)
    grid = run_monthly_chow_grid(df)
    grid.to_csv(out/"monthly_chow_grid.csv", index=False)
    corr = compute_rolling_correlation(df)
    adf = stationarity_table(df)
    adf.to_csv(out/"stationarity_adf.csv", index=False)
    cg = cointegration_diagnostic(df)
    pd.DataFrame([cg]).to_csv(out/"pre2023_cointegration.csv", index=False)
    model, valued = estimate_level_model(df)
    (out/"level_model.txt").write_text(model.summary().as_text(), encoding="utf-8")
    result = compute_technical_suite(valued)
    result["ROLL_CORR_252"] = corr
    result.to_csv(out/"all_series.csv", index_label="date")
    save_chart(out/"gold_benchmark.png", "Gold and pre-2023 historical benchmark",
               {"Gold": result.gold, "Benchmark": result.GOLD_FITTED}, "Synthetic USD per ounce")
    save_chart(out/"rolling_correlation.png", "252-observation return/yield-change correlation",
               {"Correlation": corr}, "Correlation")
    g = grid.dropna(subset=["f_stat"]).set_index("break_date")
    g.index = pd.to_datetime(g.index)
    save_chart(out/"chow_grid.png", "Exploratory monthly Chow grid", {"Chow F": g.f_stat}, "F statistic")
    save_chart(out/"dislocation.png", "Historical benchmark gap",
               {"Exact gap (%)": result.DISLOCATION_PCT_EXACT}, "Percent")
    save_chart(out/"technicals.png", "Technical stretch components",
               {"MA deviation z": result.MA200_DEV_Z, "RSI z": result.RSI14_Z,
                "Composite": result.TECH_SCORE}, "Score (composite is not unit variance)")
    latest = result.iloc[-1]
    def fmt(v):
        return "unavailable" if pd.isna(v) else f"{v:+.4f}"
    best = grid.loc[grid.f_stat.idxmax()] if grid.f_stat.notna().any() else None
    adf_diff = adf[adf.series.isin(["DLGOLD", "DTIPS"])]
    adf_message = ("All reported differenced-series ADF tests reject the unit-root null at 5%."
        if adf_diff.p_value.notna().all() and (adf_diff.p_value < .05).all()
        else "Differenced-series stationarity is not uniformly supported; inspect the ADF table before inference.")
    note = f"""# Gold–TIPS analysis: synthetic-data demonstration

Sample: {df.index[0].date()}–{df.index[-1].date()}; {len(df):,} input rows.
Latest figures refer to {result.index[-1].date()}, not today's market.

## Structural stability
January 2023 classical Chow F={F:.6g}, p={p:.6g}: {'reject' if p < .05 else 'do not reject'} parameter stability at 5% under the classical assumptions.
HAC joint-break Wald chi-square={W:.6g}, p={wp:.6g}: {'reject' if wp < .05 else 'do not reject'} stability using lag-5 HAC inference.
DTIPS slopes: pre={models['pre'].params['x']:.6g}; post={models['post'].params['x']:.6g}.
This split tests intercept and slope jointly. Rejection does not identify the exact date or establish causality.
Largest exploratory monthly F: {best['candidate_month'] if best is not None else 'unavailable'}.
Grid p-values are pointwise and unadjusted for searching many dates; the maximum is not a valid standalone significance test.
Latest 252-row correlation: {fmt(corr.iloc[-1])}. Pre/post means: {fmt(corr.loc[corr.index < '2023-01-01'].mean())} / {fmt(corr.loc[corr.index >= '2023-01-01'].mean())}.
Post-split windows initially overlap the earlier regime. Correlation is descriptive evidence, not a break test.

## Stationarity and historical benchmark
{adf_message}
Differences target short-run changes rather than a potentially spurious levels association. ADF uses an intercept and AIC lag selection; missing rows are omitted for this diagnostic, which assumes equally spaced retained observations.
Pre-2023 Engle–Granger diagnostic p={cg['p_value']:.6g}; interpretation requires compatible integration orders and is sensitive to specification and gaps. Inspect level ADF evidence too.
The level regression is a descriptive historical benchmark, not an established equilibrium or intrinsic fair value.
Latest benchmark price: {fmt(latest.GOLD_FITTED)}; log gap: {fmt(latest.DISLOCATION)};
approximate gap: {fmt(latest.DISLOCATION_PCT_APPROX)}%; exact gap: {fmt(latest.DISLOCATION_PCT_EXACT)}%.
Exponentiating fitted log price gives a geometric benchmark, not a bias-corrected conditional arithmetic mean.

## Technical indicators
MA200={fmt(latest.MA200)}; MA deviation={fmt(latest.MA200_DEV)}%; RSI14={fmt(latest.RSI14)}.
MA deviation z={fmt(latest.MA200_DEV_Z)}; RSI z={fmt(latest.RSI14_Z)}; composite={fmt(latest.TECH_SCORE)}.
Positive scores indicate readings above their trailing averages; negative scores indicate below-average readings.
The composite averages two z-scores and is not itself standardized to unit variance. No universal trading threshold or reversal forecast is assumed.

## Limitations and reproducibility
All input data are user-supplied synthetic observations. These findings validate a demonstration workflow and provide no empirical evidence about actual gold markets.
The supplied workbook does not establish its generator, seed or data-generating process; retain the original generator separately if available.
Missing values and extreme observations are preserved; invalid values and duplicate dates fail validation. Windows count supplied observations, not calendar days; no holiday calendar or daily rows are fabricated.
OLS standard errors in the comparison table use HAC with five lags. Classical Chow inference additionally assumes homoskedastic independent errors; the robust test is provided as a sensitivity check.
See methodology.md, environment.json, input_sha256.txt and manifest.csv.
"""
    (out/"report.md").write_text(note, encoding="utf-8")
    digest = hashlib.sha256(args.input.read_bytes()).hexdigest()
    (out/"input_sha256.txt").write_text(digest+"\n", encoding="utf-8")
    env = {p: version(p) for p in ["pandas", "numpy", "scipy", "statsmodels", "matplotlib", "openpyxl"]}
    env["python"] = platform.python_version()
    (out/"environment.json").write_text(json.dumps(env, indent=2), encoding="utf-8")
    logging.info("Analysis completed; report: %s", out/"report.md")
    pd.DataFrame([dict(file=p.name, bytes=p.stat().st_size) for p in sorted(out.iterdir())
                  if p.is_file() and p.name != "manifest.csv"]).to_csv(out/"manifest.csv", index=False)
    print(note)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gold–TIPS synthetic-data analysis")
    parser.add_argument("--input", type=Path, default=ROOT/"data/Gold_Model_initial_data_set.xlsx")
    parser.add_argument("--output", type=Path, default=ROOT/"results")
    args = parser.parse_args()
    try:
        execute(args)
    except Exception:
        logging.exception("Analysis failed")
        raise SystemExit(1)
