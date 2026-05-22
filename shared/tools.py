"""Optional tool use for assistants (bonus: memory + tools)."""

from __future__ import annotations

import ast
import operator
import re

SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _eval_expr(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPS:
        return SAFE_OPS[type(node.op)](_eval_expr(node.left), _eval_expr(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPS:
        return SAFE_OPS[type(node.op)](_eval_expr(node.operand))
    raise ValueError("Unsupported expression")


def safe_calculate(expression: str) -> str:
    tree = ast.parse(expression.strip(), mode="eval")
    result = _eval_expr(tree.body)
    return str(result)


TOOL_PATTERN = re.compile(r"\bcalc:\s*([0-9+\-*/().\s]+)", re.IGNORECASE)


def maybe_run_tools(user_message: str) -> str | None:
    """If user asks calc: 2+2, return tool result to inject into context."""
    match = TOOL_PATTERN.search(user_message)
    if not match:
        return None
    try:
        return f"[Tool result] {safe_calculate(match.group(1))}"
    except Exception:
        return "[Tool error] Could not evaluate expression."
