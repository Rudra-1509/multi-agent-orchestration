import boto3
import os

from .base import StorageBackend


class S3StorageBackend(StorageBackend):

    def __init__(self):

        self.bucket = os.getenv("S3_BUCKET")

        self.base_prefix = os.getenv(
            "S3_BASE_PREFIX",
            ""
        ).strip("/")

        self.client = boto3.client(
            service_name="s3",

            endpoint_url=os.getenv(
                "R2_ENDPOINT_URL"
            ),

            aws_access_key_id=os.getenv(
                "R2_ACCESS_KEY_ID"
            ),

            aws_secret_access_key=os.getenv(
                "R2_SECRET_ACCESS_KEY"
            ),

            region_name="auto"
        )

    def _resolve_key(self, path: str):

        normalized_path = path.strip("/")

        if self.base_prefix:
            return f"{self.base_prefix}/{normalized_path}"

        return normalized_path

    def read_file(self, path: str) -> bytes:

        key = self._resolve_key(path)

        response = self.client.get_object(
            Bucket=self.bucket,
            Key=key
        )

        return response["Body"].read()

    def write_file(self, path: str, data: bytes):

        key = self._resolve_key(path)

        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data
        )

    def list_files(self, path: str):

        key_prefix = self._resolve_key(path)

        response = self.client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=key_prefix
        )

        files = []

        for obj in response.get("Contents", []):

            full_key = obj["Key"]

            if self.base_prefix:

                logical_path = full_key.replace(
                    f"{self.base_prefix}/",
                    "",
                    1
                )

            else:
                logical_path = full_key

            files.append(logical_path)

        return files

    def delete_file(self, path: str):

        key = self._resolve_key(path)

        self.client.delete_object(
            Bucket=self.bucket,
            Key=key
        )