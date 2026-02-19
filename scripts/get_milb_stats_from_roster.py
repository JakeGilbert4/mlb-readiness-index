import time
import requests
import pandas as pd

SEASON = 2025

HIT_KEYS = ["atBats","hits","doubles","triples","homeRuns","baseOnBalls","strikeOuts"]
PIT_KEYS = ["inningsPitched","strikeOuts","baseOnBalls","homeRuns"]

def milb_season_stats(player_id: int, group: str):
    url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats"
    params = {
        "stats": "season",
        "group": group,
        "season": str(SEASON),
        "gameType": "R",
        "leagueListId": "milb_all",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def get_splits(payload):
    stats = payload.get("stats", [])
    if not stats:
        return []
    return stats[0].get("splits", [])

def sum_splits(splits, keys):
    total = {k: 0.0 for k in keys}
    for s in splits:
        stat = s.get("stat", {}) or {}
        for k in keys:
            v = stat.get(k)
            if v is None:
                continue
            try:
                total[k] += float(v)
            except:
                pass
    return total

def main():
    roster = pd.read_csv("data/rays_system_roster.csv")

    hitters = []
    pitchers = []

    for _, r in roster.iterrows():
        pid = int(r["player_id"])

        base = {
            "name": r["name"],
            "player_id": pid,
            "affiliate": r["affiliate"],
            "level": r["level"],
            "pos": r.get("pos"),
        }

        # hitting
        try:
            payload = milb_season_stats(pid, "hitting")
            splits = get_splits(payload)
            if splits:
                totals = sum_splits(splits, HIT_KEYS)
                hitters.append({**base, **totals})
        except:
            pass

        # pitching
        try:
            payload = milb_season_stats(pid, "pitching")
            splits = get_splits(payload)
            if splits:
                totals = sum_splits(splits, PIT_KEYS)
                pitchers.append({**base, **totals})
        except:
            pass

        time.sleep(0.08)

    pd.DataFrame(hitters).to_csv("data/rays_hitters_raw.csv", index=False)
    pd.DataFrame(pitchers).to_csv("data/rays_pitchers_raw.csv", index=False)

    print(f"Wrote data/rays_hitters_raw.csv rows={len(hitters)}")
    print(f"Wrote data/rays_pitchers_raw.csv rows={len(pitchers)}")

if __name__ == "__main__":
    main()
