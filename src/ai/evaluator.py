"""
AI 评估函数模块
核心策略：消行/列是得分的唯一途径
启发式设计围绕「创造更多消行机会 + 保持棋盘可生存性」
"""

from typing import Set, Tuple, List
from src.game.board import Board
from src.game.pieces import Piece


class Evaluator:
    """棋盘评估器"""

    # === 权重参数 ===
    WEIGHT_EMPTY = 3.0
    WEIGHT_CLEAR_PROGRESS = 10.0  # 接近完成的行/列
    WEIGHT_GAP_PENALTY = 5.0
    WEIGHT_COMPACTNESS = 0.3
    WEIGHT_EDGE = 0.5

    @staticmethod
    def evaluate(board: Board) -> float:
        return Evaluator.evaluate_board_state(board)

    @staticmethod
    def evaluate_board_state(board: Board) -> float:
        score = 0.0

        # 1. 空格数量（生存空间）
        score += board.get_empty_count() * Evaluator.WEIGHT_EMPTY

        # 2. 消行潜力（接近完成的行/列越多越好）
        score += Evaluator._get_clear_potential(board) * Evaluator.WEIGHT_CLEAR_PROGRESS

        # 3. 孤立空格惩罚
        score -= Evaluator._get_isolated_gap_count(board) * Evaluator.WEIGHT_GAP_PENALTY

        # 4. 紧凑度
        score += Evaluator._get_compactness(board) * Evaluator.WEIGHT_COMPACTNESS

        # 5. 边缘占用
        score += Evaluator._get_edge_score(board) * Evaluator.WEIGHT_EDGE

        return score

    @staticmethod
    def _get_clear_potential(board: Board) -> float:
        """计算消行潜力（接近完成的行/列）"""
        score = 0.0
        for row in range(board.size):
            filled = sum(board.grid[row][col] for col in range(board.size))
            if filled >= 7:
                # 7格=1分, 8格=4分, 9格=9分 (指数增长，鼓励填满)
                score += (filled - 6) ** 2
        for col in range(board.size):
            filled = sum(board.grid[row][col] for row in range(board.size))
            if filled >= 7:
                score += (filled - 6) ** 2
        return score

    @staticmethod
    def _get_isolated_gap_count(board: Board) -> float:
        count = 0
        for row in range(board.size):
            for col in range(board.size):
                if board.grid[row][col] == 0 and Evaluator._is_isolated(board, row, col):
                    count += 1
        return float(count)

    @staticmethod
    def _is_isolated(board: Board, row: int, col: int) -> bool:
        up = row > 0 and board.grid[row - 1][col] == 1
        down = row < board.size - 1 and board.grid[row + 1][col] == 1
        left = col > 0 and board.grid[row][col - 1] == 1
        right = col < board.size - 1 and board.grid[row][col + 1] == 1
        return sum([up, down, left, right]) >= 3

    @staticmethod
    def _get_compactness(board: Board) -> float:
        filled = [(r, c) for r in range(board.size)
                 for c in range(board.size) if board.grid[r][c] == 1]
        if len(filled) <= 1:
            return 10.0
        rows = [r for r, _ in filled]
        cols = [c for _, c in filled]
        import statistics
        spread = statistics.stdev(rows) + statistics.stdev(cols) if len(filled) > 1 else 0
        return max(0, 10.0 - spread)

    @staticmethod
    def _get_edge_score(board: Board) -> float:
        score = 0.0
        for row in range(board.size):
            for col in range(board.size):
                if board.grid[row][col] == 1:
                    if row == 0 or row == board.size - 1:
                        score += 0.5
                    if col == 0 or col == board.size - 1:
                        score += 0.5
        return score


def evaluate_action(board: Board, pieces: List[Piece],
                    piece_idx: int, row: int, col: int,
                    lookahead_depth: int = 0) -> float:
    """
    评估放置动作的价值
    核心：消行奖励 + 未来状态 + 生存能力
    """
    from src.game.rules import GameRules

    piece = pieces[piece_idx]

    # 1. 立即得分
    placement_score, clear_bonus = GameRules.calculate_placement_score(
        board, piece, row, col
    )

    # 2. 模拟放置后的棋盘
    new_board = GameRules.simulate_placement(board, piece, row, col)

    # 3. 评估后续棋盘状态
    future_eval = Evaluator.evaluate_board_state(new_board)

    # 4. 剩余积木的生存能力
    remaining = [p for i, p in enumerate(pieces) if i != piece_idx]
    survivable = sum(
        1 for p in remaining
        if GameRules.get_legal_placements(new_board, p)
    )

    # 5. 消行奖励（核心！）
    if clear_bonus > 0:
        clear_score = clear_bonus * 100.0  # 消行=立即+800分
    else:
        clear_score = 0.0

    # 6. 接近完成的行/列奖励（引导AI主动创造消行机会）
    near_complete_bonus = Evaluator._get_clear_potential(board)  # 放置前的接近完成度
    future_near_complete = Evaluator._get_clear_potential(new_board)  # 放置后
    clear_progress_bonus = (future_near_complete - near_complete_bonus) * 20.0

    # 7. 检查是否会「阻塞」接近完成的行/列（惩罚！）
    block_penalty = _calculate_block_penalty(board, new_board, piece, row, col)

    total = (
        placement_score * 1.0 +
        future_eval * 1.5 +
        clear_score +
        clear_progress_bonus +
        survivable * 10.0 -
        block_penalty
    )

    return total


def _calculate_block_penalty(board: Board, new_board: Board,
                              piece: Piece, row: int, col: int) -> float:
    """
    计算放置是否「阻塞」了接近完成的行/列
    如果放置前某行/列接近完成，但放置后变得更难完成，则惩罚
    """
    penalty = 0.0

    cells = piece.get_cells(row, col)

    # 检查放置前的行/列完成度
    for r, c in cells:
        # 检查该行
        filled_before = sum(board.grid[r][col] for col in range(board.size))
        filled_after = sum(new_board.grid[r][col] for col in range(board.size))
        if 7 <= filled_before <= 9 and filled_after < filled_before:
            # 放置阻塞了接近完成的行
            penalty += (filled_before - filled_after) * 5.0

        # 检查该列
        filled_before = sum(board.grid[row][c] for row in range(board.size))
        filled_after = sum(new_board.grid[row][c] for row in range(board.size))
        if 7 <= filled_before <= 9 and filled_after < filled_before:
            penalty += (filled_before - filled_after) * 5.0

    return penalty


if __name__ == "__main__":
    from src.game import Board, ALL_PIECES
    board = Board()
    board.place_piece(ALL_PIECES[5], 0, 0)
    print(f"Board eval: {Evaluator.evaluate_board_state(board):.2f}")
