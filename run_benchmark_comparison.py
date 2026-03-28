#!/usr/bin/env python3
"""
运行50种子策略对比测试
"""

import sys
import time
from src.ai.benchmark import run_multi_seed_benchmark, print_benchmark_report

# 生成50个固定种子（用于可复现）
SEEDS_50 = [
    42, 123, 456, 789, 101112,
    202223, 303334, 404445, 505556, 606667,
    707778, 808889, 909910, 111213, 141516,
    171819, 202122, 232425, 262728, 293031,
    323334, 353637, 383940, 414243, 444546,
    474849, 505152, 535455, 565758, 596061,
    626364, 656667, 686970, 717273, 747576,
    777879, 808182, 838485, 868788, 899091,
    929394, 959697, 9899100, 102103, 105106,
    108109, 111112, 114115
]

print("="*60)
print("50种子策略对比测试")
print("="*60)
print(f"种子列表: {SEEDS_50[:5]}... ({len(SEEDS_50)} 个)")
print()

# 测试所有策略版本
strategies_to_test = ["v1.0", "v1.2", "v1.4"]
all_results = {}

for strategy in strategies_to_test:
    print(f"\\n{'='*60}")
    print(f"测试策略: {strategy}")
    print(f"{'='*60}")
    print(f"开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    start = time.time()
    results = run_multi_seed_benchmark(SEEDS_50, strategy, time_limit=1.0)
    elapsed = time.time() - start

    all_results[strategy] = results

    print(f"完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"总耗时: {elapsed/60:.1f} 分钟")

    print_benchmark_report(results, strategy)

# 保存结果到文件
import json
with open("benchmark_results_50seeds.json", "w") as f:
    # 移除不可序列化的对象
    clean_results = {}
    for strategy, results in all_results.items():
        clean_results[strategy] = [
            {k: v for k, v in r.items() if k != "strategy"}
            for r in results
        ]
    json.dump(clean_results, f, indent=2)

print(f"\\n{'='*60}")
print("测试完成！结果已保存到 benchmark_results_50seeds.json")
print(f"{'='*60}")
