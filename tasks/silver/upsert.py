from pathlib import Path

import pandas as pd


def upsert_parquet(path: Path, new_rows: pd.DataFrame, key_columns: list[str]) -> pd.DataFrame:

    if path.exists():
        existing = pd.read_parquet(path)
        combined = pd.concat([existing, new_rows], ignore_index=True)
    else:
        combined = new_rows

    combined = combined.drop_duplicates(subset=key_columns, keep="last")

    path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(path, index=False)

    return combined