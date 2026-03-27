"""
游戏规则验证模块
提供放置检测、消除判定、得分计算、游戏结束判定等核心规则
"""

from typing import List, Tuple, Optional
from .board import Board
from .pieces import Piece


class GameRules:
    """游戏规则类"""

    @staticmethod
    def get_legal_placements(board: Board, piece: Piece) -> List[Tuple[int, int]]:
        """
        获取积木的所有合法放置位置
        :param board: 棋盘对象
        :param piece: 积木对象
        :return: 合法位置列表 [(row, col), ...]
        """
        legal_placements = []

        for row in range(board.size):
            for col in range(board.size):
                if board.can_place(piece, row, col):
                    legal_placements.append((row, col))

        return legal_placements

    @staticmethod
    def can_place_any(board: Board, pieces: List[Piece]) -> bool:
        """
        检查给定的积木列表中是否至少有一个可以放置
        :param board: 棯盘对象
        :param pieces: 积木列表
        :return: 是否至少有一个积木可以放置
        """
        for piece in pieces:
            placements = GameRules.get_legal_placements(board, piece)
            if placements:
                return True
        return False

    @staticmethod
    def is_game_over(board: Board, current_pieces: List[Piece]) -> bool:
        """
        判断游戏是否结束
        :param board: 棋盘对象
        :param current_pieces: 当前备选区的积木列表
        :return: 是否游戏结束
        """
        # 如果还有积木可以放置，游戏未结束
        if GameRules.can_place_any(board, current_pieces):
            return False

        # 如果所有积木都无法放置，游戏结束
        return True

    @staticmethod
    def calculate_placement_score(board: Board, piece: Piece, row: int, col: int) -> Tuple[int, int]:
        """
        计算放置积木的得分（不实际放置，只计算）
        :param board: 棋盘对象
        :param piece: 积木对象
        :param row: 起始行
        :param col: 起始列
        :return: (放置得分, 消除奖励得分)
        """
        # 放置得分 = 积木占用格子数
        placement_score = len(piece.shape)

        # 模拟放置以计算消除奖励
        test_board = board.copy()
        test_board.place_piece(piece, row, col)
        cleared_rows, cleared_cols = test_board.find_cleared_lines()
        clear_bonus = (len(cleared_rows) + len(cleared_cols)) * 10

        return placement_score, clear_bonus

    @staticmethod
    def simulate_placement(board: Board, piece: Piece, row: int, col: int) -> Board:
        """
        模拟放置积木并返回新棋盘（不修改原棋盘）
        :param board: 原棋盘对象
        :param piece: 积木对象
        :param row: 起始行
        :param col: 起始列
        :return: 放置后的新棋盘对象
        """
        new_board = board.copy()
        new_board.place_piece(piece, row, col)

        # 执行消除
        cleared_rows, cleared_cols = new_board.find_cleared_lines()
        if cleared_rows or cleared_cols:
            new_board.clear_lines(cleared_rows, cleared_cols)

        return new_board


if __name__ == "__main__":
    # 测试代码
    from .pieces import ALL_PIECES

    board = Board()
    board.place_piece(ALL_PIECES[5], 0, 0)  # 2x2

    print("测试合法放置位置获取:")
    piece_1x3 = ALL_PIECES[3]  # 1x3_h
    placements = GameRules.get_legal_placements(board, piece_1x3)
    print(f"{piece_1x3.name} 有 {len(placements)} 个合法位置")
    print(f"前5个: {placements[:5]}")

    print("\n测试游戏结束判定:")
    test_pieces = [ALL_PIECES[0], ALL_PIECES[5]]  # 1x1 和 2x2
    can_place = GameRules.can_place_any(board, test_pieces)
    print(f"是否可以放置: {can_place}")
    print(f"是否游戏结束: {not can_place}")
