# -*- coding: utf-8 -*-
import os

# 取本文件所在目录
BASE_DIR = os.path.dirname(__file__)

# Gemini API 配置
GEMINI_API_KEY        = "AIzaSyCRSMl-N2gWz38jKsj4xkGGxLlVPXYdH68"
GEMINI_MODEL_PRIMARY  = "gemini-1.5-flash"
GEMINI_MODEL_FALLBACK = "gemini-pro"

# Stockfish 引擎设置
ENGINE_TIME_LIMIT = 0.5
ENGINE_DEPTH      = 15
ENGINE_PATH       = os.getenv(
    "STOCKFISH_PATH",
    os.path.join(BASE_DIR, "stockfish.exe")
)

# 棋盘 & UI 设置
BOARD_WIDTH    = 480
BOARD_HEIGHT   = 480
SQUARE_SIZE    = BOARD_WIDTH // 8
FPS            = 30

WHITE_SQUARE   = (240, 217, 181)
BLACK_SQUARE   = (181, 136,  99)

# 下方输入框 & 解释区高度
UI_INPUT_H     = 30
TEXT_FONT_SIZE = 18

# 字体路径
CHINESE_FONT_PATH = r"C:/Windows/Fonts/msjh.ttc"
if not os.path.exists(CHINESE_FONT_PATH):
    CHINESE_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# 默认 AI 策略
DEFAULT_STRATEGY = "控制中心"
