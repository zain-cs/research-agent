"""Calculator tool.

Evaluates arithmetic expressions safely — LLMs are notoriously unreliable at
precise multi-step arithmetic, so the agent should call this tool instead of
trying to compute numbers itself.

Uses Python's `ast` module to parse and evaluate only a whitelisted set of
safe operations — never `eval()`, which would execute arbitrary code.
"""
import ast
import operator

# Only these operators are permitted — anything else raises an error.
_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.FloorDiv: operator.floordiv,
}


def _eval_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant: {node.value!r}")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        return _ALLOWED_OPERATORS[op_type](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _ALLOWED_OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        return _ALLOWED_OPERATORS[op_type](_eval_node(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


def calculate(expression: str) -> str:
    """Safely evaluate a math expression like '12 * (7 + 3) / 2' and return the result."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree.body)
        return str(result)
    except ZeroDivisionError:
        return "Error: division by zero."
    except Exception as e:
        return f"Error: could not evaluate '{expression}' ({e})"


SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": (
            "Evaluate a mathematical expression (arithmetic, exponents, "
            "parentheses). Use this whenever a question requires precise "
            "numeric computation instead of estimating the answer yourself."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A math expression, e.g. '(45 * 12) / 3 + 7'.",
                },
            },
            "required": ["expression"],
        },
    },
}
