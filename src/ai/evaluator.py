"""
AI 评估函数模块
设计启发式函数评估棋盘状态质量
"""

from typing import Set, Tuple, List
from src.game.board import Board
from src.game.pieces import Piece


class Evaluator:
    """棋盘评估器"""

    # 评估权重
    WEIGHT_EMPTY = 1.0           # 空格数量的权重
    WEIGHT_CLEAR_PROGRESS = 10.0  # 行/列清除进度的权重
    WEIGHT_CONNECTIVITY = 2.0    # 连通性权重
    WEIGHT_COMPACTNESS = 1.5    # 紧凑度权重
    WEIGHT_GAP_PENALTY = 3.0    # 孤立空格惩罚

    @staticmethod
    def evaluate(board: Board) -> float:
        """
        评估棋盘状态的总分数
        :param board: 棋盘对象
        :return: 评估分数（越高越好）
        """
        score = 0.0

        # 1. 空格数量（越多越好，表示有更多放置空间）
        score += Evaluator.get_empty_score(board) * Evaluator.WEIGHT_EMPTY

        # 2. 行/列清除进度（接近完成的行/列越多越好）
        score += Evaluator.get_clear_progress_score(board) * Evaluator.WEIGHT_CLEAR_PROGRESS

        # 3. 连通性（空格是否连通，避免孤立的小空隙）
        score += Evaluator.get_connectivity_score(board) * Evaluator.WEIGHT_CONNECTIVITY

        # 4. 紧凑度（积木是否紧凑分布）
        score += Evaluator.get_compactness_score(board) * Evaluator.WEIGHT_COMPACTNESS

        return score

    @staticmethod
    def get_empty_score(board: Board) -> float:
        """获取空格数量评分"""
        return float(board.get_empty_count())

    @staticmethod
    def get_clear_progress_score(board: Board) -> float:
        """
        获取行/列清除进度评分
        接近完成的行/列越多越好（8/10格比 5/10格好）
        """
        score = 0.0

        # 检查每行的完成度
        for row in range(board.size):
            filled = sum(board.grid[row][col] for col in range(board.size))
            if filled > 0:
                score += filled

        # 检查每列的完成度
        for col in range(board.size):
            filled = sum(board.grid[row][col] for row in range(board.size))
            if filled > 0:
                score += filled

        return score

    @staticmethod
    def get_connectivity_score(board: Board) -> float:
        """
        获取连通性评分
        使用 BFS 计算空格连通区域大小，奖励大面积连通区域
        """
        visited = [[False for _ in range(board.size)] for _ in range(board.size)]
        max_region = 0

        for row in range(board.size):
            for col in range(board.size):
                if board.grid[row][col] == 0 and not visited[row][col]:
                    # BFS 查找连通区域
                    region_size = Evaluator._bfs_region(board, visited, row, col)
                    max_region = max(max_region, region_size)

        # 奖励最大的连通区域
        return float(max_region)

    @staticmethod
    def _bfs_region(board: Board, visited: List[List[bool]], start_row: int, start_col: int) -> int:
        """BFS 计算连通区域大小"""
        from collections import deque
        queue = deque([(start_row, start_col)])
        visited[start_row][start_col] = True
        size = 0

        while queue:
            row, col = queue.popleft()
            size += 1

            # 4个方向
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = row + dr, col + dc
                if board.is_valid_position(nr, nc):
                    if board.grid[nr][nc] == 0 and not visited[nr][nc]:
                        visited[nr][nc] = True
                        queue.append((nr, nc))

        return size

    @staticmethod
    def get_compactness_score(board: Board) -> float:
        """
        获取紧凑度评分
        计算所有已填充格子的平均位置偏移，越集中越好
        """
        filled_cells = []
        for row in range(board.size):
            for col in range(board.size):
                if board.grid[row][col] == 1:
                    filled_cells.append((row, col))

        if not filled_cells:
            return 100.0  # 空棋盘最好

        # 计算中心点
        avg_row = sum(r for r, c in filled_cells) / len(filled_cells)
        avg_col = sum(c for r, c in filled_cells) / len(filled_cells)

        # 计算到中心点的平均距离（越小越紧凑）
        total_dist = sum(
            ((r - avg_row) ** 2 + (c - avg_col) ** 2) ** 0.5
            for r, c in filled_cells
        )
        avg_dist = total_dist / len(filled_cells)

        # 将距离转换为分数（距离越小分数越高）
        return 10.0 - avg_dist

    @staticmethod
    def evaluate_placement(board: Board, piece: Piece, row: int, col: int) -> float:
        """
        评估特定放置位置的价值
        综合考虑：立即得分、消除潜力、后续状态质量
        """
        from src.game.rules import GameRules

        # 计算立即得分
        placement_score, clear_bonus = GameRules.calculate_placement_score(board, piece, row, col)

        # 模拟放置后的棋盘
        new_board = GameRules.simulate_placement(board, piece, row, col)

        # 评估后续状态
        future_score = Evaluator.evaluate(new_board)

        # 综合评分
        total_score = (
            (placement_score + clear_bonus) * 1.0 +  # 立即得分的权重
            future_score * 0.8                        # 后续状态的权重
        )

        return total_score

    @staticmethod
    def evaluate_with_long_bar_penalty(board: Board, piece: Piece, row: int, col: int) -> float:
        """
        评估放置位置，考虑 1x4/1x5 长条积木的特殊处理
        如果当前放置的积木是长条，或者预估后续需要长条，给予额外考虑
        """
        base_score = Evaluator.evaluate_placement(board, piece, row, col)

        # 对长条积木（1x4, 1x5）的放置位置给予额外权重
        piece_name = piece.name
        if piece_name.startswith('1x4') or piece_name.startswith('1x5'):
            # 长条放置在边缘比中间更有价值（可以形成完整行/列）
            edge_bonus = 0
            cells = piece.get_cells(row, col)

            # 检查是否靠边
            for r, c in cells:
                if r == 0 or r == board.size - 1 or c == 0 or c == board.size - 1:
                    edge_bonus += 0.5

            base_score += edge_bonus * 0.1

        return base_score


if __name__ == "__main__":
    # 测试代码
    from src.game import Board, ALL_PIECES

    board = Board()
    board.place_piece(ALL_PIECES[5], 0, 0)  # 2x2

    print(f"当前评估分数: {Evaluator.evaluate(board):.2f}")
    print(f"空格得分: {Evaluator.get_empty_score(board):.2f}")
    print(f"清除进度得分: {Evaluator.get_clear_progress_score(board):.2f}")
    print(f"连通性得分: {Evaluator.get_connectivity_score(board):.2f}")
    print(f"紧凑度得分: {Evaluator.get_compactness_score(board):.2f}")
