import ast
import operator
from typing import Any


class CalculatorTool:
    name = "calculator"
    description = "安全计算器，只支持基础四则运算。"
    args_schema = {"expression": "string"}

    _operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    async def run(self, args: dict[str, Any]) -> dict[str, Any]:
        expression = str(args.get("expression", ""))
        tree = ast.parse(expression, mode="eval")
        result = self._eval(tree.body)
        return {"expression": expression, "result": result}

    def _eval(self, node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
            return float(node.value)
        if isinstance(node, ast.BinOp):
            operator_fn = self._operators.get(type(node.op))
            if operator_fn is None:
                raise ValueError("Unsupported operator")
            return float(operator_fn(self._eval(node.left), self._eval(node.right)))
        if isinstance(node, ast.UnaryOp):
            operator_fn = self._operators.get(type(node.op))
            if operator_fn is None:
                raise ValueError("Unsupported unary operator")
            return float(operator_fn(self._eval(node.operand)))
        raise ValueError("Unsupported expression")
