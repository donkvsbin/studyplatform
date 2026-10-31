"""Create a consistent SQLite backup without copying a live database file."""

from datetime import datetime, timezone
from pathlib import Path
import sqlite3

root = Path(__file__).resolve().parents[1]
source = root / "backend/instance/learnhub.db"
if not source.is_file():
    raise SystemExit("Database not found. Run setup first.")
target = (
    source.parent
    / "backups"
    / ("learnhub-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f") + ".db")
)
target.parent.mkdir(parents=True, exist_ok=True)
with (
    sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as connection,
    sqlite3.connect(target) as backup,
):
    connection.backup(backup)
print(target)
