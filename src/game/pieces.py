"""
积木定义模块
定义所有积木类型及其形状
"""

from typing import List, Tuple, Set
from dataclasses import dataclass


@dataclass
class Piece:
    """积木类"""
    name: str
    shape: Set[Tuple[int, int]]  # 相对坐标集合，例如 {(0,0), (0,1), (1,0)}
    width: int
    height: int

    def __post_init__(self):
        """计算积木尺寸"""
        if not self.shape:
            raise ValueError("Piece shape cannot be empty")
        xs = [x for x, y in self.shape]
        ys = [y for x, y in self.shape]
        self.width = max(xs) - min(xs) + 1
        self.height = max(ys) - min(ys) + 1

    def get_cells(self, start_row: int, start_col: int) -> Set[Tuple[int, int]]:
        """获取积木放置在指定位置后的所有格子坐标"""
        return {(start_row + dr, start_col + dc) for dr, dc in self.shape}


def create_all_pieces() -> List[Piece]:
    """创建所有积木类型"""
    pieces = []

    # 1x1 点块
    pieces.append(Piece("1x1", {(0, 0)}, 1, 1))

    # 1x2 直线块（横向、纵向）
    pieces.append(Piece("1x2_h", {(0, 0), (0, 1)}, 1, 2))
    pieces.append(Piece("1x2_v", {(0, 0), (1, 0)}, 2, 1))

    # 1x3 直线块（横向、纵向）
    pieces.append(Piece("1x3_h", {(0, 0), (0, 1), (0, 2)}, 1, 3))
    pieces.append(Piece("1x3_v", {(0, 0), (1, 0), (2, 0)}, 3, 1))

    # 2x2 正方形块
    pieces.append(Piece("2x2", {(0, 0), (0, 1), (1, 0), (1, 1)}, 2, 2))

    # 3x3 正方形块
    pieces.append(Piece("3x3", {
        (0, 0), (0, 1), (0, 2),
        (1, 0), (1, 1), (1, 2),
        (2, 0), (2, 1), (2, 2)
    }, 3, 3))

    # L 形块（2x2 变体）
    pieces.append(Piece("L_2x2_1", {(0, 0), (1, 0), (1, 1)}, 2, 2))
    pieces.append(Piece("L_2x2_2", {(0, 0), (0, 1), (1, 0)}, 2, 2))
    pieces.append(Piece("L_2x2_3", {(0, 1), (1, 0), (1, 1)}, 2, 2))
    pieces.append(Piece("L_2x2_4", {(0, 0), (0, 1), (1, 1)}, 2, 2))

    # L 形块（3x3 变体）
    pieces.append(Piece("L_3x3_1", {(0, 0), (1, 0), (2, 0), (2, 1)}, 3, 2))
    pieces.append(Piece("L_3x3_2", {(0, 0), (1, 0), (2, 0), (2, -1)}, 3, 2))
    pieces.append(Piece("L_3x3_3", {(0, 0), (0, 1), (1, 0), (2, 0)}, 3, 2))
    pieces.append(Piece("L_3x3_4", {(0, 0), (0, 1), (0, 2), (1, 0)}, 2, 3))

    # 1x4 长条块（横向、纵向）
    pieces.append(Piece("1x4_h", {(0, 0), (0, 1), (0, 2), (0, 3)}, 1, 4))
    pieces.append(Piece("1x4_v", {(0, 0), (1, 0), (2, 0), (3, 0)}, 4, 1))

    # 1x5 长条块（横向、纵向）
    pieces.append(Piece("1x5_h", {(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)}, 1, 5))
    pieces.append(Piece("1x5_v", {(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)}, 5, 1))

    return pieces


# 全局积木库
ALL_PIECES = create_all_pieces()

if __name__ == "__main__":
    # 测试代码
    print(f"总共有 {len(ALL_PIECES)} 种积木类型")
    for piece in ALL_PIECES:
        print(f"{piece.name}: {piece.width}x{piece.height}, {len(piece.shape)} 格")
