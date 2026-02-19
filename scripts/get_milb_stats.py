import time
import requests
import pandas as pd
import statsapi

SEASON = 2025  # change later if you want a different season

def find_player_id(name: str):
    results = statsapi.lookup_player(name)
    if not results:
        return None
    return results[0].get("id")

def milb_season_stats(player_id: int, group: str):
    url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats"
    params = {
        "stats": "season",
        "group": group,              # "hitting" or "pitching"
        "season": str(SEASON),
        "gameType": "R",
        "leagueListId": "milb_all",   # includes minor leagues
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def extract_splits(payload):
    stats = payload.get("stats", [])
    if not stats:
        return []
    return stats[0].get("splits", [])

def main():
    seed = pd.read_csv("data/rays_prospects_seed.csv")

    hitters_rows = []
    pitchers_rows = []

    for name in seed["name"].dropna().astype(str).tolist():
        pid = find_player_id(name)
        if not pid:
            print(f"[WARN] No id for: {name}")
            continue

        # Try both hitting and pitching
        for group in ["hitting", "pitching"]:
            try:
                payload = milb_season_stats(pid, group=group)
                splits = extract_splits(payload)
                if not splits:
                    continue

                # For MVP: take the first split (often totals)
                s = splits[0]
                stat = s.get("stat", {}) or {}

                out = {"name": name, "player_id": pid}
                for k, v in stat.items():
                    out[k] = v

                if group == "hitting":
                    hitters_rows.append(out)
                else:
                    pitchers_rows.append(out)

            except Exception as e:
                print(f"[WARN] {group} failed for {name}: {e}")

        time.sleep(0.15)

    pd.DataFrame(hitters_rows).to_csv("data/rays_hitters_raw.csv", index=False)
    pd.DataFrame(pitchers_rows).to_csv("data/rays_pitchers_raw.csv", index=False)

    print("Wrote data/rays_hitters_raw.csv")
    print("Wrote data/rays_pitchers_raw.csv")

if __name__ == "__main__":
    main()
