# 🗂️ Bulk File Organizer

Scans a messy folder and automatically sorts files into categorized subdirectories.

```
Downloads/
├── invoice_2024.pdf   ──▶ Documents/invoice_2024.pdf
├── photo.jpg          ──▶ Images/photo.jpg
├── backup.zip         ──▶ Archives/backup.zip
├── app.py             ──▶ Code/app.py
└── ...
```

## Quick Start

```bash
# Organize your Downloads folder
python organize.py --path "C:\Users\swarnabh\Downloads"

# Dry-run first (preview without moving)
python organize.py --path "C:\Users\swarnabh\Downloads" --dry-run

# With custom config
python organize.py --path "C:\Users\swarnabh\Downloads" --config config.json --verbose
```

## CLI Arguments

| Argument | Description | Default |
|---|---|---|
| `--path` | Target directory to organize | `~/Downloads` |
| `--dry-run` | Preview mode (no actual moves) | `False` |
| `--config` | Path to custom config.json | `config.json` |
| `--conflict` | How to handle name collisions: `skip`, `overwrite`, `rename` | `skip` |
| `--verbose` | Enable detailed logging | `False` |
| `--exclude-files` | Filenames to skip (e.g. `README.md`) | `[]` |
| `--exclude-dirs` | Directory names to skip during scan | `['__pycache__', '.git', '.venv', 'venv', 'node_modules']` |

## File Type Mappings (Default)

| Category | Extensions |
|---|---|
| **Documents** | .pdf, .doc, .docx, .txt, .odt, .ppt, .pptx, .xls, .xlsx, .rtf |
| **Images** | .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .ico, .tiff |
| **Videos** | .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm |
| **Audio** | .mp3, .wav, .flac, .aac, .ogg, .wma, .m4a |
| **Archives** | .zip, .rar, .7z, .tar, .gz, .bz2 |
| **Executables** | .exe, .msi, .dmg, .app, .deb, .rpm |
| **Code** | .py, .js, .ts, .java, .cpp, .c, .h, .go, .rs, .rb, .php, .sh |
| **Spreadsheets** | .csv, .xlsm, .ods |
| **Presentations** | .pps, .ppsx, .odp |
| **Other** | Everything else |

## Project Structure

```
bulk-file-organizer/
├── organize.py          # CLI entry point
├── config.json          # File type → category mapping
├── requirements.txt
├── README.md
├── organizer/           # Core library
│   ├── __init__.py
│   ├── config_manager.py    # Reads & validates config
│   ├── file_classifier.py   # Extension → category mapping
│   ├── file_mover.py        # Move operations + conflict handling
│   └── logger_config.py     # Logging setup
└── tests/               # Unit tests
    ├── __init__.py
    ├── test_classifier.py
    ├── test_mover.py
    └── test_config.py
```

## Design Principles

- **Single Responsibility** — Each class has one job (config, classify, move, log)
- **Open/Closed** — Add new categories via `config.json`, not code changes
- **Dependency Inversion** — Protocols abstract concrete implementations
- **Configuration Over Code** — File-type mappings are data, not hardcoded
- **SOLID** — All five principles followed throughout

## Custom Config

Create your own `config.json`:

```json
{
  "categories": {
    "Documents": [".pdf", ".doc", ".docx", ".txt"],
    "Images": [".jpg", ".png", ".webp"],
    "Code": [".py", ".js", ".ts"],
    "Music": [".mp3", ".wav", ".flac"]
  },
  "default_category": "Other",
  "conflict_strategy": "skip"
}
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Notes

- Files already in subdirectories are **not** processed (only root-level files in the target)
- Hidden files (starting with `.`) are skipped by default
- Log file written to `organize.log` in the target directory
