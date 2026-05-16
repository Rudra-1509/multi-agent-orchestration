import ast
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL

python_repl=PythonREPL()

BLOCKED_NODES = (
    ast.Import,
    ast.ImportFrom,
    ast.With,
    ast.AsyncWith,
    ast.Try,
    ast.ClassDef,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.Global,
    ast.Nonlocal,
    ast.Lambda,
)

BLOCKED_CALLS = {"open", "exec", "eval", "__import__", "compile", "input"}


def _validate_code_is_safe(code: str) -> None:
    tree = ast.parse(code, mode="exec")
    for node in ast.walk(tree):
        if isinstance(node, BLOCKED_NODES):
            raise ValueError(f"Disallowed Python construct: {type(node).__name__}")
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in {"os", "sys", "subprocess"}:
            raise ValueError("Disallowed module access.")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
            raise ValueError(f"Disallowed function call: {node.func.id}")

@tool
def code_tool(code: str)-> str:
    """Executes restricted Python commands (sandbox-lite checks)."""
    try:
        _validate_code_is_safe(code)
        results=python_repl.run(code)
        return results
    except Exception as e:
        return f"Error in repl tool: {str(e)}"
