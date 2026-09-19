import json
import threading
from pathlib import Path
from typing import Any


class StorageError(RuntimeError):
    """Raised when local storage cannot be read safely."""


class JsonProductRepository:
    """A small JSON repository suitable for one local application process."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.RLock()

    def load_all(self) -> list[dict[str, Any]]:
        with self._lock:
            if not self.path.exists():
                return []
            try:
                with self.path.open("r", encoding="utf-8") as file:
                    data = json.load(file)
            except (OSError, json.JSONDecodeError) as error:
                raise StorageError("Не вдалося прочитати файл даних") from error
            if not isinstance(data, list) or not all(
                isinstance(item, dict) for item in data
            ):
                raise StorageError("Файл даних має неправильну структуру")
            return data

    def save_all(self, products: list[dict[str, Any]]) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
            try:
                with temporary_path.open("w", encoding="utf-8") as file:
                    json.dump(products, file, ensure_ascii=False, indent=2)
                    file.flush()
                temporary_path.replace(self.path)
            except OSError as error:
                raise StorageError("Не вдалося зберегти файл даних") from error
