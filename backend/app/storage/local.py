import os

from .base import StorageBackend


class LocalStorageBackend(StorageBackend):

    def __init__(self):
        self.base_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                os.pardir,
                os.pardir,
                "workspace"
            )
        )

    def _resolve_path(self, path: str):
        return os.path.join(self.base_dir, path)

    def read_file(self, path: str) -> bytes:
        resolved = self._resolve_path(path)

        with open(resolved, "rb") as f:
            return f.read()

    def write_file(self, path: str, data: bytes):
        resolved = self._resolve_path(path)

        os.makedirs(os.path.dirname(resolved), exist_ok=True)

        with open(resolved, "wb") as f:
            f.write(data)

    def list_files(self, path: str):
        resolved = self._resolve_path(path)

        return os.listdir(resolved)

    def delete_file(self, path: str):
        resolved = self._resolve_path(path)

        os.remove(resolved)