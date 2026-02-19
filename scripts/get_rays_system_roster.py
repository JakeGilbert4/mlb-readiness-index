print("RUNNING ROSTER SCRIPT")

import requests
import pandas as pd
import time
from urllib.parse import quote

SEASON = 2025

AFFILIATES = [
    {"name": "Durham Bulls", "level": "AAA"},
    {"name": "Montgomery Biscuits", "level": "AA"},
    {"name": "Bowling Green Hot Rods", "level": "A+"},
    {"name": "Charleston RiverDogs", "level": "A"},
]

def find_team_id(team_name: str):
    url = f"https://statsapi.mlb.com/api/v1/teams?sportId=11&name={quote(team_name)}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    teams = r.json().get("teams", [])
    if not teams:
        return None
    return teams[0].get("id")

def get_team_roster(team_id: int):
    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster"
    params = {"season": str(SEASON), "rosterType": "active"}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("roster", [])

def main():
    rows = []

    for a in AFFILIATES:
        team_name = a["name"]
        level = a["level"]

        team_id = find_team_id(team_name)
        print(f"{team_name} team_id={team_id}")

        if not team_id:
            continue

        roster = get_team_roster(team_id)
        print(f"{team_name} roster_count={len(roster)}")

        for p in roster:
            person = p.get("person", {})
            pos = p.get("position", {})
            rows.append({
                "affiliate": team_name,
                "level": level,
                "player_id": person.get("id"),
                "name": person.get("fullName"),
                "pos": pos.get("abbreviation"),
            })

        time.sleep(0.2)

    df = pd.DataFrame(rows).dropna(subset=["player_id"])
    df["player_id"] = df["player_id"].astype(int)

    df.to_csv("data/rays_system_roster.csv", index=False)
    print(f"Wrote data/rays_system_roster.csv rows={len(df)}")

if __name__ == "__main__":
    main()
