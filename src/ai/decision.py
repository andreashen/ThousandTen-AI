"""
AI 决策算法模块
实现最优放置决策的搜索算法
"""

import time
from typing import List, Tuple, Optional, Dict
from src.game.board import Board
from src.game.pieces import Piece
from src.game.rules import GameRules
from .evaluator import Evaluator


class DecisionMaker:
    """AI 决策器"""

    def __init__(self, use_long_bar_strategy: bool = True, time_limit: float = 1.0):
        """
        初始化决策器
        :param use_long_bar_strategy: 是否启用长条积木特殊策略
        :param time_limit: 单步决策时间限制（秒）
        """
        self.use_long_bar_strategy = use_long_bar_strategy
        self.time_limit = time_limit
        self.last_decision_time = 0.0
        self.nodes_explored = 0

    def find_best_action(self, board: Board, pieces: List[Piece]) -> Optional[Tuple[int, int, int]]:
        """
        找到当前最优的放置动作
        :param board: 当前棋盘
        :param pieces: 当前可用的积木列表
        :return: (piece_index, row, col) 或 None（如果无法放置）
        """
        start_time = time.time()
        self.nodes_explored = 0

        best_action = None
        best_score = float('-inf')

        # 获取所有可能的动作
        actions = self._generate_all_actions(board, pieces)

        if not actions:
            return None

        # 评估每个动作
        for piece_idx, row, col in actions:
            self.nodes_explored += 1

            # 使用长条策略评估
            if self.use_long_bar_strategy:
                score = Evaluator.evaluate_with_long_bar_penalty(board, pieces[piece_idx], row, col)
            else:
                score = Evaluator.evaluate_placement(board, pieces[piece_idx], row, col)

            if score > best_score:
                best_score = score
                best_action = (piece_idx, row, col)

            # 检查时间限制
            elapsed = time.time() - start_time
            if elapsed > self.time_limit:
                break

        self.last_decision_time = time.time() - start_time
        return best_action

    def _generate_all_actions(self, board: Board, pieces: List[Piece]) -> List[Tuple[int, int, int]]:
        """
        生成所有可能的动作
        :return: [(piece_index, row, col), ...]
        """
        actions = []

        for piece_idx, piece in enumerate(pieces):
            placements = GameRules.get_legal_placements(board, piece)
            for row, col in placements:
                actions.append((piece_idx, row, col))

        # 按放置得分排序，优先评估高分动作（启发式剪枝）
        actions.sort(
            key=lambda a: len(pieces[a[0]].shape),
            reverse=True
        )

        return actions

    def find_best_sequence(self, board: Board, pieces: List[Piece]) -> List[Tuple[int, int, int]]:
        """
        找到当前轮次的最优放置序列（考虑所有3个积木的最优顺序）
        使用贪婪算法，每步选择当前最优
        :param board: 当前棋盘
        :param pieces: 当前可用的积木列表
        :return: [(piece_index, row, col), ...] 放置序列
        """
        start_time = time.time()
        sequence = []
        remaining_pieces = pieces.copy()
        current_board = board.copy()

        while remaining_pieces:
            # 找到当前最优动作
            best_action = None
            best_score = float('-inf')

            for piece_idx, piece in enumerate(remaining_pieces):
                placements = GameRules.get_legal_placements(current_board, piece)
                for row, col in placements:
                    self.nodes_explored += 1

                    if self.use_long_bar_strategy:
                        score = Evaluator.evaluate_with_long_bar_penalty(
                            current_board, piece, row, col
                        )
                    else:
                        score = Evaluator.evaluate_placement(current_board, piece, row, col)

                    if score > best_score:
                        best_score = score
                        best_action = (piece_idx, row, col)

            if best_action is None:
                # 没有可以放置的积木
                break

            # 添加到序列
            piece_idx, row, col = best_action
            piece = remaining_pieces[piece_idx]

            # 转换为原始索引
            original_idx = pieces.index(piece)
            sequence.append((original_idx, row, col))

            # 模拟放置
            current_board.place_piece(piece, row, col)
            cleared_rows, cleared_cols = current_board.find_cleared_lines()
            if cleared_rows or cleared_cols:
                current_board.clear_lines(cleared_rows, cleared_cols)

            # 从剩余积木中移除
            remaining_pieces.pop(piece_idx)

            # 检查时间限制
            elapsed = time.time() - start_time
            if elapsed > self.time_limit:
                break

        self.last_decision_time = time.time() - start_time
        return sequence

    def get_stats(self) -> Dict:
        """获取决策统计信息"""
        return {
            "decision_time": self.last_decision_time,
            "nodes_explored": self.nodes_explored
        }


if __name__ == "__main__":
    # 测试代码
    from src.game import Board, ALL_PIECES

    board = Board()
    # 放置一些积木
    board.place_piece(ALL_PIECES[5], 0, 0)  # 2x2
    board.place_piece(ALL_PIECES[3], 0, 2)  # 1x3_h

    print("当前棋盘:")
    print(board)

    # 模拟一轮的积木
    test_pieces = [ALL_PIECES[0], ALL_PIECES[10], ALL_PIECES[16]]  # 1x1, L_2x2_1, 1x4_h

    decision_maker = DecisionMaker()

    print(f"\n可用积木: {[p.name for p in test_pieces]}")
    print("寻找最优动作...")

    best_action = decision_maker.find_best_action(board, test_pieces)
    if best_action:
        piece_idx, row, col = best_action
        print(f"最优动作: 放置 {test_pieces[piece_idx].name} 到 ({row}, {col})")

    stats = decision_maker.get_stats()
    print(f"决策时间: {stats['decision_time']*1000:.2f}ms")
    print(f"探索节点数: {stats['nodes_explored']}")
