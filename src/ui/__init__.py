"""
UI 模块
包含 Pygame 可视化界面
"""

from .pygame_view import PygameView
from .colors import get_piece_color

__all__ = [
    'PygameView',
    'get_piece_color'
]
