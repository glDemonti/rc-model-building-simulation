import ast # for parsing expressions
from typing import Any, Tuple, List  # for type annotations

class EvalError(Exception):
    """Custom exception for evaluation errors."""
    pass

class ExpressionEvaluator:
    """
    Secure expression evaluator:
    - only allows nodes: Expression, BinOP, UnaryOp, Constant (Num), parentheses
    - supports operators: +, -, *, /, **, %, //
    - no names, function calls, or other constructs allowed --> prevents code injection
    """

    # Allowed AST node types.
    ALLOWED_BINOPS = (
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
        ast.Mod, ast.FloorDiv
    )
    # Allowed unary operators.
    ALLOWED_UNARYOPS = (ast.UAdd, ast.USub)

    def __init__(self) -> None:
        pass

    def _eval_node(self, node: ast.AST) -> float:
        """Recursively evaluate an AST node."""
        if isinstance(node, ast.Expression):    
            return self._eval_node(node.body)
        
        if isinstance(node, ast.Constant):      
            if isinstance(node.value, (int, float)):
                return float(node.value)
            else:
                raise EvalError(f"Nur numerische Konstanten sind erlaubt, nicht {node.value!r}")
        
        if isinstance(node, ast.BinOp):
            if not isinstance(node.op, self.ALLOWED_BINOPS):
                raise EvalError(f"Operator {type(node.op).__name__} ist nicht erlaubt.")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op = node.op
            if isinstance(op, ast.Add): return left + right
            if isinstance(op, ast.Sub): return left - right
            if isinstance(op, ast.Mult): return left * right
            if isinstance(op, ast.Div):
                if right == 0:
                    raise EvalError("Division durch Null ist nicht erlaubt.")
                return left / right
            if isinstance(op, ast.Pow): return left ** right
            if isinstance(op, ast.Mod): return left % right
            if isinstance(op, ast.FloorDiv):
                if right == 0:
                    raise EvalError("Ganzzahlige Division durch Null ist nicht erlaubt.")
                return left // right
            
        if isinstance(node, ast.UnaryOp):
            if not  isinstance(node.op, self.ALLOWED_UNARYOPS):
                raise EvalError(f"Unary operator {type(node.op).__name__} ist nicht erlaubt.")
            val = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd): return +val
            if isinstance(node.op, ast.USub): return -val
        # for all other nodes: deny
        raise EvalError(f"Nicht erlaubter Ausdruck: {type(node).__name__}")
    
    def save_eval(self, expr: str) -> float:
        """Safely evaluate a mathematical expression.
        Accepts e.g "2 + 3 * (4 - 1)" and returns the result as float. Or raises EvalError.
        """
        if not isinstance(expr, str):
            raise EvalError("Der Ausdruck muss ein String sein.")
        src = expr.strip()
        if src == "":
            raise EvalError("Leerer Ausdruck ist nicht erlaubt.")
        try:
            node = ast.parse(src, mode='eval')
        except SyntaxError as e:
            raise EvalError(f"Syntaxfehler im Ausdruck: {e}") from e
        return self._eval_node(node)
    
    def evaluate_cfg(self, cfg: dict) -> Tuple[dict, List[str]]:
        """
        Runs recursive true the dict. Evaluates all fields with 'expression' and sets the result in 'value'.
        Returns the modified dict and a list of error messages.
        Errors get collected; 'value' is not set if evaluation fails.
        """
        errors = []

        def _walk(o, path=""):
            if isinstance(o, dict):
                # if dict has 'expression', evaluate it
                if "expression" in o and isinstance(o["expression"], str):
                    expr = o["expression"]
                    try:
                        v = self.save_eval(expr)
                        o["value"] = v
                    except EvalError as e:
                        errors.append(f"{path or '/'}: {e}")
                # recurse for child keys
                for k, v in o.items():
                    # avoid recusing on already changed 'value' keys
                    if k == "value":
                        continue
                    _walk(v, path=f"{path}/{k}" if path else k)
            elif isinstance(o, list):
                for i, item in enumerate(o):
                    _walk(item, path=f"{path}[{i}]")
            # primiteves -> do nothing
        _walk(cfg, path="")
        return cfg, errors

