import streamlit as st
import pandas as pd

from src.features import add_hitter_features, add_pitcher_features
from src.scoring import score_hitters, score_pitchers

st.set_page_config(layout="wide")

st.title("MLB Readiness Index")

st.markdown(
    """
    This model ranks upper-level minor league players
    based on performance translation and workload stabilization.
    """
)

player_type = st.radio("Select Player Type", ["Hitters", "Pitchers"])

# --------------------------
# HITTERS
# --------------------------

if player_type == "Hitters":

    df = pd.read_csv("data/rays_hitters_raw.csv")

    # Remove duplicate players (keep highest level)
    df = df.sort_values("level", ascending=False).drop_duplicates(subset=["name"])

    df = add_hitter_features(df)
    df = score_hitters(df)

    st.subheader("Filters")

    ab_min = st.slider("Min At-Bats", 0, 1000, 200)

    df = df[df["atBats"] >= ab_min]

    display_cols = [
        "name",
        "breakout_score",
        "level",
        "AVG_calc",
        "BB_pct",
        "ISO",
        "atBats",
        "homeRuns",
        "baseOnBalls",
        "strikeOuts"
    ]

    st.dataframe(
        df[display_cols].sort_values("breakout_score", ascending=False),
        width="stretch"
    )

# --------------------------
# PITCHERS
# --------------------------

else:

    df = pd.read_csv("data/rays_pitchers_raw.csv")

    # Remove duplicate players
    df = df.sort_values("level", ascending=False).drop_duplicates(subset=["name"])

    df = add_pitcher_features(df)
    df = score_pitchers(df)

    st.subheader("Filters")

    min_ip = st.slider("Min Innings Pitched", 0, 250, 40)

    df = df[df["inningsPitched"] >= min_ip]

    display_cols = [
        "name",
        "breakout_score",
        "level",
        "KBB_pct",
        "HR9",
        "inningsPitched",
        "strikeOuts",
        "baseOnBalls",
        "homeRuns"
    ]

    st.dataframe(
        df[display_cols].sort_values("breakout_score", ascending=False),
        width="stretch"
    )