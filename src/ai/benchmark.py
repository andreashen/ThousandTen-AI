"""
可复现的评测基准系统
使用固定随机种子生成确定的积木序列
"""

import random
import time
from typing import List, Dict
from src.ai.bot import AIBot


class SeededBenchmark:
    """基于种子的可复现基准测试"""

    def __init__(self, seed: int):
        """
        初始化基准测试
        :param seed: 随机种子
        """
        self.seed = seed
        self.rng = random.Random(seed)

    def run_benchmark(self) -> Dict:
        """
        运行单局基准测试
        :return: 游戏统计字典
        """
        bot = AIBot()
        bot.game.reset()

        # 使用种子初始化随机数生成器
        import src.game.engine as engine_module
        original_random = engine_module.random
        engine_module.random = self.rng

        bot.game.start_new_round()

        total_clears = 0
        start_time = time.time()
        total_moves = 0

        while not bot.game.is_game_over():
            action = bot.decision_maker.find_best_action(
                bot.game.board,
                bot.game.current_pieces
            )

            if action is None:
                break

            piece_idx, row, col = action
            piece = bot.game.current_pieces[piece_idx]

            old_score = bot.game.get_score()
            bot.game.place_piece(piece_idx, row, col)
            new_score = bot.game.get_score()

            actual_clear = new_score - old_score - len(piece.shape)
            if actual_clear > 0:
                total_clears += actual_clear // 10

            total_moves += 1

        elapsed = time.time() - start_time

        # 恢复原始随机数生成器
        engine_module.random = original_random

        return {
            "seed": self.seed,
            "score": bot.game.get_score(),
            "clears": total_clears,
            "rounds": bot.game.round,
            "moves": total_moves,
            "time": elapsed
        }

    def run_benchmark_with_decision_maker(self, decision_maker) -> Dict:
        """
        使用指定决策器运行基准测试
        :param decision_maker: DecisionMaker 实例
        :return: 游戏统计字典
        """
        from src.game.engine import GameEngine
        from src.game.pieces import ALL_PIECES

        engine = GameEngine()

        # 使用种子初始化随机数生成器
        import src.game.engine as engine_module
        original_random = engine_module.random
        engine_module.random = self.rng

        engine.start_new_round()

        total_clears = 0
        start_time = time.time()
        total_moves = 0

        while not engine.is_game_over():
            action = decision_maker.find_best_action(
                engine.board,
                engine.current_pieces
            )

            if action is None:
                break

            piece_idx, row, col = action
            piece = engine.current_pieces[piece_idx]

            old_score = engine.get_score()
            engine.place_piece(piece_idx, row, col)
            new_score = engine.get_score()

            actual_clear = new_score - old_score - len(piece.shape)
            if actual_clear > 0:
                total_clears += actual_clear // 10

            total_moves += 1

        elapsed = time.time() - start_time

        # 恢复原始随机数生成器
        engine_module.random = original_random

        return {
            "seed": self.seed,
            "score": engine.get_score(),
            "clears": total_clears,
            "rounds": engine.round,
            "moves": total_moves,
            "time": elapsed
        }


def run_multi_seed_benchmark(
    seeds: List[int],
    strategy_version: str = "v1.4",
    time_limit: float = 1.0
) -> List[Dict]:
    """
    多种子基准测试
    :param seeds: 种子列表
    :param strategy_version: 策略版本号
    :param time_limit: 决策时间限制
    :return: 结果列表
    """
    from .strategies import StrategyFactory

    results = []
    strategy_name = StrategyFactory.get_strategy_info(strategy_version)["name"]

    for i, seed in enumerate(seeds):
        # 创建指定版本的 Bot
        dm = StrategyFactory.create_decision_maker(strategy_version, time_limit)

        benchmark = SeededBenchmark(seed)
        result = benchmark.run_benchmark_with_decision_maker(dm)
        result["strategy"] = strategy_name
        result["strategy_version"] = strategy_version
        results.append(result)

        if (i + 1) % 10 == 0:
            print(f"  完成 {i+1}/{len(seeds)}...")

    return results


def print_benchmark_report(results: List[Dict], strategy_name: str):
    """打印基准测试报告"""
    import statistics

    scores = [r["score"] for r in results]
    clears = [r["clears"] for r in results]
    times = [r["time"] for r in results]

    print(f"\n=== {strategy_name} ===")
    print(f"种子数: {len(results)}")
    print(f"平均分: {statistics.mean(scores):.1f}")
    print(f"中位数: {statistics.median(scores):.1f}")
    print(f"最高分: {max(scores)}")
    print(f"最低分: {min(scores)}")
    print(f"标准差: {statistics.stdev(scores):.1f}")
    print(f"平均消行: {statistics.mean(clears):.1f}")
    print(f"得分/消行比: {statistics.mean(scores) / statistics.mean(clears):.1f}")
    print(f"平均时间: {statistics.mean(times):.2f}s")


if __name__ == "__main__":
    # 测试种子机制
    test_seeds = [42, 123, 456, 789, 101112]

    print("运行种子基准测试...")
    results = run_multi_seed_benchmark(test_seeds, "Enhanced Weights v5")
    print_benchmark_report(results, "Enhanced Weights v5")
