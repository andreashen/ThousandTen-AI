# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI bot project for the game **ThousandTen** (10x10 积木消除游戏). The goal is to develop an AI that can automatically play the game and achieve the highest possible score.

## Game Rules (ThousandTen)

Based on `games_spec.md`, the game is a 10x10 grid-based block placement puzzle game with the following core mechanics:

### Core Mechanics
- **Grid**: 10x10 playing field
- **Pieces**: Each round, 3 random pieces are generated in the reserve area
- **Placement**: Player can place pieces in any order, without overlap or going out of bounds
- **Clearing**: Filling any entire row or column triggers clearing and bonus points
- **Game Over**: When no remaining piece in the reserve can be legally placed anywhere on the board

### Scoring
- **Base placement score**: `n` points where `n` = number of cells occupied by the piece
- **Clear bonus**: `+10` points per row/column cleared
- **Multi-clear examples**: Clearing 1 row + 1 column = `+20`; clearing 2 rows + 1 column = `+30`
- **Total**: Placement score + Clear bonus

### Piece Types
- **Basic pieces** (max 3x3):
  - 1x1 dot
  - 1x2 / 1x3 lines (horizontal and vertical)
  - 2x2 / 3x3 squares
  - L-shaped pieces (2x2 and 3x3 variants)
  - 1x4 long bars (horizontal and vertical)
  - 1x5 long bars (horizontal and vertical)

### Technical Stack (for game implementation)
- React + Vite + TypeScript + Tailwind CSS
- Logic layer and presentation layer separation
- Immutable data structures for grid state updates
- Game Over detection must execute precisely after "successful placement" and "after restocking"

## M1 里程碑计划

**当前开发阶段**: M1 - 纯逻辑 AI Bot + Pygame 可视化

详细计划请参阅 `M1_PLAN.md`，包含：
- 完整任务清单（4 个主任务）
- 项目结构设计
- 技术栈确认：Python 3.10+, Pygame, pytest
- 开发顺序和交付物

### M1 关键约束
- **暂不对接游戏前端**：只做纯逻辑的 AI，然后自己模拟
- **决策时限**：期望 1s 内给出决策（先精度后性能）
- **评估目标**：单局最高分和平均分稳定性并重
- **积木类型**：必须包含所有积木（1x1 到 1x5 全部变体）
- **可视化要求**：需要 Pygame 界面用于人工验证效果（视觉效果可简陋）

## AI Development Goals

The AI should:
1. Analyze the current board state and available pieces
2. Make optimal placement decisions to maximize score
3. Plan ahead to avoid early game termination
4. Prioritize moves that enable row/column clears
5. Handle spatial reasoning for piece placement
6. **M1 特殊要求**：特别处理 1x4/1x5 长条积木（预留空间、避免破碎空地）

## Key Constraints

- The AI needs to simulate legal placements before executing them
- Must consider all 3 pieces in each round before committing to placements
- Should evaluate placement quality based on immediate score AND future board viability
- Game Over condition is critical: any remaining piece that cannot be placed ends the game
