from pathlib import Path
import os

RATE_LIMIT_TOTAL = int(os.getenv("APP_GENERATION_LIMIT", "5"))
RATE_LIMIT_WINDOW_SECONDS = int(
    os.getenv("APP_GENERATION_LIMIT_WINDOW_SECONDS", str(24 * 60 * 60))
)
RATE_LIMIT_DB_PATH = Path(
    os.getenv(
        "APP_RATE_LIMIT_DB_PATH",
        str(Path(__file__).resolve().parent.parent / "data" / "rate_limits.sqlite3"),
    )
)