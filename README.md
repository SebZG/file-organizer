# File Organizer

Safely organize a messy folder into category-based subfolders. The organizer never deletes files, avoids overwriting duplicates, records each move in a CSV log, and can undo a completed organization.

## Requirements

- Python 3.8 or newer
- No third-party packages

The script uses only Python's standard library.

## Usage

Run the commands from this project directory:

```bash
python3 organizer.py /path/to/folder --dry-run
```

The dry run previews the planned moves without changing anything. After reviewing the preview, organize the folder:

```bash
python3 organizer.py /path/to/folder
```

For example, to organize a Downloads folder:

```bash
python3 organizer.py ~/Downloads
```

## Example

```text
$ python3 organizer.py ~/Downloads --dry-run
[preview] invoice.pdf  ->  closet/Documents/invoice.pdf
[preview] budget.xlsx  ->  closet/Spreadsheets/budget.xlsx
[preview] photo.jpg  ->  closet/Images/photo.jpg
[preview] notes.txt  ->  closet/Documents/notes (1).txt

Preview only, nothing was moved. Would sort 4 item(s): 2 Documents, 1 Images, 1 Spreadsheets
```

## Moving subfolders

By default, only files directly inside the target folder are moved. To also move subfolders, use `--move-folders`:

```bash
python3 organizer.py ~/Downloads --move-folders
```

With this option:

- ordinary subfolders are moved to `closet/Folders`
- folders whose names contain `temp` are moved to `closet/_Review`

Subfolder contents move with the folder. Files inside subfolders are not sorted individually; only the top level of the target folder is organized.

## Categories

Files are placed in a `closet` folder according to their extension:

| Category | Extensions |
| --- | --- |
| `Documents` | `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`, `.md` |
| `Spreadsheets` | `.xls`, `.xlsx`, `.csv`, `.tsv`, `.ods` |
| `Presentations` | `.ppt`, `.pptx`, `.key`, `.odp` |
| `Images` | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp`, `.heic`, `.tiff` |
| `Videos` | `.mp4`, `.mov`, `.avi`, `.mkv`, `.wmv` |
| `Audio` | `.mp3`, `.wav`, `.m4a`, `.flac`, `.aac` |
| `Archives` | `.zip`, `.rar`, `.7z`, `.tar`, `.gz` |
| `Code` | `.py`, `.js`, `.html`, `.css`, `.json`, `.ipynb` |
| `Other` | Files with extensions not listed above |

The organizer skips hidden files and folders, the `closet` folder it creates, and files whose names start with `organizer_log_`. This prevents previous organizer logs from being sorted into `Spreadsheets`.

## Logs and undo

Successful moves are recorded in a timestamped log file by default. The filename format is:

```text
organizer_log_YYYYMMDD_HHMMSS.csv
```

For example:

```text
organizer_log_20261003_153000.csv
```

The log is saved in the directory you run the command from, not inside the folder being organized.

Use `--log` to choose another log path:

```bash
python3 organizer.py ~/Downloads --log downloads_log.csv
```

Only logs with the default `organizer_log_` prefix are skipped automatically. If you choose a custom log name with `--log`, save it outside the folder you are organizing.

To reverse moves recorded in a log:

```bash
python3 organizer.py --undo organizer_log_20261003_153000.csv
```

Each run creates its own log. To reverse several runs, undo them in order from newest to oldest.

The undo operation restores items only when the moved item still exists and its original location is available.

## Duplicate filenames

If a destination already contains a file with the same name, the organizer does not overwrite it. Instead, it creates a name such as:

```text
report (1).pdf
```

## Command-line options

```text
python3 organizer.py [folder] [--dry-run] [--move-folders] [--log LOG]
python3 organizer.py --undo LOG
```

- `folder`: folder to organize
- `-n`, `--dry-run`: preview moves without changing files
- `--move-folders`: also organize subfolders
- `-l`, `--log LOG`: choose the move-log file; otherwise a timestamped `organizer_log_...csv` file is created
- `--undo LOG`: restore moves from a log file