"""OLS, fixed-break tests, exploratory breakpoint grid and stationarity evidence."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import f
from statsmodels.tsa.stattools import adfuller, coint


def fit_ols(y, x):
    data = pd.concat([y.rename("y"), x.rename("x")], axis=1).dropna()
    X = sm.add_constant(data[["x"]], has_constant="add")
    if len(data) <= 2 or np.linalg.matrix_rank(X) < 2:
        raise ValueError("Regression needs more than two complete observations and a varying regressor")
    return sm.OLS(data.y, X).fit()


def run_subsample_ols(df, split_date="2023-01-01"):
    cut = pd.Timestamp(split_date)
    d = df[["DLGOLD", "DTIPS"]].dropna()
    return {name: fit_ols(s.DLGOLD, s.DTIPS) for name, s in
            [("full", d), ("pre", d.loc[d.index < cut]), ("post", d.loc[d.index >= cut])]}


def compute_chow_test(full, pre, post):
    k = len(full.params)
    if full.nobs != pre.nobs + post.nobs or full.df_resid <= k:
        raise ValueError("Chow models must partition the same pooled sample")
    rss = pre.ssr + post.ssr
    if rss <= 0:
        raise ValueError("Chow statistic undefined with zero unrestricted residual variance")
    stat = max(0.0, float(((full.ssr-rss)/k)/(rss/(full.nobs-2*k))))
    return stat, float(f.sf(stat, k, full.nobs-2*k))


def robust_break_test(df, split_date):
    d = df[["DLGOLD", "DTIPS"]].dropna()
    post = (d.index >= pd.Timestamp(split_date)).astype(float)
    X = pd.DataFrame({"const": 1., "x": d.DTIPS, "post": post,
                      "interaction": d.DTIPS * post}, index=d.index)
    if len(d) <= 4 or np.linalg.matrix_rank(X) < 4:
        raise ValueError("Insufficient full-rank data for robust break test")
    m = sm.OLS(d.DLGOLD, X).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
    w = m.wald_test(np.array([[0,0,1,0],[0,0,0,1]]), scalar=True)
    return float(w.statistic), float(w.pvalue)


def run_monthly_chow_grid(df, start="2008-01-01", end="2025-12-01", min_obs=30):
    records = []
    for month in pd.date_range(start, end, freq="MS"):
        dates = df.index[(df.index >= month) & (df.index < month + pd.offsets.MonthBegin(1))]
        row = {"candidate_month": month.strftime("%Y-%m"), "break_date": None,
               "f_stat": np.nan, "p_value": np.nan, "status": "no observations in month"}
        if len(dates):
            cut = dates[0]
            row["break_date"] = cut.strftime("%Y-%m-%d")
            complete = df[["DLGOLD", "DTIPS"]].dropna()
            if min((complete.index < cut).sum(), (complete.index >= cut).sum()) < min_obs:
                row["status"] = "insufficient subsample observations"
            else:
                try:
                    m = run_subsample_ols(df, cut)
                    row["f_stat"], row["p_value"] = compute_chow_test(m["full"], m["pre"], m["post"])
                    row["status"] = "ok"
                except ValueError as exc:
                    row["status"] = str(exc)
        records.append(row)
    return pd.DataFrame(records)


def compute_rolling_correlation(df, window=252):
    # Keep original rows: a missing pair invalidates a full-window estimate.
    return df.DLGOLD.rolling(window, min_periods=window).corr(df.DTIPS)


def stationarity_table(df):
    rows = []
    for sample, d in [("full", df), ("pre", df.loc[df.index < "2023-01-01"]),
                      ("post", df.loc[df.index >= "2023-01-01"])]:
        for col in ("LOG_GOLD", "tips", "DLGOLD", "DTIPS"):
            s = d[col].dropna()
            row = {"sample": sample, "series": col, "n": len(s)}
            try:
                result = adfuller(s, regression="c", autolag="AIC")
                row.update(adf_stat=result[0], p_value=result[1], lags=result[2], status="ok")
            except ValueError as exc:
                row.update(adf_stat=np.nan, p_value=np.nan, lags=np.nan, status=str(exc))
            rows.append(row)
    return pd.DataFrame(rows)


def cointegration_diagnostic(df):
    d = df.loc[df.index < "2023-01-01", ["LOG_GOLD", "tips"]].dropna()
    stat, p, _ = coint(d.LOG_GOLD, d.tips, trend="c", autolag="aic")
    return {"statistic": float(stat), "p_value": float(p)}
