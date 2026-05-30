import os

from langchain.tools import BaseTool
from pydantic import Field

from app.storage.factory import get_storage_backend


storage = get_storage_backend()


class BaseFileTool(BaseTool):

    directory: str = Field(...)

    def build_path(self, filename: str) -> str:
        """
        Convert logical filename into logical storage path.
        """

        filename = filename.strip("/")

        return f"{self.directory}/{filename}"



class ReadInputFileTool(BaseFileTool):

    name: str = "input_read_file"

    description: str = (
        "Read files from the inputs directory. "
        "Use this for reading uploaded input data."
    )

    directory: str = "inputs"

    def _run(self, filename: str) -> str:

        path = self.build_path(filename)

        data = storage.read_file(path)

        return data.decode("utf-8")


class ListInputDirectoryTool(BaseFileTool):

    name: str = "input_list_directory"

    description: str = (
        "List files inside the inputs directory."
    )

    directory: str = "inputs"

    def _run(self, path: str = ""):

        logical_path = self.build_path(path)

        return storage.list_files(logical_path)


class WriteOutputFileTool(BaseFileTool):

    name: str = "output_write_file"

    description: str = (
        "Write files into the outputs directory. "
        "Use this for saving final results."
    )

    directory: str = "outputs"

    def _run(self, filename: str, content: str):

        path = self.build_path(filename)

        storage.write_file(
            path,
            content.encode("utf-8")
        )

        return f"Successfully wrote file to {path}"


class ListOutputDirectoryTool(BaseFileTool):

    name: str = "output_list_directory"

    description: str = (
        "List files inside the outputs directory."
    )

    directory: str = "outputs"

    def _run(self, path: str = ""):

        logical_path = self.build_path(path)

        return storage.list_files(logical_path)


class ReadTempFileTool(BaseFileTool):

    name: str = "temp_read_file"

    description: str = (
        "Read temporary intermediate files."
    )

    directory: str = "temp"

    def _run(self, filename: str):

        path = self.build_path(filename)

        data = storage.read_file(path)

        return data.decode("utf-8")


class WriteTempFileTool(BaseFileTool):

    name: str = "temp_write_file"

    description: str = (
        "Write temporary intermediate files."
    )

    directory: str = "temp"

    def _run(self, filename: str, content: str):

        path = self.build_path(filename)

        storage.write_file(
            path,
            content.encode("utf-8")
        )

        return f"Successfully wrote temp file to {path}"


class DeleteTempFileTool(BaseFileTool):

    name: str = "temp_delete_file"

    description: str = (
        "Delete temporary files."
    )

    directory: str = "temp"

    def _run(self, filename: str):

        path = self.build_path(filename)

        storage.delete_file(path)

        return f"Deleted temp file {path}"

class WriteLogFileTool(BaseFileTool):

    name: str = "log_write_file"

    description: str = (
        "Write execution logs and important events."
    )

    directory: str = "logs"

    def _run(self, filename: str, content: str):

        path = self.build_path(filename)

        storage.write_file(
            path,
            content.encode("utf-8")
        )

        return f"Successfully wrote log file to {path}"

def get_file_tools():

    return {

        "input": [
            ReadInputFileTool(),
            ListInputDirectoryTool()
        ],

        "output": [
            WriteOutputFileTool(),
            ListOutputDirectoryTool()
        ],

        "temp": [
            ReadTempFileTool(),
            WriteTempFileTool(),
            DeleteTempFileTool()
        ],

        "log": [
            WriteLogFileTool()
        ]
    }