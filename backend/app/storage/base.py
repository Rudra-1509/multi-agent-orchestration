from abc import ABC, abstractmethod
from typing import List

class StorageBackend(ABC):

    @abstractmethod
    def read_file(self, path: str) -> bytes:
        pass

    @abstractmethod
    def write_file(self, path: str, data: bytes):
        pass

    @abstractmethod
    def list_files(self, path: str) -> List[str]:
        pass

    @abstractmethod
    def delete_file(self, path: str):
        pass