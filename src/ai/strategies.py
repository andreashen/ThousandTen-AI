"""
策略版本库
管理所有已实现的 AI 策略，支持版本号复现
"""

from typing import Dict, Any
from src.ai.decision import DecisionMaker
from src.ai.evaluator import Evaluator


# 策略版本配置
STRATEGIES = {
    "v1.0": {
        "name": "Baseline (Initial)",
        "description": "初始版本，基础评估函数",
        "evaluator_params": {},
        "decision_params": {"use_long_bar_strategy": False},
    },

    "v1.1": {
        "name": "Clear Focused",
        "description": "消行优先策略",
        "evaluator_params": {},
        "decision_params": {"use_long_bar_strategy": False},
    },

    "v1.2": {
        "name": "Clear Priority",
        "description": "Clear Priority + 序列评估",
        "evaluator_params": {},
        "decision_params": {"use_long_bar_strategy": False},
    },

    "v1.3": {
        "name": "Edge Bonus",
        "description": "Clear Priority + 边缘奖励",
        "evaluator_params": {},
        "decision_params": {"use_long_bar_strategy": False},
    },

    "v1.4": {
        "name": "Enhanced Weights",
        "description": "Enhanced Weights（当前最佳）",
        "evaluator_params": {},
        "decision_params": {"use_long_bar_strategy": False},
    },
}


class StrategyFactory:
    """策略工厂"""

    @staticmethod
    def create_decision_maker(version: str, time_limit: float = 1.0) -> DecisionMaker:
        """
        创建指定版本的决策器
        :param version: 策略版本号（如 "v1.0"）
        :param time_limit: 决策时间限制
        :return: DecisionMaker 实例
        """
        if version not in STRATEGIES:
            raise ValueError(f"未知策略版本: {version}，可用版本: {list(STRATEGIES.keys())}")

        params = STRATEGIES[version]["decision_params"].copy()
        params["time_limit"] = time_limit

        return DecisionMaker(**params)

    @staticmethod
    def get_strategy_info(version: str) -> Dict[str, Any]:
        """获取策略信息"""
        if version not in STRATEGIES:
            raise ValueError(f"未知策略版本: {version}")

        return STRATEGIES[version].copy()

    @staticmethod
    def list_strategies() -> Dict[str, str]:
        """列出所有策略"""
        return {v: STRATEGIES[v]["name"] for v in STRATEGIES}


if __name__ == "__main__":
    # 测试策略工厂
    print("可用策略:")
    for version, name in StrategyFactory.list_strategies().items():
        print(f"  {version}: {name}")

    print("\n创建 v1.4 决策器:")
    dm = StrategyFactory.create_decision_maker("v1.4")
    print(f"  创建成功: {type(dm).__name__}")
