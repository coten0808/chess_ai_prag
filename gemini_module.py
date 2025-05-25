# -*- coding: utf-8 -*-
import ast
import logging
from typing import Tuple

# 尝试导入 Gemini SDK
try:
    import google.generativeai as genai
except ImportError:
    genai = None

from config import GEMINI_API_KEY, GEMINI_MODEL_PRIMARY, GEMINI_MODEL_FALLBACK

logger = logging.getLogger(__name__)


class DummyModel:
    def generate_content(self, prompt: str):
        class Resp:
            text = "（AI 解释暂不可用）"
        return Resp()


def _init_model():
    if not genai:
        logger.warning("google-generativeai SDK 未安装，启用离线 DummyModel")
        return DummyModel()

    genai.configure(api_key=GEMINI_API_KEY)
    try:
        model = genai.GenerativeModel(GEMINI_MODEL_PRIMARY)
        logger.info(f"连接到主模型：{GEMINI_MODEL_PRIMARY}")
        return model
    except Exception as e:
        logger.warning(f"主模型连接失败：{e}，尝试备用模型")
        try:
            model = genai.GenerativeModel(GEMINI_MODEL_FALLBACK)
            logger.info(f"连接到备用模型：{GEMINI_MODEL_FALLBACK}")
            return model
        except Exception as e2:
            logger.error(f"备用模型也失败：{e2}，启用离线 DummyModel")
            return DummyModel()


_model = _init_model()


def generate_move_explanation(
    move_uci: str,
    move_number: int,
    strategy: str
) -> str:
    """
    使用 Gemini 为 UCI 走法生成一句中文战略解释（不超过20字）。
    """
    prompt = (
        f"你是一个会说中文的国际象棋 AI，当前策略“{strategy}”。\n"
        f"这是第 {move_number} 步，走法：{move_uci}。\n"
        "请用一句话（不超过20字）简要说明这一步的战略意图。"
    )
    try:
        resp = _model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        logger.error(f"生成解释失败：{e}")
        return f"（AI走了{move_uci}，无法生成解释）"


def interpret_user_command(text: str) -> Tuple[str, str]:
    """
    解析用户的中文策略指令，提取标准策略名并返回 AI 的确认回应。
    返回 (策略名称, AI回应文本)。
    """
    prompt = (
        f"你是一个国际象棋 AI 策略助手，"
        f"现在用户输入：「{text}」。\n"
        "请返回一个 Python 字典，格式如下：\n"
        "{'strategy':'策略名称','response':'AI 的中文确认回应'}\n"
        "如果策略不明确，就把 strategy 设为“灵活应对”。"
    )
    try:
        resp = _model.generate_content(prompt)
        data = ast.literal_eval(resp.text.strip())
        strat = data.get("strategy", "灵活应对")
        reply = data.get("response", "")
        return strat, reply
    except Exception as e:
        logger.error(f"解析指令失败：{e}")
        return "灵活应对", "（无法解析您的策略，请再试）"
