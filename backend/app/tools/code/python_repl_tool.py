from langchain.tools import StructuredTool
from langchain_experimental.utilities import PythonREPL
from pydantic import BaseModel

python_repl=PythonREPL()

class PythonREPLInput(BaseModel):
    code: str

def repl_func(code: str)-> str:
    try:
        results=python_repl.run(code)
        return results
    except Exception as e:
        return f"Error in search tool: {str(e)}"
    
code_tool=StructuredTool.from_function(
    func=repl_func,
    name="python_repl",
    description="Executes Python commands.",
    args_schema=PythonREPLInput
)