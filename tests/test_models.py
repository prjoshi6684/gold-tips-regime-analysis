import numpy as np
import pandas as pd
import pytest
from src.data_pipeline import prepare_data
from src.technicals import compute_rsi, compute_technical_suite
from src.break_analysis import (run_subsample_ols, compute_chow_test,
    compute_rolling_correlation, run_monthly_chow_grid)
from src.valuation_model import estimate_level_model


def test_validation_and_missing_difference():
    raw = pd.DataFrame({"date": ["2022-01-01", "2022-01-02", "2022-01-03"],
                        "gold": [100, np.nan, 110], "tips": [1, 2, 3]})
    d = prepare_data(raw)
    assert len(d) == 3 and d.DLGOLD.isna().all()
    with pytest.raises(ValueError, match="Duplicate dates"):
        prepare_data(pd.concat([raw, raw.iloc[:1]]))
    raw.loc[0, "gold"] = 0
    with pytest.raises(ValueError, match="positive"):
        prepare_data(raw)


@pytest.mark.parametrize("values,expected", [(np.arange(20.), 100), (-np.arange(20.), 0), (np.ones(20), 50)])
def test_rsi_edges(values, expected):
    r = compute_rsi(pd.Series(values))
    assert r.iloc[:14].isna().all()
    assert r.iloc[14] == expected


def test_rsi_wilder_seed_and_gap():
    s = pd.Series([100, 102, 101, 104, 102, 105, np.nan, 110, 111])
    r = compute_rsi(s, period=3)
    assert r.iloc[3] == pytest.approx(100-100/(1+5))
    assert r.iloc[4] == pytest.approx(100-100/(1+(10/9)/(8/9)))
    assert r.iloc[6:].isna().all()


def test_break_detection_and_no_break_reference():
    rng = np.random.default_rng(7)
    index = pd.bdate_range("2021-01-01", "2024-12-31")
    x = rng.normal(size=len(index))
    noise = rng.normal(scale=.1, size=len(index))
    d = pd.DataFrame({"DTIPS": x, "DLGOLD": 1+2*x+noise}, index=index)
    m = run_subsample_ols(d)
    # Independently compute the unrestricted interaction-model RSS.
    post = (index >= "2023-01-01").astype(float)
    X = np.column_stack([np.ones(len(x)), x, post, x*post])
    rss_u = np.sum((d.DLGOLD-X@np.linalg.lstsq(X, d.DLGOLD, rcond=None)[0])**2)
    expected = ((m['full'].ssr-rss_u)/2)/(rss_u/(len(x)-4))
    assert compute_chow_test(m['full'], m['pre'], m['post'])[0] == pytest.approx(expected)
    d.loc[d.index >= "2023-01-01", "DLGOLD"] += 5*x[post == 1]
    m = run_subsample_ols(d)
    assert compute_chow_test(m['full'], m['pre'], m['post'])[1] < 1e-10


def test_rolling_keeps_missing_rows():
    d = pd.DataFrame({"DLGOLD": [1,2,np.nan,4,5,6], "DTIPS": [1,2,3,4,5,6]})
    r = compute_rolling_correlation(d, 3)
    assert len(r) == 6 and r.iloc[:5].isna().all()
    assert r.iloc[-1] == pytest.approx(1)


def test_valuation_identity_and_preserves_missing():
    index = pd.bdate_range("2022-01-01", periods=500)
    tips = np.linspace(-1, 2, 500)
    raw = pd.DataFrame({"date": index, "gold": np.exp(7-.2*tips), "tips": tips})
    raw.loc[490, "gold"] = np.nan
    d = prepare_data(raw)
    m, v = estimate_level_model(d)
    assert m.params['x'] == pytest.approx(-.2)
    assert len(v) == len(d) and pd.notna(v.GOLD_FITTED.iloc[490])
    assert v.DISLOCATION_PCT_EXACT.dropna().abs().max() < 1e-9


def test_technical_warmup():
    d = pd.DataFrame({"gold": np.arange(1., 601)})
    t = compute_technical_suite(d)
    assert t.MA200.first_valid_index() == 199
    assert t.MA200_DEV_Z.first_valid_index() == 450
    assert t.RSI14_Z.isna().all()  # Constant RSI has zero variance.


def test_grid_does_not_borrow_next_month():
    idx = pd.bdate_range("2007-01-01", "2008-06-30")
    idx = idx[idx.month != 2]
    rng = np.random.default_rng(5)
    d = pd.DataFrame({"DLGOLD": rng.normal(size=len(idx)), "DTIPS": rng.normal(size=len(idx))}, index=idx)
    g = run_monthly_chow_grid(d, "2008-01-01", "2008-03-01")
    assert len(g) == 3
    assert g.iloc[1].status == "no observations in month"
