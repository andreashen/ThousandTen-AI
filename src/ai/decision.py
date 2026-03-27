"""
AI 决策算法模块
实现最优放置决策的搜索算法
"""

import time
from typing import List, Tuple, Optional, Dict
from src.game.board import Board
from src.game.pieces import Piece
from src.game.rules import GameRules
from .evaluator import Evaluator, evaluate_action


class DecisionMaker:
    """AI 决策器"""

    def __init__(self, use_long_bar_strategy: bool = True, time_limit: float = 1.0):
        self.use_long_bar_strategy = use_long_bar_strategy
        self.time_limit = time_limit
        self.last_decision_time = 0.0
        self.nodes_explored = 0

    def find_best_action(self, board: Board, pieces: List[Piece]) -> Optional[Tuple[int, int, int]]:
        """找到当前最优的放置动作"""
        start_time = time.time()
        self.nodes_explored = 0

        best_action = None
        best_score = float('-inf')

        # 生成所有可能的动作
        actions = self._generate_all_actions(board, pieces)
        if not actions:
            return None

        # 评估每个动作
        for piece_idx, row, col in actions:
            self.nodes_explored += 1

            score = self._evaluate_action(
                board, pieces, piece_idx, row, col
            )

            if score > best_score:
                best_score = score
                best_action = (piece_idx, row, col)

            elapsed = time.time() - start_time
            if elapsed > self.time_limit:
                break

        self.last_decision_time = time.time() - start_time
        return best_action

    def _evaluate_action(
        self, board: Board, pieces: List[Piece],
        piece_idx: int, row: int, col: int
    ) -> float:
        """评估单个动作的价值"""
        return evaluate_action(board, pieces, piece_idx, row, col)

    def _generate_all_actions(self, board: Board, pieces: List[Piece]) -> List[Tuple[int, int, int]]:
        """生成所有可能的动作，按优先级排序"""
        actions = []
        for piece_idx, piece in enumerate(pieces):
            placements = GameRules.get_legal_placements(board, piece)
            for row, col in placements:
                actions.append((piece_idx, row, col))

        # 按消行/列潜力排序优先评估
        def sort_key(a):
            piece_idx, row, col = a
            _, cb = GameRules.calculate_placement_score(board, pieces[piece_idx], row, col)
            return -cb  # 消行优先

        actions.sort(key=sort_key)
        return actions

    def find_best_sequence(self, board: Board, pieces: List[Piece]) -> List[Tuple[int, int, int]]:
        """找到当前轮次的最优放置序列（贪婪）"""
        start_time = time.time()
        sequence = []
        remaining = pieces.copy()
        current_board = board.copy()

        while remaining:
            best_action = None
            best_score = float('-inf')

            for piece_idx, piece in enumerate(remaining):
                placements = GameRules.get_legal_placements(current_board, piece)
                for row, col in placements:
                    self.nodes_explored += 1
                    score = self._evaluate_action(
                        current_board, remaining, piece_idx, row, col
                    )
                    if score > best_score:
                        best_score = score
                        best_action = (piece_idx, row, col)

            if best_action is None:
                break

            piece_idx, row, col = best_action
            piece = remaining[piece_idx]
            original_idx = pieces.index(piece)
            sequence.append((original_idx, row, col))

            current_board.place_piece(piece, row, col)
            cleared_rows, cleared_cols = current_board.find_cleared_lines()
            if cleared_rows or cleared_cols:
                current_board.clear_lines(cleared_rows, cleared_cols)

            remaining.pop(piece_idx)

            elapsed = time.time() - start_time
            if elapsed > self.time_limit:
                break

        self.last_decision_time = time.time() - start_time
        return sequence

    def get_stats(self) -> Dict:
        return {
            "decision_time": self.last_decision_time,
            "nodes_explored": self.nodes_explored
        }


if __name__ == "__main__":
    from src.game import Board, ALL_PIECES
    board = Board()
    board.place_piece(ALL_PIECES[5], 0, 0)
    board.place_piece(ALL_PIECES[3], 0, 2)
    test_pieces = [ALL_PIECES[0], ALL_PIECES[10], ALL_PIECES[16]]
    decision_maker = DecisionMaker()
    best_action = decision_maker.find_best_action(board, test_pieces)
    if best_action:
        piece_idx, row, col = best_action
        print(f"最优动作: 放置 {test_pieces[piece_idx].name} 到 ({row}, {col})")
    print(f"决策时间: {decision_maker.last_decision_time*1000:.2f}ms")
