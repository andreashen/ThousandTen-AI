"""
测试 AI 模块
"""

import pytest
from src.game.board import Board
from src.game.pieces import ALL_PIECES
from src.game.rules import GameRules
from src.ai.evaluator import Evaluator
from src.ai.decision import DecisionMaker
from src.ai.bot import AIBot, run_benchmark


class TestEvaluator:
    """测试评估器"""

    def test_empty_score(self):
        """测试空格评分"""
        board = Board()
        score = Evaluator.get_empty_score(board)
        assert score == 100.0

    def test_clear_progress_score(self):
        """测试清除进度评分"""
        board = Board()
        # 放置一些积木
        board.place_piece(ALL_PIECES[0], 0, 0)
        board.place_piece(ALL_PIECES[0], 0, 1)

        score = Evaluator.get_clear_progress_score(board)
        assert score > 0

    def test_evaluate(self):
        """测试综合评估"""
        board = Board()
        score = Evaluator.evaluate(board)
        assert score > 0

    def test_evaluate_placement(self):
        """测试放置评估"""
        board = Board()
        piece = ALL_PIECES[0]  # 1x1

        score = Evaluator.evaluate_placement(board, piece, 0, 0)
        assert score > 0


class TestDecisionMaker:
    """测试决策器"""

    def test_init(self):
        """测试决策器初始化"""
        maker = DecisionMaker()
        assert maker.use_long_bar_strategy is True
        assert maker.time_limit == 1.0

    def test_find_best_action(self):
        """测试寻找最优动作"""
        board = Board()
        pieces = [ALL_PIECES[0], ALL_PIECES[5], ALL_PIECES[16]]  # 1x1, 2x2, 1x4_h

        maker = DecisionMaker()
        action = maker.find_best_action(board, pieces)

        assert action is not None
        piece_idx, row, col = action
        assert 0 <= piece_idx < len(pieces)
        assert board.can_place(pieces[piece_idx], row, col)

    def test_find_best_sequence(self):
        """测试寻找最优序列"""
        board = Board()
        pieces = [ALL_PIECES[0], ALL_PIECES[5]]  # 1x1, 2x2

        maker = DecisionMaker()
        sequence = maker.find_best_sequence(board, pieces)

        assert len(sequence) > 0
        # 验证序列中的动作都是合法的
        for piece_idx, row, col in sequence:
            assert board.can_place(pieces[piece_idx], row, col)


class TestAIBot:
    """测试 AI Bot"""

    def test_init(self):
        """测试 Bot 初始化"""
        bot = AIBot()
        assert bot.game is not None
        assert bot.decision_maker is not None

    def test_make_one_move(self):
        """测试执行一步"""
        bot = AIBot()
        bot.game.start_new_round()

        success, action = bot.make_one_move()
        assert success is True
        assert action is not None

    def test_play_one_round(self):
        """测试执行一轮"""
        bot = AIBot()
        bot.game.start_new_round()

        success, msg = bot.play_one_round()
        assert success is True

    def test_play_full_game(self):
        """测试完整游戏"""
        bot = AIBot()
        score = bot.play_full_game()
        assert score >= 0
        assert bot.game.is_game_over() is True

    def test_reset(self):
        """测试重置"""
        bot = AIBot()
        bot.game.start_new_round()
        bot.make_one_move()

        bot.reset()
        assert bot.game.get_score() == 0
        assert bot.stats["total_moves"] == 0


class TestBenchmark:
    """测试基准测试"""

    def test_run_benchmark(self):
        """测试运行基准测试"""
        results = run_benchmark(num_games=3)

        assert results["num_games"] == 3
        assert results["avg_score"] >= 0
        assert results["max_score"] >= results["min_score"]
        assert len(results["scores"]) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
