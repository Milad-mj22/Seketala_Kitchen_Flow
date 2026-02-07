import pandas as pd
from pathlib import Path

# Load once at import time

def normalize_fa(text: str) -> str:
    return (
        text.replace("ي", "ی")
            .replace("ك", "ک")
            .replace("\u200c", "")
            .strip()
    )


EXCEL_PATH = Path(r"cache\sepidar_food_code.xlsx")  # adjust path

_df = pd.read_excel(
    EXCEL_PATH,

    dtype=str
)

# -----------------------------
# Normalize columns (Persian-safe)
# -----------------------------
_df["كد"] = _df["كد"].astype(str).str.strip()
_df["عنوان"] = _df["عنوان"].apply(normalize_fa)

# -----------------------------
# Build NAME -> CODE map
# -----------------------------
_NAME_TO_CODE = dict(zip(_df["عنوان"], _df["كد"]))


def get_code_by_name(name: str) -> str | None:
    if not name:
        return None
    return _NAME_TO_CODE.get(name.strip())


# -----------------------------
# Test
# -----------------------------
if __name__ == "__main__":
    a = get_code_by_name("ماشروم برگر")
    print(a)