# services/agent_service/tools/calculator.py

import ast
import operator as op

from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("CalculatorTool"), {})

# Безопасные операции
SAFE_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
}


def eval_expr(expr):
    """
    Безопасно вычисляет математическое выражение через AST.
    Поддерживаются +, -, *, /, %, **, отрицательные числа.
    """
    try:
        node = ast.parse(expr, mode='eval').body
        return _eval(node)
    except Exception as e:
        logger.debug(f"Calculator eval error: {e}")
        return f"Ошибка вычисления выражения: {e}"


def _eval(node):
    if isinstance(node, ast.Num):  # число
        return node.n
    elif isinstance(node, ast.BinOp):  # бинарная операция
        left = _eval(node.left)
        right = _eval(node.right)
        return SAFE_OPERATORS[type(node.op)](left, right)
    elif isinstance(node, ast.UnaryOp):  # унарная операция
        operand = _eval(node.operand)
        return SAFE_OPERATORS[type(node.op)](operand)
    else:
        raise TypeError(f"Неподдерживаемый тип: {type(node)}")


async def calculator(*, expression=None, args=None, **kwargs):
    """
    Инструмент для вычисления математических выражений.
    Поддерживает:
      - expression: str
      - args: {"expression": str} (для совместимости с LLM)
    """
    expr = None

    # Сначала ищем в args
    if args and isinstance(args, dict):
        expr = args.get("expression")

    # Если нет, берем напрямую
    if expression:
        expr = expression

    if not expr:
        return "Нет выражения для вычисления."

    # Возвращаем результат
    result = eval_expr(expr)
    return str(result)
