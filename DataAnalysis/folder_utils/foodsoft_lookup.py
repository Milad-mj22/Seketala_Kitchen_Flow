import pandas as pd
from pathlib import Path

# Load once at import time
EXCEL_PATH = Path(r"cache\food_soft_food_code.xls")  # adjust path
_df = pd.read_excel(EXCEL_PATH, dtype=str)

# Optional: normalize
_df["kcod"] = _df["kcod"].str.strip()
_df["kname"] = _df["kname"].str.strip()

# Build dict for O(1) lookup
_KCOD_MAP = dict(zip(_df["kcod"], _df["kname"]))


def get_kname_by_kcod(kcod: str) -> str | None:
    if not kcod:
        return None
    return _KCOD_MAP.get(str(kcod).strip())



if __name__=='__main__':
    a = get_kname_by_kcod(111)
    print(a)