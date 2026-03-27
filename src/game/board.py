"""
棋盘状态管理模块
维护 10x10 网格状态，提供核心操作接口
"""

from typing import List, Set, Tuple, Optional
from copy import deepcopy
from .pieces import Piece


class Board:
    """棋盘类"""

    def __init__(self, size: int = 10):
        """
        初始化棋盘
        :param size: 棋盘尺寸，默认 10x10
        """
        self.size = size
        # 0 表示空格，1 表示已占用
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.score = 0

    def copy(self) -> 'Board':
        """创建棋盘深拷贝"""
        new_board = Board(self.size)
        new_board.grid = deepcopy(self.grid)
        new_board.score = self.score
        return new_board

    def is_valid_position(self, row: int, col: int) -> bool:
        """检查坐标是否在棋盘范围内"""
        return 0 <= row < self.size and 0 <= col < self.size

    def is_empty(self, row: int, col: int) -> bool:
        """检查指定位置是否为空"""
        return self.is_valid_position(row, col) and self.grid[row][col] == 0

    def can_place(self, piece: Piece, row: int, col: int) -> bool:
        """
        检查是否可以在指定位置放置积木
        :param piece: 积木对象
        :param row: 起始行
        :param col: 起始列
        :return: 是否可以放置
        """
        cells = piece.get_cells(row, col)
        for r, c in cells:
            if not self.is_empty(r, c):
                return False
        return True

    def place_piece(self, piece: Piece, row: int, col: int) -> bool:
        """
        在指定位置放置积木
        :param piece: 积木对象
        :param row: 起始行
        :param col: 起始列
        :return: 是否成功放置
        """
        if not self.can_place(piece, row, col):
            return False

        # 放置积木
        cells = piece.get_cells(row, col)
        for r, c in cells:
            self.grid[r][c] = 1

        # 计算放置得分
        self.score += len(cells)

        return True

    def find_cleared_lines(self) -> Tuple[Set[int], Set[int]]:
        """
        查找可以消除的行和列
        :return: (可消除的行集合, 可消除的列集合)
        """
        cleared_rows = set()
        cleared_cols = set()

        # 检查每一行
        for row in range(self.size):
            if all(self.grid[row][col] == 1 for col in range(self.size)):
                cleared_rows.add(row)

        # 检查每一列
        for col in range(self.size):
            if all(self.grid[row][col] == 1 for row in range(self.size)):
                cleared_cols.add(col)

        return cleared_rows, cleared_cols

    def clear_lines(self, rows: Set[int], cols: Set[int]) -> int:
        """
        消除指定的行和列，并返回消除奖励得分
        :param rows: 要消除的行集合
        :param cols: 要消除的列集合
        :return: 消除奖励得分（每行/列 10 分）
        """
        # 清除行
        for row in rows:
            for col in range(self.size):
                self.grid[row][col] = 0

        # 清除列
        for col in cols:
            for row in range(self.size):
                self.grid[row][col] = 0

        # 计算消除奖励
        bonus = (len(rows) + len(cols)) * 10
        self.score += bonus

        return bonus

    def get_empty_cells(self) -> Set[Tuple[int, int]]:
        """获取所有空格坐标"""
        empty_cells = set()
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] == 0:
                    empty_cells.add((row, col))
        return empty_cells

    def get_empty_count(self) -> int:
        """获取空格数量"""
        return sum(1 for row in range(self.size) for col in range(self.size) if self.grid[row][col] == 0)

    def get_filled_count(self) -> int:
        """获取已占用格子数量"""
        return self.size * self.size - self.get_empty_count()

    def __str__(self) -> str:
        """字符串表示，用于调试"""
        lines = []
        lines.append(f"Score: {self.score}")
        lines.append("   " + " ".join(str(i % 10) for i in range(self.size)))
        for row in range(self.size):
            lines.append(f"{row:2d} " + " ".join(
                "█" if self.grid[row][col] == 1 else "·"
                for col in range(self.size)
            ))
        return "\n".join(lines)


if __name__ == "__main__":
    # 测试代码
    from .pieces import ALL_PIECES

    board = Board()
    print("初始棋盘:")
    print(board)
    print()

    # 放置一个 2x2 积木
    piece_2x2 = ALL_PIECES[5]  # 2x2 积木
    if board.place_piece(piece_2x2, 0, 0):
        print(f"放置 {piece_2x2.name} 后:")
        print(board)
        print()

    # 放置一个 1x3 积木填满第一行
    piece_1x3_h = ALL_PIECES[3]  # 1x3_h 积木
    if board.place_piece(piece_1x3_h, 0, 2):
        print(f"放置 {piece_1x3_h.name} 后:")
        print(board)

        rows, cols = board.find_cleared_lines()
        print(f"可消除的行: {rows}")
        print(f"可消除的列: {cols}")

        if rows or cols:
            bonus = board.clear_lines(rows, cols)
            print(f"消除后（奖励 {bonus} 分）:")
            print(board)
