"""Wilder RSI with SMA initialization; gaps restart the warm-up."""
import numpy as np
import pandas as pd


def compute_rsi(series, period=14):
    if not isinstance(period, int) or period < 1:
        raise ValueError("RSI period must be a positive integer")
    result = pd.Series(np.nan, index=series.index, dtype=float)
    prev = None
    gains, losses = [], []
    avg_g = avg_l = None
    for i, price in enumerate(series):
        if pd.isna(price):
            prev = None
            gains, losses = [], []
            avg_g = avg_l = None
            continue
        if prev is not None:
            change = price-prev
            g, loss = max(change, 0), max(-change, 0)
            if avg_g is None:
                gains.append(g)
                losses.append(loss)
                if len(gains) == period:
                    avg_g, avg_l = np.mean(gains), np.mean(losses)
            else:
                avg_g = ((period-1)*avg_g+g)/period
                avg_l = ((period-1)*avg_l+loss)/period
            if avg_g is not None:
                result.iloc[i] = (50. if avg_g == avg_l == 0 else
                                  100. if avg_l == 0 else 100.-100./(1.+avg_g/avg_l))
        prev = price
    return result


def rolling_zscore(series, window=252):
    rolling = series.rolling(window, min_periods=window)
    return (series-rolling.mean())/rolling.std(ddof=1).replace(0, np.nan)


def compute_technical_suite(df):
    out = df.copy()
    out["MA200"] = out.gold.rolling(200, min_periods=200).mean()
    out["MA200_DEV"] = 100*(out.gold/out.MA200-1)
    out["RSI14"] = compute_rsi(out.gold)
    out["MA200_DEV_Z"] = rolling_zscore(out.MA200_DEV)
    out["RSI14_Z"] = rolling_zscore(out.RSI14)
    out["TECH_SCORE"] = (out.MA200_DEV_Z+out.RSI14_Z)/2
    return out
