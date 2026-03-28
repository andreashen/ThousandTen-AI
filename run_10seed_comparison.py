#!/usr/bin/env python3
"""
简化的种子对比测试
使用10个种子快速验证策略对比
"""

import sys
import time
import json
from src.ai.benchmark import run_multi_seed_benchmark, print_benchmark_report

# 10个固定种子（用于快速验证）
SEEDS_10 = [42, 123, 456, 789, 101112, 202223, 303334, 404445, 505556, 606667]

print("="*70)
print("10种子策略对比测试（验证版）")
print("="*70)
print(f"种子列表: {SEEDS_10}")
print()

# 测试策略版本
strategies_to_test = ["v1.0", "v1.2", "v1.4"]
all_results = {}

for strategy in strategies_to_test:
    print(f"\n{'='*70}")
    print(f"测试策略: {strategy}")
    print(f"{'='*70}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    start = time.time()

    try:
        results = run_multi_seed_benchmark(SEEDS_10, strategy, time_limit=1.0)
        elapsed = time.time() - start

        all_results[strategy] = results

        print(f"完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {elapsed/60:.1f} 分钟")

        print_benchmark_report(results, strategy)

        # 显示每局详情
        print(f"\n详细结果:")
        for r in results:
            print(f"  种子 {r['seed']:6d}: 得分 {r['score']:5d}, 消行 {r['clears']:3d} 次, 轮次 {r['rounds']:3d}")

    except Exception as e:
        print(f"策略 {strategy} 测试失败: {e}")
        import traceback
        traceback.print_exc()

# 对比分析
print(f"\n{'='*70}")
print("策略对比分析")
print(f"{'='*70}")

for strategy in strategies_to_test:
    if strategy in all_results:
        scores = [r["score"] for r in all_results[strategy]]
        print(f"{strategy}: {sum(scores)/len(scores):.1f} 平均分")
    else:
        print(f"{strategy}: 测试失败")

# 保存结果
if all_results:
    with open("benchmark_results_10seeds.json", "w") as f:
        clean_results = {}
        for strategy, results in all_results.items():
            clean_results[strategy] = results
        json.dump(clean_results, f, indent=2)

    print(f"\n{'='*70}")
    print("测试完成！结果已保存到 benchmark_results_10seeds.json")
    print(f"{'='*70}")

print("\n所有任务完成！")
