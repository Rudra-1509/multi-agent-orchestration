from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

python_repl=PythonREPL()

@tool
def code_tool(code: str)-> str:
    """Executes Python commands."""
    try:
        results=python_repl.run(code)
        return results
    except Exception as e:
        return f"Error in repl tool: {str(e)}"