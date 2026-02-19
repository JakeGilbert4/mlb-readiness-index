import numpy as np

def pct_rank(s):
    s = s.replace([np.inf, -np.inf], np.nan)
    return s.rank(pct=True)

def score_hitters(df):
    """
    MLB Readiness Score (Hitters):
    Emphasizes discipline + power + stable production, with a playing-time confidence factor.
    """
    df = df.copy()

    # Confidence based on PA (AB + BB approximation)
    if "PA" in df.columns:
        pa = df["PA"].fillna(0)
    else:
        pa = (df.get("atBats", 0) + df.get("baseOnBalls", 0)).fillna(0)

    df["conf"] = np.minimum(pa, 300) / 300  # ramps up until ~300 PA

    # Component scores (0..1)
    # Discipline: BB% high, K% low
    disc = 0.55 * pct_rank(df["BB_pct"]) + 0.45 * (1 - pct_rank(df["K_pct"]))

    # Power translation
    power = 0.75 * pct_rank(df["ISO"]) + 0.25 * pct_rank(df["HR_rate"])

    # Production floor proxy
    prod = 0.60 * pct_rank(df["SLG_calc"]) + 0.40 * pct_rank(df["AVG_calc"])

    # Optional: small bonus for being in AA/AAA (more “near MLB”)
    level_bonus = 0
    if "level" in df.columns:
        lvl = df["level"].astype(str)
        level_bonus = np.where(lvl == "AAA", 1.0,
                        np.where(lvl == "AA", 0.6,
                        np.where(lvl == "A+", 0.3,
                        np.where(lvl == "A", 0.1, 0.0))))
        level_bonus = level_bonus / 1.0  # normalize 0..1

    # Optional: age "prime window" bonus (not prospect upside)
    # best around 25-27, small penalty far away
    age_bonus = 0
    if "age" in df.columns:
        age = df["age"].astype(float)
        age_bonus = 1 - np.minimum(np.abs(age - 26) / 8, 1)  # 26 best, fades out by +/-8 yrs

    # Final MLB Readiness Score
    df["breakout_score"] = 100 * df["conf"] * (
        0.38 * disc +
        0.28 * power +
        0.24 * prod +
        0.05 * level_bonus +
        0.05 * age_bonus
    )

    return df.sort_values("breakout_score", ascending=False)

def score_pitchers(df):
    """
    MLB Readiness Score (Pitchers):
    Emphasizes K-BB control and HR suppression, heavily stabilized by innings pitched.
    """
    df = df.copy()

    # Confidence based on innings pitched
    ip = df.get("inningsPitched", 0)
    ip = ip.replace([np.inf, -np.inf], np.nan).fillna(0)

    df["ip_conf"] = np.minimum(ip, 80) / 80  # ramps up until ~80 IP

    # Use engineered metrics if present; otherwise fallback to basic
    # Expected columns from your add_pitcher_features: KBB_pct, HR9, BB_pct, K_pct etc.
    kbb = df.get("KBB_pct")
    hr9 = df.get("HR9")
    k_pct = df.get("K_pct")
    bb_pct = df.get("BB_pct")

    # If you don’t have KBB_pct/HR9, we can still score with basics
    if kbb is None or kbb.isna().all():
        # crude fallback: higher K, lower BB, lower HR
        k_score = pct_rank(k_pct) if k_pct is not None else 0
        bb_score = 1 - pct_rank(bb_pct) if bb_pct is not None else 0
        hr_score = 1 - pct_rank(df.get("homeRuns", 0))  # weak proxy
        core = 0.5 * k_score + 0.3 * bb_score + 0.2 * hr_score
    else:
        # main scoring: K-BB% high, HR9 low
        core = 0.70 * pct_rank(kbb) + 0.30 * (1 - pct_rank(hr9))

    df["breakout_score"] = 100 * df["ip_conf"] * core

    return df.sort_values("breakout_score", ascending=False)
