"""Sync root leads.csv to barrie-lead-tracker and add browser-confirmed tags."""
import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).parent / "leads.csv"
TRACKER_CSV = Path(__file__).parent / "barrie-lead-tracker" / "leads.csv"

# Append browser proof to notes if not already present
BROWSER_TAGS = [
    ("Express Country Style", "BROWSER-CONFIRMED Canada411 2026-06-08: 705-791-6925=Starbucks. Correct 705-730-0944."),
    ("Thornton Cafe", "BROWSER-CONFIRMED Canada411 2026-06-08: 705-718-7816=Starbucks Innisfil. Correct 705-458-1500+FB."),
    ("The Installer", "BROWSER-CONFIRMED Canada411 2026-06-08: 705-466-2244=Hamilton Bros. Correct 705-796-3499."),
    ("Fils Rest", "BROWSER-CONFIRMED Canada411 2026-06-08: 705-726-7818=Fils Rest Duckworth St. CORRECT SMS."),
    ("Carmen's Maid", "BROWSER-CONFIRMED Canada411 2026-06-08: 705-734-1118=Carmens Maid Service. CORRECT SMS."),
]


def main() -> None:
    with ROOT.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))

    for row in rows[1:]:
        if not row or len(row) < 12:
            continue
        name = row[0]
        for key, tag in BROWSER_TAGS:
            if key in name and "BROWSER-CONFIRMED" not in row[11]:
                row[11] = f"{row[11]} {tag}".strip() if row[11] else tag
                print(f"Tagged: {name[:50]}")
                break

    with ROOT.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)

    TRACKER_CSV.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT, TRACKER_CSV)
    print(f"Synced -> {TRACKER_CSV}")


if __name__ == "__main__":
    main()
