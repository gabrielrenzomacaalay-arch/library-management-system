"""JsonRepository: crash-safe JSON persistence for the whole Library.

* Atomic writes: data goes to a temp file, is fsync'd, then os.replace()d
  over the real file, so a power cut leaves either the old or the new file,
  never a half-written one.
* Backups: before each save, the existing files are copied into a
  timestamped folder under data/backups/ (newest MAX_BACKUPS are kept).
"""
import json
import os
import shutil
import tempfile
from datetime import date, datetime

from exceptions import DataCorruptionError, PSLMSError
from models import (Library, LoanRecord, LoanStatus, item_from_dict, member_from_dict)

FILES = ("books.json", "members.json", "loans.json")
MAX_BACKUPS = 20


class JsonRepository:
    def __init__(self, data_dir):
        self._data_dir = data_dir
        self._backup_dir = os.path.join(data_dir, "backups")

    # ---- saving -----------------------------------------------------
    def save_all(self, library):
        os.makedirs(self._data_dir, exist_ok=True)
        self.create_backup()
        self._atomic_write("books.json", [i.to_dict() for i in library.items()])
        self._atomic_write("members.json", [m.to_dict() for m in library.members()])
        self._atomic_write("loans.json", [l.to_dict() for l in library.loans()])

    def _atomic_write(self, filename, records):
        target = os.path.join(self._data_dir, filename)
        payload = {"version": 1, "records": records}
        fd, tmp_path = tempfile.mkstemp(dir=self._data_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                json.dump(payload, tmp, indent=2, ensure_ascii=False)
                tmp.flush()
                os.fsync(tmp.fileno())
            os.replace(tmp_path, target)
        except BaseException:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    # ---- backups ----------------------------------------------------
    def create_backup(self):
        """Copy existing data files to a new timestamped folder.

        Returns the backup folder name, or None if there was nothing to back up.
        """
        existing = [f for f in FILES if os.path.exists(os.path.join(self._data_dir, f))]
        if not existing:
            return None
        name = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        folder = os.path.join(self._backup_dir, name)
        os.makedirs(folder)
        for filename in existing:
            shutil.copy2(os.path.join(self._data_dir, filename), folder)
        self._prune_backups()
        return name

    def list_backups(self):
        if not os.path.isdir(self._backup_dir):
            return []
        return sorted(d for d in os.listdir(self._backup_dir)
                      if os.path.isdir(os.path.join(self._backup_dir, d)))

    def _prune_backups(self):
        for old in self.list_backups()[:-MAX_BACKUPS]:
            shutil.rmtree(os.path.join(self._backup_dir, old), ignore_errors=True)

    def restore_backup(self, name=None):
        """Copy a backup (default: newest) back over the live data files."""
        backups = self.list_backups()
        if not backups:
            raise DataCorruptionError("There are no backups to restore.")
        name = name or backups[-1]
        if name not in backups:
            raise DataCorruptionError(f"Backup '{name}' does not exist.")
        folder = os.path.join(self._backup_dir, name)
        for filename in os.listdir(folder):
            if filename in FILES:
                shutil.copy2(os.path.join(folder, filename),
                             os.path.join(self._data_dir, filename))
        return name

    # ---- loading ----------------------------------------------------
    def load_all(self):
        """Rebuild a Library from disk. Missing files mean an empty library."""
        library = Library()
        try:
            for record in self._read("books.json"):
                library.add_item(item_from_dict(record))
            for record in self._read("members.json"):
                library.add_member(member_from_dict(record))
            for record in self._read("loans.json"):
                library.add_loan(self._loan_from_dict(library, record))
        except DataCorruptionError:
            raise
        except (KeyError, ValueError, TypeError, PSLMSError) as exc:
            raise DataCorruptionError(f"Data files are inconsistent: {exc!r}") from exc
        return library

    def _read(self, filename):
        path = os.path.join(self._data_dir, filename)
        if not os.path.exists(path):
            return []
        try:
            with open(path, encoding="utf-8") as handle:
                payload = json.load(handle)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise DataCorruptionError(f"{filename} is corrupted: {exc}") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
            raise DataCorruptionError(f"{filename} has an unexpected structure.")
        return payload["records"]

    @staticmethod
    def _loan_from_dict(library, d):
        returned = date.fromisoformat(d["return_date"]) if d.get("return_date") else None
        return LoanRecord(
            d["loan_id"], library.get_member(d["member_id"]), library.get_item(d["item_id"]),
            date.fromisoformat(d["issue_date"]), date.fromisoformat(d["due_date"]),
            returned, LoanStatus(d["status"]), d.get("note", ""))
