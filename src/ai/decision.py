"""
AI 决策算法模块
策略：消行优先 + 序列评估（优化版）
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
        """找到当前最优的放置动作（消行优先策略）"""
        start_time = time.time()
        self.nodes_explored = 0

        # 生成所有动作并��类
        all_actions = self._generate_all_actions(board, pieces)
        if not all_actions:
            return None

        if len(all_actions) == 1:
            self.last_decision_time = time.time() - start_time
            return all_actions[0]

        # 分类：消行动作 vs 非消行动作
        clear_actions = []
        non_clear_actions = []

        for piece_idx, row, col in all_actions:
            self.nodes_explored += 1
            _, clear_bonus = GameRules.calculate_placement_score(
                board, pieces[piece_idx], row, col
            )
            score = evaluate_action(board, pieces, piece_idx, row, col)

            if clear_bonus > 0:
                clear_actions.append((piece_idx, row, col, score, clear_bonus))
            else:
                non_clear_actions.append((piece_idx, row, col, score))

        # 策略：如果有消行动作，选评分最高的
        if clear_actions:
            # 按 (score + clear_bonus * 200) 排序
            clear_actions.sort(key=lambda x: x[3] + x[4] * 200, reverse=True)
            best = clear_actions[0]
            self.last_decision_time = time.time() - start_time
            return (best[0], best[1], best[2])

        # 没有消行动作：对 top-10 候选进行序列评估
        non_clear_actions.sort(key=lambda x: x[3], reverse=True)

        best_action = (non_clear_actions[0][0], non_clear_actions[0][1], non_clear_actions[0][2])
        best_score = non_clear_actions[0][3]

        # 对 top-10 进行序列评估（但在时间限制内）
        max_candidates = min(10, len(non_clear_actions))
        for i in range(1, max_candidates):
            piece_idx, row, col, score = non_clear_actions[i]
            seq_score = self._evaluate_sequence(board, pieces, piece_idx, row, col)
            if seq_score > best_score:
                best_score = seq_score
                best_action = (piece_idx, row, col)

            elapsed = time.time() - start_time
            if elapsed > self.time_limit * 0.8:
                break

        self.last_decision_time = time.time() - start_time
        return best_action

    def _evaluate_sequence(
        self, board: Board, pieces: List[Piece],
        piece_idx: int, row: int, col: int
    ) -> float:
        """评估完整轮次的序列价值（轻量级）"""
        piece = pieces[piece_idx]

        # 模拟第一步
        new_board = GameRules.simulate_placement(board, piece, row, col)
        placement_score, clear_bonus = GameRules.calculate_placement_score(
            board, piece, row, col
        )

        # 快速评估剩余积木（只评估，不递归）
        remaining = [p for i, p in enumerate(pieces) if i != piece_idx]
        seq_score = 0.0
        total_clear = clear_bonus

        for _ in range(len(remaining)):
            best_score = None
            best_placement = None

            for pi, p in enumerate(remaining):
                placements = GameRules.get_legal_placements(new_board, p)
                if not placements:
                    continue

                for r, c in placements:
                    ps, cb = GameRules.calculate_placement_score(new_board, p, r, c)
                    future_board = GameRules.simulate_placement(new_board, p, r, c)
                    future_eval = Evaluator.evaluate_board_state(future_board)

                    # 综合评分
                    total = ps + cb * 150.0 + future_eval * 2.0

                    if best_score is None or total > best_score:
                        best_score = total
                        best_placement = (pi, ps, cb, future_board)

            if best_placement is None:
                break

            pi, ps, cb, future_board = best_placement
            seq_score += ps
            total_clear += cb
            new_board = future_board
            remaining.pop(pi)

        # 最终评估
        final_eval = Evaluator.evaluate_board_state(new_board)
        final_survivable = sum(
            1 for p in remaining
            if GameRules.get_legal_placements(new_board, p)
        )

        return (
            placement_score +
            seq_score +
            total_clear * 150.0 +
            final_eval * 2.0 +
            final_survivable * 15.0
        )

    def _generate_all_actions(self, board: Board, pieces: List[Piece]) -> List[Tuple[int, int, int]]:
        """生成所有可能的动作"""
        actions = []
        for piece_idx, piece in enumerate(pieces):
            placements = GameRules.get_legal_placements(board, piece)
            for row, col in placements:
                actions.append((piece_idx, row, col))
        return actions

    def find_best_sequence(self, board: Board, pieces: List[Piece]) -> List[Tuple[int, int, int]]:
        """找到当前轮次的最优放置序列"""
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
                    score = evaluate_action(
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
