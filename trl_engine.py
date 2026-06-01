"""TRL Assessment Engine for RLV Maintenance Technologies."""
import json, os
import pandas as pd
import numpy as np

def load_trl_data():
    path = os.path.join(os.path.dirname(__file__), "data", "trl_assessment.json")
    with open(path, "r") as f:
        db = json.load(f)
    df = pd.DataFrame(db["assessments"])
    return df, db["trl_scale"], db["technologies"]

def compute_maturity_score(df):
    """Average TRL per vehicle as percentage (TRL 9 = 100%)."""
    scores = df.groupby("vehicle")["trl"].mean()
    return (scores / 9 * 100).round(1)

def compute_gap_matrix(df):
    """Pivot: vehicles (rows) x technologies (columns) with TRL values."""
    return df.pivot_table(index="vehicle", columns="technology",
                          values="trl", aggfunc="first")

def identify_gaps(df, threshold=5):
    """Flag all assessments below threshold as gaps."""
    gaps = df[df["trl"] < threshold].copy()
    gaps["severity"] = 9 - gaps["trl"]
    gaps["category"] = gaps["trl"].apply(lambda t:
        "Critical Gap" if t <= 3 else
        "Development Needed" if t <= 5 else
        "Validation Required")
    return gaps.sort_values("severity", ascending=False)

def compute_tech_landscape(df):
    """Per-technology statistics across all vehicles."""
    stats = df.groupby("technology")["trl"].agg(
        ["min", "max", "mean"]).round(1)
    stats["spread"] = stats["max"] - stats["min"]
    stats["leader"] = df.loc[df.groupby("technology")["trl"].idxmax()
                             ].set_index("technology")["vehicle"]
    return stats.sort_values("mean", ascending=False)

if __name__ == "__main__":
    df, scale, techs = load_trl_data()
    scores = compute_maturity_score(df)
    gaps = identify_gaps(df)
    print(f"Total assessments: {len(df)}")
    print(f"\nMaturity scores:\n{scores}")
    print(f"\nGaps (TRL < 5): {len(gaps)}")
    print(f"Critical gaps (TRL <= 3): {len(gaps[gaps['trl'] <= 3])}")