"""
automation/file_manager.py — Local file and folder management
Aura can open, create, delete, search, and list files on your PC.
"""

import os
import shutil
import subprocess
import glob
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

# Safe root folders Aura is allowed to work in
# (prevents accidental deletion of system files)
SAFE_ROOTS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Pictures"),
    os.path.expanduser("~/Music"),
    os.path.expanduser("~/Videos"),
]


class FileManager:

    # ── Open files / folders ──────────────────────────────

    def open_file(self, filename: str) -> str:
        """
        Open a file with its default application.
        Searches Desktop, Documents, Downloads first.
        """
        # Search common locations
        found = self._find_file(filename)
        if found:
            try:
                os.startfile(found)
                logger.info(f"Opened file: {found}")
                return f"Opening {filename}!"
            except Exception as e:
                logger.error(f"Open file error: {e}")
                return f"Found {filename} but couldn't open it."

        return f"I couldn't find a file named {filename} on your PC."

    def open_folder(self, folder_name: str) -> str:
        """Open a folder in File Explorer."""
        # Named shortcuts
        shortcuts = {
            "desktop":   os.path.expanduser("~/Desktop"),
            "documents": os.path.expanduser("~/Documents"),
            "downloads": os.path.expanduser("~/Downloads"),
            "pictures":  os.path.expanduser("~/Pictures"),
            "music":     os.path.expanduser("~/Music"),
            "videos":    os.path.expanduser("~/Videos"),
            "this pc":   "explorer.exe",
        }

        key = folder_name.lower().strip()
        if key in shortcuts:
            path = shortcuts[key]
            try:
                subprocess.Popen(f'explorer "{path}"')
                return f"Opening {folder_name} folder!"
            except Exception as e:
                return f"Couldn't open {folder_name}."

        # Search for folder
        found = self._find_folder(folder_name)
        if found:
            subprocess.Popen(f'explorer "{found}"')
            return f"Opening {folder_name}!"

        return f"I couldn't find a folder named {folder_name}."

    # ── Create files / folders ────────────────────────────

    def create_folder(self, name: str, location: str = "Desktop") -> str:
        """Create a new folder on Desktop or Documents."""
        locations = {
            "desktop":   os.path.expanduser("~/Desktop"),
            "documents": os.path.expanduser("~/Documents"),
            "downloads": os.path.expanduser("~/Downloads"),
        }
        base = locations.get(location.lower(), os.path.expanduser("~/Desktop"))
        path = os.path.join(base, name)

        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"Folder created: {path}")
            return f"Folder '{name}' created on your {location}!"
        except Exception as e:
            logger.error(f"Create folder error: {e}")
            return f"Couldn't create folder '{name}'."

    def create_text_file(self, name: str, content: str = "", location: str = "Desktop") -> str:
        """Create a new text file with optional content."""
        if not name.endswith(".txt"):
            name += ".txt"

        locations = {
            "desktop":   os.path.expanduser("~/Desktop"),
            "documents": os.path.expanduser("~/Documents"),
        }
        base = locations.get(location.lower(), os.path.expanduser("~/Desktop"))
        path = os.path.join(base, name)

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            os.startfile(path)  # Open it immediately
            logger.info(f"Text file created: {path}")
            return f"Created and opened '{name}' on your {location}!"
        except Exception as e:
            logger.error(f"Create file error: {e}")
            return f"Couldn't create file '{name}'."

    # ── List files ────────────────────────────────────────

    def list_files(self, folder: str = "Desktop", extension: str = None) -> str:
        """
        List files in a folder. Optionally filter by extension.
        Example: list_files("Downloads", ".pdf")
        """
        locations = {
            "desktop":   os.path.expanduser("~/Desktop"),
            "documents": os.path.expanduser("~/Documents"),
            "downloads": os.path.expanduser("~/Downloads"),
            "pictures":  os.path.expanduser("~/Pictures"),
        }
        path = locations.get(folder.lower(), os.path.expanduser("~/Desktop"))

        try:
            all_files = os.listdir(path)

            if extension:
                ext = extension if extension.startswith(".") else f".{extension}"
                all_files = [f for f in all_files if f.lower().endswith(ext)]

            if not all_files:
                return f"No {'files' if not extension else extension + ' files'} found in {folder}."

            # Limit to 8 for TTS readability
            shown = all_files[:8]
            names = ", ".join(shown)
            more  = f" and {len(all_files) - 8} more" if len(all_files) > 8 else ""

            return f"Files in {folder}: {names}{more}."

        except Exception as e:
            logger.error(f"List files error: {e}")
            return f"Couldn't list files in {folder}."

    # ── Search files ──────────────────────────────────────

    def search_file(self, query: str) -> str:
        """
        Search for a file by name across common folders.
        Returns the path if found.
        """
        logger.info(f"Searching for file: {query}")
        found = self._find_file(query)

        if found:
            return f"Found it! {query} is located at {found}"
        return f"I couldn't find any file named {query} in your common folders."

    # ── Delete files ──────────────────────────────────────

    def delete_file(self, filename: str) -> str:
        """
        Delete a file — moves to Recycle Bin (safe delete).
        Only works in SAFE_ROOTS to prevent system damage.
        """
        found = self._find_file(filename)

        if not found:
            return f"I couldn't find {filename} to delete."

        # Safety check — only delete from safe folders
        is_safe = any(found.startswith(root) for root in SAFE_ROOTS)
        if not is_safe:
            return f"For safety, I can only delete files from your Desktop, Documents, or Downloads."

        try:
            # Use send2trash for safe recycle bin delete if available
            try:
                import send2trash
                send2trash.send2trash(found)
                logger.info(f"File moved to Recycle Bin: {found}")
                return f"{filename} has been moved to the Recycle Bin."
            except ImportError:
                # Fallback: permanent delete with warning
                os.remove(found)
                logger.info(f"File permanently deleted: {found}")
                return f"{filename} has been permanently deleted."

        except Exception as e:
            logger.error(f"Delete error: {e}")
            return f"Couldn't delete {filename}. It may be in use by another program."

    # ── Disk info ─────────────────────────────────────────

    def get_disk_info(self) -> str:
        """Return free and total disk space on C drive."""
        try:
            import psutil
            disk = psutil.disk_usage("C:\\")
            total = round(disk.total / (1024**3), 1)
            used  = round(disk.used  / (1024**3), 1)
            free  = round(disk.free  / (1024**3), 1)
            pct   = disk.percent
            return (
                f"Your C drive has {total} gigabytes total. "
                f"{used} gigabytes used, {free} gigabytes free. "
                f"Storage is {pct} percent full."
            )
        except Exception as e:
            return "Couldn't read disk information."

    # ── Recent files ──────────────────────────────────────

    def get_recent_files(self, count: int = 5) -> str:
        """List the most recently modified files across common folders."""
        all_files = []
        for root in SAFE_ROOTS:
            try:
                for f in os.listdir(root):
                    full = os.path.join(root, f)
                    if os.path.isfile(full):
                        mtime = os.path.getmtime(full)
                        all_files.append((mtime, f))
            except Exception:
                continue

        if not all_files:
            return "No recent files found."

        all_files.sort(reverse=True)
        recent = [name for _, name in all_files[:count]]
        return "Your most recent files are: " + ", ".join(recent) + "."

    # ── Helpers ───────────────────────────────────────────

    def _find_file(self, filename: str) -> str | None:
        """Search for a file across SAFE_ROOTS."""
        for root in SAFE_ROOTS:
            try:
                # Exact match
                exact = os.path.join(root, filename)
                if os.path.exists(exact):
                    return exact

                # Partial match
                for f in os.listdir(root):
                    if filename.lower() in f.lower():
                        return os.path.join(root, f)
            except Exception:
                continue
        return None

    def _find_folder(self, name: str) -> str | None:
        """Search for a folder across SAFE_ROOTS."""
        for root in SAFE_ROOTS:
            try:
                for item in os.listdir(root):
                    full = os.path.join(root, item)
                    if os.path.isdir(full) and name.lower() in item.lower():
                        return full
            except Exception:
                continue
        return None


# ── Singleton ─────────────────────────────────────────────
_fm = None

def get_file_manager() -> FileManager:
    global _fm
    if _fm is None:
        _fm = FileManager()
    return _fm


# ── Quick test ────────────────────────────────────────────
if __name__ == "__main__":
    fm = FileManager()
    print(fm.get_disk_info())
    print(fm.get_recent_files())
    print(fm.list_files("Desktop"))