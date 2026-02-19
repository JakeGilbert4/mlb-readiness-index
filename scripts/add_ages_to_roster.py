import requests
import pandas as pd
from datetime import datetime, date
import time

SEASON = 2025
TODAY = date(SEASON, 7, 1)  # mid-season age snapshot (good enough for MVP)

def get_birthdate(player_id: int):
    url = f"https://statsapi.mlb.com/api/v1/people/{player_id}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    people = r.json().get("people", [])
    if not people:
        return None
    return people[0].get("birthDate")  # "YYYY-MM-DD"

def calc_age(birthdate_str: str):
    if not birthdate_str:
        return None
    b = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
    age = TODAY.year - b.year - ((TODAY.month, TODAY.day) < (b.month, b.day))
    return float(age)

def main():
    roster = pd.read_csv("data/rays_system_roster.csv")
    roster["player_id"] = roster["player_id"].astype(int)

    # cache file so we don't hit API every time
    cache_path = "data/player_ages.csv"
    try:
        cache = pd.read_csv(cache_path)
        cache["player_id"] = cache["player_id"].astype(int)
    except:
        cache = pd.DataFrame(columns=["player_id", "birthDate", "age"])

    cache_ids = set(cache["player_id"].tolist())

    new_rows = []
    for pid in roster["player_id"].unique():
        if pid in cache_ids:
            continue
        try:
            bd = get_birthdate(int(pid))
            age = calc_age(bd)
            new_rows.append({"player_id": int(pid), "birthDate": bd, "age": age})
        except:
            new_rows.append({"player_id": int(pid), "birthDate": None, "age": None})
        time.sleep(0.05)

    if new_rows:
        cache = pd.concat([cache, pd.DataFrame(new_rows)], ignore_index=True)
        cache.to_csv(cache_path, index=False)

    roster = roster.merge(cache[["player_id", "age"]], on="player_id", how="left")
    roster.to_csv("data/rays_system_roster_with_age.csv", index=False)

    print("Wrote data/rays_system_roster_with_age.csv")
    print(roster[["name","level","player_id","age"]].head(10))

if __name__ == "__main__":
    main()
