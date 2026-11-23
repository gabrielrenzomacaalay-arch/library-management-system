"""PSLMS entry point:  python main.py"""
import os
import sys

from exceptions import DataCorruptionError
from storage import JsonRepository
from ui.cli import LibraryApp
from ui.prompts import confirm

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def load_library(repository):
    """Load data; offer a backup restore if the files are corrupted."""
    try:
        return repository.load_all()
    except DataCorruptionError as exc:
        print(f"[!] Could not load saved data: {exc}")
        if repository.list_backups() and confirm("Restore the latest backup?"):
            repository.restore_backup()
            return repository.load_all()
        print("Please repair or remove the files in the data/ folder, then restart.")
        return None


def main():
    repository = JsonRepository(DATA_DIR)
    library = load_library(repository)
    if library is None:
        return 1
    try:
        LibraryApp(library, repository).run()
    except (KeyboardInterrupt, EOFError):
        print("\nInterrupted: saving before exit...")
        repository.save_all(library)
    return 0


if __name__ == "__main__":
    sys.exit(main())
