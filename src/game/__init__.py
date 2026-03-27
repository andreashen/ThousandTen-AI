"""
游戏模块
包含棋盘、积木、规则、引擎等核心组件
"""

from .board import Board
from .pieces import Piece, ALL_PIECES, create_all_pieces
from .rules import GameRules
from .engine import GameEngine

__all__ = [
    'Board',
    'Piece',
    'ALL_PIECES',
    'create_all_pieces',
    'GameRules',
    'GameEngine'
]
