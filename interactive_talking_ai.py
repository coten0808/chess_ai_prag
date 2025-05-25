# -*- coding: utf-8 -*-
import os
import sys
import random

# 在导入 pygame 之前，处理 Linux 无头环境
if sys.platform.startswith("linux") and "DISPLAY" not in os.environ:
    os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import chess
import chess.engine
import pygame_textinput
import textwrap

from config import (
    CHINESE_FONT_PATH, TEXT_FONT_SIZE,
    BOARD_WIDTH, BOARD_HEIGHT, SQUARE_SIZE, FPS,
    WHITE_SQUARE, BLACK_SQUARE, UI_INPUT_H,
    ENGINE_PATH, ENGINE_TIME_LIMIT
)
from gemini_module import generate_move_explanation, interpret_user_command

# 初始化 Pygame
pygame.init()
pygame.font.init()

# 尝试启动 Stockfish 引擎；失败则警告并后备随机走法
engine = None
engine_available = False
if os.path.exists(ENGINE_PATH):
    try:
        engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)
        engine_available = True
        print(f"Loaded Stockfish from {ENGINE_PATH}")
    except Exception as e:
        print(f"Warning: 无法启动 Stockfish ({ENGINE_PATH})：{e}\nAI 将使用随机走法作为后备。")
else:
    print(f"Warning: 找不到 Stockfish 可执行：{ENGINE_PATH}\nAI 将使用随机走法作为后备。")

# 创建窗口
HEIGHT = BOARD_HEIGHT + UI_INPUT_H + TEXT_FONT_SIZE * 3 + 20
screen = pygame.display.set_mode((BOARD_WIDTH, HEIGHT))
pygame.display.set_caption("互动国际象棋 AI")

# 字体
font_piece   = pygame.font.Font(CHINESE_FONT_PATH, SQUARE_SIZE // 2)
font_explain = pygame.font.Font(CHINESE_FONT_PATH, TEXT_FONT_SIZE)

# 文本输入框
textinput = pygame_textinput.TextInputVisualizer()
textinput.font_object    = pygame.font.Font(CHINESE_FONT_PATH, TEXT_FONT_SIZE)
textinput.cursor_visible = True
textinput.cursor_width   = 2
textinput.value          = ""


def get_square_from_pos(pos):
    x, y = pos
    if y >= BOARD_HEIGHT:
        return None
    col = x // SQUARE_SIZE
    row = 7 - (y // SQUARE_SIZE)
    return chess.square(col, row)


def draw_board(board, selected, legal_moves, explanation):
    # 绘制棋盘格与棋子
    for r in range(8):
        for c in range(8):
            color = WHITE_SQUARE if (r + c) % 2 == 0 else BLACK_SQUARE
            x, y = c * SQUARE_SIZE, r * SQUARE_SIZE
            pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))
            sq = chess.square(c, 7 - r)
            p = board.piece_at(sq)
            if p:
                symbol = p.symbol().upper()
                surf = font_piece.render(symbol, True, (0,0,0))
                screen.blit(
                    surf,
                    surf.get_rect(center=(x + SQUARE_SIZE//2, y + SQUARE_SIZE//2))
                )

    # 高亮选中格
    if selected is not None:
        x = chess.square_file(selected) * SQUARE_SIZE
        y = (7 - chess.square_rank(selected)) * SQUARE_SIZE
        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        s.fill((255,255,0,100))
        screen.blit(s, (x, y))

    # 合法走法提示
    for mv in legal_moves:
        x = chess.square_file(mv) * SQUARE_SIZE
        y = (7 - chess.square_rank(mv)) * SQUARE_SIZE
        pygame.draw.circle(
            screen, (0,200,0),
            (x + SQUARE_SIZE//2, y + SQUARE_SIZE//2),
            SQUARE_SIZE//6
        )

    # 解释文字
    y0 = BOARD_HEIGHT + 10
    for i, line in enumerate(textwrap.wrap(explanation, 40)[:3]):
        text_surf = font_explain.render(line, True, (0,0,0))
        screen.blit(text_surf, (10, y0 + i*(TEXT_FONT_SIZE+2)))

    # 输入框
    rect = pygame.Rect(
        10,
        BOARD_HEIGHT + TEXT_FONT_SIZE*3 + 20,
        BOARD_WIDTH - 20,
        UI_INPUT_H
    )
    pygame.draw.rect(screen, (230,230,230), rect, border_radius=5)
    screen.blit(textinput.surface, (rect.x+5, rect.y+4))


def main():
    board        = chess.Board()
    selected     = None
    legal_moves  = []
    explanation  = "欢迎！点击棋子 或 在下方输入策略回车"
    strategy     = "控制中心"

    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill((255,255,255))
        draw_board(board, selected, legal_moves, explanation)
        pygame.display.flip()
        clock.tick(FPS)

        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                running = False

            # 点击：选子或走子
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                sq = get_square_from_pos(ev.pos)
                if sq is not None and board.turn == chess.WHITE:
                    if selected is None and board.piece_at(sq):
                        selected = sq
                        legal_moves = [
                            m.to_square for m in board.legal_moves
                            if m.from_square == sq
                        ]
                    elif selected is not None and sq in legal_moves:
                        board.push(chess.Move(selected, sq))
                        selected, legal_moves = None, []

                        # AI 走子
                        if engine_available:
                            result = engine.play(
                                board,
                                chess.engine.Limit(time=ENGINE_TIME_LIMIT)
                            )
                            board.push(result.move)
                            uci = result.move.uci()
                        else:
                            mv = random.choice(list(board.legal_moves))
                            board.push(mv)
                            uci = mv.uci()

                        move_no = len(board.move_stack)//2 + 1
                        explanation = generate_move_explanation(
                            uci, move_no, strategy
                        )

            # 回车提交策略
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    cmd = textinput.value.strip()
                    if cmd:
                        strategy, explanation = interpret_user_command(cmd)
                        textinput.value = ""
                elif ev.key == pygame.K_BACKSPACE:
                    textinput.value = textinput.value[:-1]
                elif ev.unicode.isprintable():
                    textinput.value += ev.unicode

        # 更新输入框状态，一次性接收完整事件列表
        textinput.update(events)

    if engine_available:
        engine.quit()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
