"""
Pygame 可视化界面模块
实现 10x10 棋盘绘制、积木展示、AI 决策过程可视化
"""

import pygame
import sys
from typing import Optional, List, Tuple
from src.game.board import Board
from src.game.pieces import Piece
from src.ai.bot import AIBot
from .colors import *


class PygameView:
    """Pygame 可视化视图"""

    # 窗口配置
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 700
    BOARD_SIZE = 400  # 棋盘区域大小
    CELL_SIZE = BOARD_SIZE // 10

    # 布局配置
    BOARD_X = 50
    BOARD_Y = 100
    PIECE_AREA_X = 500
    PIECE_AREA_Y = 100
    PIECE_SIZE = 30  # 备选区积木格子大小

    def __init__(self):
        """初始化 Pygame"""
        pygame.init()
        pygame.display.set_caption("ThousandTen AI")

        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 22)

        # 颜色
        self.bg_color = WHITE

        # 按钮
        self.buttons = {
            "next_move": pygame.Rect(50, 520, 150, 50),
            "auto_play": pygame.Rect(220, 520, 150, 50),
            "new_game": pygame.Rect(390, 520, 150, 50),
            "quit": pygame.Rect(560, 520, 150, 50),
        }

        # 状态
        self.bot: Optional[AIBot] = None
        self.last_action: Optional[Tuple[int, int, int]] = None
        self.auto_play = False
        self.game_over = False

    def init_game(self):
        """初始化游戏"""
        self.bot = AIBot()
        self.bot.game.start_new_round()
        self.game_over = False
        self.auto_play = False
        self.last_action = None

    def draw_board(self, board: Board, highlight_cells: Optional[set] = None):
        """绘制棋盘"""
        if highlight_cells is None:
            highlight_cells = set()

        # 棋盘背景
        board_rect = pygame.Rect(
            self.BOARD_X, self.BOARD_Y,
            self.BOARD_SIZE, self.BOARD_SIZE
        )
        pygame.draw.rect(self.screen, BOARD_EMPTY, board_rect)
        pygame.draw.rect(self.screen, BOARD_GRID, board_rect, 2)

        # 绘制每个格子
        for row in range(board.size):
            for col in range(board.size):
                cell_rect = pygame.Rect(
                    self.BOARD_X + col * self.CELL_SIZE,
                    self.BOARD_Y + row * self.CELL_SIZE,
                    self.CELL_SIZE, self.CELL_SIZE
                )

                # 填充格子
                if board.grid[row][col] == 1:
                    pygame.draw.rect(self.screen, BOARD_FILLED, cell_rect)

                # 高亮显示
                if (row, col) in highlight_cells:
                    highlight_color = (*BOARD_HIGHLIGHT, 128)
                    s = pygame.Surface((self.CELL_SIZE, self.CELL_SIZE), pygame.SRCALPHA)
                    s.fill(highlight_color)
                    self.screen.blit(s, cell_rect.topleft)

                # 网格线
                pygame.draw.rect(self.screen, BOARD_GRID, cell_rect, 1)

    def draw_piece_preview(self, piece: Piece, x: int, y: int, cell_size: int, selected: bool = False):
        """绘制积木预览"""
        color = get_piece_color(piece.name)

        # 找到积木的边界
        min_r = min(r for r, c in piece.shape)
        max_r = max(r for r, c in piece.shape)
        min_c = min(c for r, c in piece.shape)
        max_c = max(c for r, c in piece.shape)

        # 计算偏移，使积木左上角对齐
        offset_r = min_r
        offset_c = min_c

        for r, c in piece.shape:
            cell_rect = pygame.Rect(
                x + (c - offset_c) * cell_size,
                y + (r - offset_r) * cell_size,
                cell_size - 1, cell_size - 1
            )
            pygame.draw.rect(self.screen, color, cell_rect)
            pygame.draw.rect(self.screen, BLACK, cell_rect, 1)

    def draw_pieces_area(self, pieces: List[Piece], selected_idx: int = -1):
        """绘制备选区积木"""
        if not pieces:
            return

        # 标题
        title = self.font.render("Reserve Pieces", True, TEXT_COLOR)
        self.screen.blit(title, (self.PIECE_AREA_X, self.PIECE_AREA_Y - 35))

        # 绘制每个积木
        piece_height = 80
        for idx, piece in enumerate(pieces):
            y = self.PIECE_AREA_Y + idx * piece_height

            # 积木名称
            name_text = self.font_small.render(piece.name, True, TEXT_COLOR)
            self.screen.blit(name_text, (self.PIECE_AREA_X, y))

            # 绘制积木形状
            self.draw_piece_preview(piece, self.PIECE_AREA_X, y + 25, self.PIECE_SIZE)

            # 选中效果
            if idx == selected_idx:
                pygame.draw.rect(
                    self.screen, BOARD_HIGHLIGHT,
                    (self.PIECE_AREA_X - 5, y - 5, 200, 75), 2
                )

    def draw_info(self, score: int, round_num: int, decision_time: float = 0):
        """绘制信息面板"""
        # 分数
        score_text = self.font_large.render(f"Score: {score}", True, SCORE_COLOR)
        self.screen.blit(score_text, (50, 30))

        # 回合
        round_text = self.font.render(f"Round: {round_num}", True, TEXT_COLOR)
        self.screen.blit(round_text, (300, 35))

        # 决策时间
        if decision_time > 0:
            time_text = self.font_small.render(
                f"Decision: {decision_time*1000:.1f}ms", True, TEXT_COLOR
            )
            self.screen.blit(time_text, (500, 35))

    def draw_buttons(self):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()

        button_texts = {
            "next_move": "Next Move",
            "auto_play": "Auto Play" if not self.auto_play else "Pause",
            "new_game": "New Game",
            "quit": "Quit"
        }

        for key, rect in self.buttons.items():
            # 鼠标悬停效果
            color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else BUTTON_BG

            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=8)

            # 按钮文字
            text = self.font.render(button_texts[key], True, BUTTON_TEXT)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    def draw_game_over(self, final_score: int):
        """绘制游戏结束画面"""
        # 半透明遮罩
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # 游戏结束文字
        game_over_text = self.font_large.render("GAME OVER", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(self.WINDOW_WIDTH // 2, 300))
        self.screen.blit(game_over_text, game_over_rect)

        # 最终得分
        score_text = self.font_large.render(f"Final Score: {final_score}", True, SCORE_COLOR)
        score_rect = score_text.get_rect(center=(self.WINDOW_WIDTH // 2, 360))
        self.screen.blit(score_text, score_rect)

    def draw_last_action(self):
        """绘制最后一步动作信息"""
        if self.last_action is None or self.bot is None:
            return

        piece_idx, row, col = self.last_action
        pieces = self.bot.game.current_pieces + [None]  # 放置后可能被移除

        # 如果有剩余积木
        if piece_idx < len(self.bot.game.current_pieces):
            piece_name = self.bot.game.current_pieces[piece_idx].name
        else:
            piece_name = f"Piece at ({row}, {col})"

        info_text = self.font_small.render(
            f"Last: {piece_name} -> ({row}, {col})",
            True, TEXT_COLOR
        )
        self.screen.blit(info_text, (50, 585))

    def handle_events(self) -> bool:
        """处理事件，返回是否继续运行"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                # 检查按钮点击
                if self.buttons["next_move"].collidepoint(mouse_pos):
                    self.do_next_move()
                elif self.buttons["auto_play"].collidepoint(mouse_pos):
                    self.auto_play = not self.auto_play
                elif self.buttons["new_game"].collidepoint(mouse_pos):
                    self.init_game()
                elif self.buttons["quit"].collidepoint(mouse_pos):
                    return False

        return True

    def do_next_move(self):
        """执行下一步"""
        if self.bot is None or self.game_over:
            return

        if not self.bot.game.current_pieces:
            self.bot.game.start_new_round()

        success, action = self.bot.make_one_move()
        if success:
            self.last_action = action
        else:
            self.game_over = True

    def render(self):
        """渲染画面"""
        # 清屏
        self.screen.fill(self.bg_color)

        if self.bot is None:
            self.init_game()

        # 绘制棋盘
        highlight = set()
        if self.last_action:
            piece_idx, row, col = self.last_action
            # 获取放置的格子用于高亮
            pieces = self.bot.game.current_pieces
            # 上一步放置的积木位置可能已经被清除，这里简化处理

        self.draw_board(self.bot.game.board, highlight)

        # 绘制备选区积木
        self.draw_pieces_area(self.bot.game.current_pieces)

        # 绘制信息
        stats = self.bot.bot.stats
        avg_time = (
            stats["total_decision_time"] / stats["total_moves"]
            if stats["total_moves"] > 0 else 0
        )
        self.draw_info(
            self.bot.game.get_score(),
            self.bot.game.round,
            avg_time
        )

        # 绘制按钮
        self.draw_buttons()

        # 绘制最后动作
        self.draw_last_action()

        # 游戏结束画面
        if self.game_over:
            self.draw_game_over(self.bot.game.get_score())

        # 自动播放
        if self.auto_play and not self.game_over:
            self.do_next_move()

        pygame.display.flip()
        self.clock.tick(30)  # 控制帧率

    def run(self):
        """运行游戏"""
        self.init_game()

        running = True
        while running:
            running = self.handle_events()
            self.render()

        pygame.quit()
        sys.exit()


def main():
    """主函数"""
    view = PygameView()
    view.run()


if __name__ == "__main__":
    main()
