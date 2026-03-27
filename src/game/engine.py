"""
游戏引擎模块
管理游戏主循环、积木生成、轮次控制
"""

import random
from typing import List, Optional, Tuple
from .board import Board
from .pieces import Piece, ALL_PIECES
from .rules import GameRules


class GameEngine:
    """游戏引擎类"""

    def __init__(self, board_size: int = 10, pieces_per_round: int = 3):
        """
        初始化游戏引擎
        :param board_size: 棋盘尺寸
        :param pieces_per_round: 每轮生成的积木数量
        """
        self.board = Board(board_size)
        self.pieces_per_round = pieces_per_round
        self.current_pieces: List[Piece] = []
        self.round = 0
        self.game_over = False

    def generate_pieces(self) -> List[Piece]:
        """
        随机生成一轮的积木
        :return: 积木列表
        """
        return [random.choice(ALL_PIECES) for _ in range(self.pieces_per_round)]

    def start_new_round(self):
        """开始新一轮，生成新的积木"""
        self.current_pieces = self.generate_pieces()
        self.round += 1

        # 检查新生成的积木是否都无法放置
        if GameRules.is_game_over(self.board, self.current_pieces):
            self.game_over = True

    def place_piece(self, piece_index: int, row: int, col: int) -> bool:
        """
        放置指定索引的积木到指定位置
        :param piece_index: 积木在 current_pieces 中的索引
        :param row: 起始行
        :param col: 起始列
        :return: 是否成功放置
        """
        if self.game_over:
            return False

        if piece_index < 0 or piece_index >= len(self.current_pieces):
            return False

        piece = self.current_pieces[piece_index]

        # 尝试放置积木
        if not self.board.place_piece(piece, row, col):
            return False

        # 执行消除
        cleared_rows, cleared_cols = self.board.find_cleared_lines()
        if cleared_rows or cleared_cols:
            self.board.clear_lines(cleared_rows, cleared_cols)

        # 移除已放置的积木
        self.current_pieces.pop(piece_index)

        # 检查是否需要开始新一轮
        if not self.current_pieces:
            self.start_new_round()
        else:
            # 检查剩余积木是否都无法放置
            if GameRules.is_game_over(self.board, self.current_pieces):
                self.game_over = True

        return True

    def get_score(self) -> int:
        """获取当前得分"""
        return self.board.score

    def is_game_over(self) -> bool:
        """判断游戏是否结束"""
        return self.game_over

    def get_state(self) -> dict:
        """
        获取游戏状态快照
        :return: 包含 board, current_pieces, score, round, game_over 的字典
        """
        return {
            "board": self.board,
            "current_pieces": self.current_pieces.copy(),
            "score": self.board.score,
            "round": self.round,
            "game_over": self.game_over
        }

    def reset(self):
        """重置游戏"""
        self.board = Board(self.board.size)
        self.current_pieces = []
        self.round = 0
        self.game_over = False
        self.start_new_round()


if __name__ == "__main__":
    # 测试代码
    engine = GameEngine()
    engine.start_new_round()

    print(f"第 {engine.round} 轮，积木: {[p.name for p in engine.current_pieces]}")
    print(engine.board)
    print()

    # 手动放置一些积木进行测试
    pieces = engine.current_pieces
    if pieces:
        piece = pieces[0]
        placements = GameRules.get_legal_placements(engine.board, piece)
        if placements:
            row, col = placements[0]
            print(f"放置 {piece.name} 到 ({row}, {col})")
            engine.place_piece(0, row, col)
            print(f"得分: {engine.get_score()}")
            print(f"剩余积木: {[p.name for p in engine.current_pieces]}")
            print(engine.board)
