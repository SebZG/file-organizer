"""Sort a messy folder into tidy categories, safely.

Nothing is ever deleted. Every move is logged, and can be undone.

Usage:
    python3 organizer.py ~/Downloads --dry-run     # preview only
    python3 organizer.py ~/Downloads               # sort the files
    python3 organizer.py ~/Downloads --move-folders
    python3 organizer.py --undo organizer_log_20261003_153000.csv
"""

import argparse
import csv
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

CATEGORIES = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".tsv", ".ods"},
    "Presentations": {".ppt", ".pptx", ".key", ".odp"},
    "Images": {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".svg",
        ".webp",
        ".heic",
        ".tiff",
    },
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".wmv"},
    "Audio": {".mp3", ".wav", ".m4a", ".flac", ".aac"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".html", ".css", ".json", ".ipynb"},
}
SORTED_DIR = "closet"  # everything is moved inside this folder
OTHER = "Other"  # files that match no category
FOLDERS = "Folders"  # sub-folders (only with --move-folders)
REVIEW = "_Review"  # folders named "temp": set aside for review, never deleted
LOG_PREFIX = "organizer_log_"  # log files start with this and are never sorted


def category_for(path):
    suffix = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if suffix in extensions:
            return category
    return OTHER


def unique_destination(destination, reserved):
    """If a file with that name already exists, add (1), (2)... instead of overwriting."""
    candidate, counter = destination, 1
    while candidate.exists() or candidate in reserved:
        candidate = destination.with_name(
            f"{destination.stem} ({counter}){destination.suffix}"
        )
        counter += 1
    return candidate


def is_skipped(item, sorted_root):
    """Our own folder, hidden files such as .DS_Store, and previous log files."""
    return (
        item == sorted_root
        or item.name.startswith(".")
        or item.name.startswith(LOG_PREFIX)
    )


def plan_moves(root, move_folders):
    """Work out where everything should go, without touching anything."""
    sorted_root = root / SORTED_DIR
    moves, reserved = [], set()

    for item in sorted(root.iterdir()):
        if is_skipped(item, sorted_root):
            continue
        if item.is_file():
            category = category_for(item)
        elif item.is_dir() and move_folders:
            category = REVIEW if "temp" in item.name.lower() else FOLDERS
        else:
            continue

        destination = unique_destination(sorted_root / category / item.name, reserved)
        reserved.add(destination)
        moves.append((item, destination, category))
    return moves


def write_log(records, log_path):
    with open(log_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Category", "Original path", "New path"])
        writer.writerows(records)


def organize(root, dry_run, move_folders, log_path):
    moves = plan_moves(root, move_folders)
    if not moves:
        print("Nothing to sort.")
        return

    records = []
    for source, destination, category in moves:
        if dry_run:
            print(f"[preview] {source.name}  ->  {destination.relative_to(root)}")
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        records.append(
            (
                datetime.now().isoformat(timespec="seconds"),
                category,
                source,
                destination,
            )
        )

    counts = Counter(category for _, _, category in moves)
    summary = ", ".join(
        f"{count} {category}" for category, count in sorted(counts.items())
    )

    if dry_run:
        print(
            f"\nPreview only, nothing was moved. Would sort {len(moves)} item(s): {summary}"
        )
    else:
        write_log(records, log_path)
        print(f"Sorted {len(moves)} item(s): {summary}")
        print(
            f"Log saved to {log_path}  (undo with: python3 organizer.py --undo {log_path})"
        )


def undo(log_path):
    if not Path(log_path).exists():
        sys.exit(f"Log not found: {log_path}")

    with open(log_path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    restored = 0
    for row in reversed(rows):
        original, moved = Path(row["Original path"]), Path(row["New path"])
        if moved.exists() and not original.exists():
            shutil.move(str(moved), str(original))
            restored += 1
    print(f"Restored {restored} of {len(rows)} item(s).")


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("folder", nargs="?", help="the folder to sort")
    parser.add_argument(
        "-n", "--dry-run", action="store_true", help="preview without moving anything"
    )
    parser.add_argument(
        "--move-folders", action="store_true", help="also move sub-folders"
    )
    parser.add_argument(
        "-l",
        "--log",
        help=f"log file (default: {LOG_PREFIX}<date>_<time>.csv)",
    )
    parser.add_argument(
        "--undo", metavar="LOG", help="reverse the moves recorded in a log file"
    )
    args = parser.parse_args()

    if args.undo:
        undo(args.undo)
        return
    if not args.folder:
        parser.error("please give a folder to sort (or use --undo LOG)")

    root = Path(args.folder).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"Not a folder: {root}")

    log_path = args.log or f"{LOG_PREFIX}{datetime.now():%Y%m%d_%H%M%S}.csv"
    organize(root, args.dry_run, args.move_folders, log_path)


if __name__ == "__main__":
    main()
