"""Historical benchmark; no claim that fitted values are intrinsic fair value."""
import numpy as np
from .break_analysis import fit_ols


def estimate_level_model(df, train_end_date="2023-01-01"):
    train = df.loc[df.index < train_end_date]
    model = fit_ols(train.LOG_GOLD, train.tips)
    out = df.copy()
    out["GOLD_FITTED_LOG"] = model.params["const"] + model.params["x"] * out.tips
    out["GOLD_FITTED"] = np.exp(out.GOLD_FITTED_LOG)
    out["DISLOCATION"] = out.LOG_GOLD - out.GOLD_FITTED_LOG
    out["DISLOCATION_PCT_APPROX"] = 100 * out.DISLOCATION
    out["DISLOCATION_PCT_EXACT"] = 100 * np.expm1(out.DISLOCATION)
    return model, out
