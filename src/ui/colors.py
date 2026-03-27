"""
Pygame 颜色配置模块
"""

# 基础颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)

# 棋盘颜色
BOARD_EMPTY = (240, 240, 240)
BOARD_FILLED = (50, 100, 200)
BOARD_GRID = (180, 180, 180)
BOARD_HIGHLIGHT = (100, 200, 100)

# 积木颜色（不同积木类型用不同颜色）
PIECE_COLORS = {
    # 基础积木
    "1x1": (255, 200, 100),    # 黄色
    "1x2_h": (255, 150, 100),  # 橙色
    "1x2_v": (255, 150, 100),
    "1x3_h": (255, 100, 100),  # 红色
    "1x3_v": (255, 100, 100),
    "2x2": (200, 100, 200),     # 紫色
    "3x3": (150, 100, 200),     # 深紫色

    # L 形积木
    "L_2x2_1": (100, 200, 150),  # 青绿色
    "L_2x2_2": (100, 200, 150),
    "L_2x2_3": (100, 200, 150),
    "L_2x2_4": (100, 200, 150),
    "L_3x3_1": (100, 180, 200),  # 浅蓝色
    "L_3x3_2": (100, 180, 200),
    "L_3x3_3": (100, 180, 200),
    "L_3x3_4": (100, 180, 200),

    # 长条积木
    "1x4_h": (150, 200, 100),    # 浅绿色
    "1x4_v": (150, 200, 100),
    "1x5_h": (100, 180, 100),    # 绿色
    "1x5_v": (100, 180, 100),
}

# 文本颜色
TEXT_COLOR = (50, 50, 50)
SCORE_COLOR = (0, 100, 200)

# 按钮颜色
BUTTON_BG = (60, 120, 200)
BUTTON_HOVER = (80, 140, 220)
BUTTON_TEXT = WHITE


def get_piece_color(piece_name: str) -> tuple:
    """获取积木对应的颜色"""
    # 尝试精确匹配
    if piece_name in PIECE_COLORS:
        return PIECE_COLORS[piece_name]

    # 尝试前缀匹配
    for key, color in PIECE_COLORS.items():
        if piece_name.startswith(key.split('_')[0]):
            return color

    # 默认颜色
    return (150, 150, 150)
