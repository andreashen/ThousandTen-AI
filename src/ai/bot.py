"""
AI Bot 主控模块
整合游戏引擎和 AI 决策系统，实现完整的 AI 玩家
"""

import time
from typing import List, Tuple, Optional, Dict
from src.game.engine import GameEngine
from src.game.board import Board
from src.game.pieces import Piece
from .decision import DecisionMaker
from .evaluator import Evaluator


class AIBot:
    """AI 游戏玩家"""

    def __init__(self, use_long_bar_strategy: bool = True, time_limit: float = 1.0):
        """
        初始化 AI Bot
        :param use_long_bar_strategy: 是否启用长条积木特殊策略
        :param time_limit: 单步决策时间限制（秒）
        """
        self.game = GameEngine()
        self.decision_maker = DecisionMaker(
            use_long_bar_strategy=use_long_bar_strategy,
            time_limit=time_limit
        )
        self.stats = {
            "total_moves": 0,
            "total_decision_time": 0.0,
            "max_decision_time": 0.0,
            "total_rounds": 0
        }

    def reset(self):
        """重置游戏"""
        self.game.reset()
        self.stats = {
            "total_moves": 0,
            "total_decision_time": 0.0,
            "max_decision_time": 0.0,
            "total_rounds": 0
        }

    def play_one_round(self) -> Tuple[bool, str]:
        """
        执行一轮游戏（放置所有可用积木）
        :return: (是否成功完成一轮, 状态信息)
        """
        if self.game.is_game_over():
            return False, "Game Over"

        self.stats["total_rounds"] += 1
        moves_made = 0

        while not self.game.is_game_over() and self.game.current_pieces:
            # AI 决策
            action = self.decision_maker.find_best_action(
                self.game.board,
                self.game.current_pieces
            )

            if action is None:
                # 没有合法动作
                return False, "No legal moves"

            piece_idx, row, col = action
            piece = self.game.current_pieces[piece_idx]

            # 执行放置
            self.game.place_piece(piece_idx, row, col)
            moves_made += 1
            self.stats["total_moves"] += 1

            # 更新统计
            decision_time = self.decision_maker.last_decision_time
            self.stats["total_decision_time"] += decision_time
            self.stats["max_decision_time"] = max(
                self.stats["max_decision_time"],
                decision_time
            )

        if moves_made > 0:
            return True, f"Placed {moves_made} pieces"
        else:
            return False, "No moves made"

    def play_full_game(self) -> int:
        """
        玩完整局游戏直到结束
        :return: 最终得分
        """
        self.reset()
        self.game.start_new_round()

        while not self.game.is_game_over():
            success, msg = self.play_one_round()
            if not success:
                break

        return self.game.get_score()

    def get_state(self) -> Dict:
        """获取游戏状态"""
        return {
            "score": self.game.get_score(),
            "round": self.game.round,
            "game_over": self.game.is_game_over(),
            "current_pieces": self.game.current_pieces.copy() if self.game.current_pieces else [],
            "board": self.game.board.copy(),
            "stats": self.stats.copy()
        }

    def make_one_move(self) -> Tuple[bool, Optional[Tuple[int, int, int]]]:
        """
        执行一步 AI 决策
        :return: (是否有动作执行, 动作详情)
        """
        if self.game.is_game_over():
            return False, None

        if not self.game.current_pieces:
            self.game.start_new_round()

        action = self.decision_maker.find_best_action(
            self.game.board,
            self.game.current_pieces
        )

        if action is None:
            return False, None

        piece_idx, row, col = action
        self.game.place_piece(piece_idx, row, col)

        # 更新统计
        decision_time = self.decision_maker.last_decision_time
        self.stats["total_decision_time"] += decision_time
        self.stats["max_decision_time"] = max(
            self.stats["max_decision_time"],
            decision_time
        )
        self.stats["total_moves"] += 1

        return True, action

    def get_performance_report(self) -> str:
        """获取性能报告"""
        avg_decision_time = (
            self.stats["total_decision_time"] / self.stats["total_moves"]
            if self.stats["total_moves"] > 0
            else 0
        )

        return f"""
=== AI Performance Report ===
Total Moves: {self.stats['total_moves']}
Total Rounds: {self.stats['total_rounds']}
Final Score: {self.game.get_score()}
Avg Decision Time: {avg_decision_time*1000:.2f}ms
Max Decision Time: {self.stats['max_decision_time']*1000:.2f}ms
Total Decision Time: {self.stats['total_decision_time']:.2f}s
=============================
"""


def run_benchmark(num_games: int = 10, time_limit: float = 1.0) -> Dict:
    """
    运行基准测试
    :param num_games: 游戏局数
    :param time_limit: 决策时间限制
    :return: 统计数据
    """
    scores = []
    decision_times = []

    for i in range(num_games):
        bot = AIBot(time_limit=time_limit)
        score = bot.play_full_game()

        state = bot.get_state()
        scores.append(score)
        avg_time = (
            state["stats"]["total_decision_time"] / state["stats"]["total_moves"]
            if state["stats"]["total_moves"] > 0
            else 0
        )
        decision_times.append(avg_time)

        print(f"Game {i+1}/{num_games}: Score = {score}, Avg Decision Time = {avg_time*1000:.2f}ms")

    return {
        "num_games": num_games,
        "avg_score": sum(scores) / len(scores),
        "max_score": max(scores),
        "min_score": min(scores),
        "avg_decision_time": sum(decision_times) / len(decision_times),
        "max_decision_time": max(decision_times),
        "scores": scores
    }


if __name__ == "__main__":
    # 运行测试游戏
    print("=== AI Bot Test ===\n")

    bot = AIBot()
    bot.game.start_new_round()

    print(f"初始状态 - Round: {bot.game.round}, Score: {bot.game.get_score()}")
    print(f"初始积木: {[p.name for p in bot.game.current_pieces]}\n")

    # 执行几步
    for i in range(5):
        if bot.game.is_game_over():
            print("Game Over!")
            break

        success, action = bot.make_one_move()
        if success:
            piece_idx, row, col = action
            print(f"Step {i+1}: 放置 {bot.game.current_pieces[piece_idx].name if piece_idx < len(bot.game.current_pieces) else 'N/A'} 到 ({row}, {col})")
        else:
            print(f"Step {i+1}: 无法放置")

    print(f"\n当前得分: {bot.game.get_score()}")
    print(bot.game.board)

    print(bot.get_performance_report())

    # 运行基准测试
    print("\n=== Running Benchmark ===")
    results = run_benchmark(num_games=5)
    print(f"\nBenchmark Results:")
    print(f"Average Score: {results['avg_score']:.2f}")
    print(f"Max Score: {results['max_score']}")
    print(f"Min Score: {results['min_score']}")
    print(f"Average Decision Time: {results['avg_decision_time']*1000:.2f}ms")
