import os

from .local import LocalStorageBackend
from .s3 import S3StorageBackend


def get_storage_backend():

    backend = os.getenv(
        "FILE_STORAGE_BACKEND",
        "local"
    )

    if backend == "s3":
        return S3StorageBackend()

    return LocalStorageBackend()