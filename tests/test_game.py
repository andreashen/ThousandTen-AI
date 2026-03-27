"""
测试游戏核心逻辑
"""

import pytest
from src.game.board import Board
from src.game.pieces import Piece, ALL_PIECES, create_all_pieces
from src.game.rules import GameRules
from src.game.engine import GameEngine


class TestBoard:
    """测试棋盘类"""

    def test_init(self):
        """测试棋盘初始化"""
        board = Board()
        assert board.size == 10
        assert board.get_empty_count() == 100
        assert board.score == 0

    def test_can_place(self):
        """测试放置检测"""
        board = Board()
        piece = ALL_PIECES[0]  # 1x1

        assert board.can_place(piece, 0, 0)  # 空位置可以放置
        assert not board.can_place(piece, -1, 0)  # 越界不能放置
        assert not board.can_place(piece, 10, 0)  # 越界不能放置

    def test_place_piece(self):
        """测试放置积木"""
        board = Board()
        piece_2x2 = ALL_PIECES[5]  # 2x2

        assert board.place_piece(piece_2x2, 0, 0)  # 成功放置
        assert board.grid[0][0] == 1
        assert board.grid[0][1] == 1
        assert board.grid[1][0] == 1
        assert board.grid[1][1] == 1
        assert board.score == 4

    def test_clear_lines(self):
        """测试清除行/列"""
        board = Board()

        # 填满第一行
        for col in range(10):
            board.place_piece(ALL_PIECES[0], 0, col)  # 1x1 点块

        rows, cols = board.find_cleared_lines()
        assert 0 in rows

        bonus = board.clear_lines(rows, cols)
        assert bonus == 10  # 清除一行得 10 分
        assert board.get_empty_count() == 100  # 行被清除

    def test_game_over_detection(self):
        """测试游戏结束判定"""
        board = Board()
        pieces = [ALL_PIECES[5], ALL_PIECES[6]]  # 2x2, 3x3

        # 放置一些积木填满角落
        board.place_piece(ALL_PIECES[5], 0, 0)
        board.place_piece(ALL_PIECES[5], 0, 2)
        board.place_piece(ALL_PIECES[5], 0, 4)
        board.place_piece(ALL_PIECES[5], 0, 6)

        # 应该有可放置的位置
        can_place = GameRules.can_place_any(board, pieces)
        assert can_place is True


class TestPieces:
    """测试积木"""

    def test_all_pieces_created(self):
        """测试所有积木都被创建"""
        pieces = create_all_pieces()
        assert len(pieces) == 19  # 应该包含所有积木类型

        # 检查关键积木
        names = [p.name for p in pieces]
        assert "1x1" in names
        assert "1x4_h" in names
        assert "1x4_v" in names
        assert "1x5_h" in names
        assert "1x5_v" in names

    def test_piece_shape(self):
        """测试积木形状"""
        piece_1x1 = ALL_PIECES[0]
        assert len(piece_1x1.shape) == 1

        piece_2x2 = ALL_PIECES[5]
        assert len(piece_2x2.shape) == 4

        piece_3x3 = ALL_PIECES[6]
        assert len(piece_3x3.shape) == 9

    def test_get_cells(self):
        """测试获取积木格子"""
        piece = Piece("test", {(0, 0), (0, 1), (1, 0)}, 2, 2)
        cells = piece.get_cells(5, 5)
        assert (5, 5) in cells
        assert (5, 6) in cells
        assert (6, 5) in cells


class TestGameRules:
    """测试游戏规则"""

    def test_get_legal_placements(self):
        """测试获取合法放置位置"""
        board = Board()
        piece = ALL_PIECES[3]  # 1x3_h

        placements = GameRules.get_legal_placements(board, piece)
        assert len(placements) == 10 * 8  # 10x8 个可能位置

        # 放置一个积木后
        board.place_piece(ALL_PIECES[0], 0, 0)
        placements = GameRules.get_legal_placements(board, piece)
        assert len(placements) == 10 * 8 - 1  # 减少一个位置

    def test_simulate_placement(self):
        """测试模拟放置"""
        board = Board()
        piece = ALL_PIECES[3]  # 1x3_h

        new_board = GameRules.simulate_placement(board, piece, 0, 0)
        assert new_board.grid[0][0] == 1
        assert new_board.grid[0][1] == 1
        assert new_board.grid[0][2] == 1
        assert new_board.score == 3

    def test_calculate_placement_score(self):
        """测试得分计算"""
        board = Board()
        piece = ALL_PIECES[3]  # 1x3_h, 3 格

        placement_score, clear_bonus = GameRules.calculate_placement_score(board, piece, 0, 0)
        assert placement_score == 3
        assert clear_bonus == 0  # 没有行/列被填满


class TestGameEngine:
    """测试游戏引擎"""

    def test_init(self):
        """测试引擎初始化"""
        engine = GameEngine()
        assert engine.board.size == 10
        assert engine.game_over is False

    def test_generate_pieces(self):
        """测试积木生成"""
        engine = GameEngine()
        pieces = engine.generate_pieces()
        assert len(pieces) == 3

    def test_full_game_loop(self):
        """测试完整游戏循环"""
        engine = GameEngine()
        engine.start_new_round()

        move_count = 0
        while not engine.is_game_over() and move_count < 100:
            pieces = engine.current_pieces
            if not pieces:
                break

            # 找到第一个可放置的位置
            for idx, piece in enumerate(pieces):
                placements = GameRules.get_legal_placements(engine.board, piece)
                if placements:
                    row, col = placements[0]
                    engine.place_piece(idx, row, col)
                    move_count += 1
                    break
            else:
                break

        # 游戏应该正常结束或有合理的移动次数
        assert move_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
