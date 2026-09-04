from pathlib import Path

import pandas as pd

GOLD_DIR = Path("storage/gold")


def read_gold_table(name: str) -> pd.DataFrame:
    path = GOLD_DIR / f"{name}.parquet"

    if not path.exists():
        return pd.DataFrame()

    return pd.read_parquet(path)