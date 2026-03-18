from langchain_community.agent_toolkits import FileManagementToolkit
import os

BASE_DIR = os.path.abspath("workspace")

INPUT_DIR = os.path.join(BASE_DIR, "inputs")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
LOG_DIR = os.path.join(BASE_DIR, "logs")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
def get_file_tools():

    for d in [INPUT_DIR, OUTPUT_DIR, LOG_DIR, TEMP_DIR]:
        os.makedirs(d, exist_ok=True)

    def prefix_tools(tools, prefix):
        for tool in tools:
            tool.name = f"{prefix}_{tool.name}"
        return tools

    def enhance_descriptions(tools, context):
        for tool in tools:
            tool.description += f" (Use for {context})"
        return tools

    file_input_tools = FileManagementToolkit(
        root_dir=INPUT_DIR,
        selected_tools=["read_file", "list_directory"]
    ).get_tools()

    file_output_tools = FileManagementToolkit(
        root_dir=OUTPUT_DIR,
        selected_tools=["write_file", "list_directory"]
    ).get_tools()

    file_temp_tools = FileManagementToolkit(
        root_dir=TEMP_DIR,
        selected_tools=["read_file", "write_file", "delete_file"]
    ).get_tools()

    file_log_tools = FileManagementToolkit(
        root_dir=LOG_DIR,
        selected_tools=["write_file"]
    ).get_tools()

    file_input_tools = enhance_descriptions(prefix_tools(file_input_tools, "input"), "reading input data")
    file_output_tools = enhance_descriptions(prefix_tools(file_output_tools, "output"), "saving final results")
    file_temp_tools = enhance_descriptions(prefix_tools(file_temp_tools, "temp"), "temporary intermediate work")
    file_log_tools = enhance_descriptions(prefix_tools(file_log_tools, "log"), "logging important events")

    return {
        "input": file_input_tools,
        "output": file_output_tools,
        "temp": file_temp_tools,
        "log": file_log_tools
    }