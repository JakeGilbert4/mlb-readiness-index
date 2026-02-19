import pandas as pd

FG_RAYS_DEPTH = "https://www.fangraphs.com/roster-resource/depth-charts/rays"

def main():
    tables = pd.read_html(FG_RAYS_DEPTH)

    target = None
    for t in tables:
        cols = [c.lower() for c in t.columns.astype(str)]
        if "org rank" in cols and "name" in cols:
            target = t.copy()
            break

    if target is None:
        raise RuntimeError("Could not find Top Prospects table.")

    target.columns = [str(c).strip().lower().replace(" ", "_") for c in target.columns]

    keep = [c for c in ["name", "level", "age", "org_rank"] if c in target.columns]
    df = target[keep].copy()

    df["name"] = df["name"].astype(str).str.strip()
    df.to_csv("data/rays_prospects_seed.csv", index=False)

    print("Wrote data/rays_prospects_seed.csv")
    print(df.head())

if __name__ == "__main__":
    main()


