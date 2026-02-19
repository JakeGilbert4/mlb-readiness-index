import pandas as pd
import numpy as np


def add_hitter_features(df):
    df = df.copy()

    numeric_cols = [
        "atBats", "hits", "baseOnBalls", "strikeOuts",
        "doubles", "triples", "homeRuns"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Plate appearances (approx)
    df["PA"] = df["atBats"] + df["baseOnBalls"]
    df["PA"] = df["PA"].replace(0, np.nan)

    # Rates
    df["BB_pct"] = df["baseOnBalls"] / df["PA"]
    df["K_pct"] = df["strikeOuts"] / df["PA"]
    df["HR_rate"] = df["homeRuns"] / df["PA"]

    # AVG / SLG / ISO
    ab = df["atBats"].replace(0, np.nan)
    df["AVG_calc"] = df["hits"] / ab

    df["TB"] = (
        df["hits"]
        + df["doubles"]
        + 2 * df["triples"]
        + 3 * df["homeRuns"]
    )

    df["SLG_calc"] = df["TB"] / ab
    df["ISO"] = df["SLG_calc"] - df["AVG_calc"]

    return df


def add_pitcher_features(df):
    df = df.copy()

    numeric_cols = [
        "inningsPitched", "strikeOuts", "baseOnBalls", "homeRuns"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    ip = df["inningsPitched"].replace(0, np.nan)

    # K-BB per inning (simple dominance metric)
    df["KBB_pct"] = (df["strikeOuts"] - df["baseOnBalls"]) / ip

    # HR per 9
    df["HR9"] = (df["homeRuns"] * 9) / ip

    return df