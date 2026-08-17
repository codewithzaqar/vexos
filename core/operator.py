"""core/operator.py - VexOS Operator Definitions"""
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class OperatorType(Enum):
    DELETE = auto()
    YANK = auto()
    CHANGE = auto()


@dataclass
class PendingOperator:
    """Represents an operator waiting for a motion."""
    op_type: OperatorType
    count: int = 1
    register: str = ""


# Map of normal-mode keys to operators
OPERATOR_MAP = {
    'd': OperatorType.DELETE,
    'y': OperatorType.YANK,
    'c': OperatorType.CHANGE,
}

# Single-key operators (no motion needed)
SIMPLE_OPERATORS = {
    'x': OperatorType.DELETE,
}
