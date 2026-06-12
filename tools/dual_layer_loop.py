#!/usr/bin/env python3
"""
Dual-Layer LLM Loop Tool

複雜問題自動交給 Gemini 規劃策略，再由 Low-LLM 精確執行 tool_call。
不需要 system prompt 或 LLM 自行判斷，LLM 直接呼叫他作為普通 tool。

使用方式：
    LLM 遇到複雜問題（分析、比較、評估、研究、策劃等）時直接呼叫此 tool。
    回傳結果包含策略規劃 + 工具執行結果。

Author: Hermes Agent
"""

import json
import sys
import os
import logging

logger = logging.getLogger(__name__)

# 動態載入 high_llm_loop
HIGH_LLM_LOOP_PATH = "/home/eric/.hermes/work/dual-layer-llm-architect"
if HIGH_LLM_LOOP_PATH not in sys.path:
    sys.path.insert(0, HIGH_LLM_LOOP_PATH)

from tools.registry import registry


def check_requirements() -> bool:
    """檢查所需套件已安裝"""
    try:
        import high_llm_loop
        return True
    except ImportError:
        return False


def dual_layer_loop(
    question: str,
    profile: str = "default",
    tools_json: str = "[]",
) -> str:
    """
    使用 High-LLM (Gemini) 規劃策略 + Low-LLM 執行 tool_call。

    Args:
        question: 用戶的問題（完整描述）
        profile: Hermes profile 名稱（預設 default）
        tools_json: 可用工具的 JSON 字串 [{"name": "...", "description": "..."}, ...]

    Returns:
        JSON 字串，包含 status、result、history
    """
    try:
        from high_llm_loop import high_llm_loop

        tools = json.loads(tools_json)
        result = high_llm_loop(question, tools, profile)
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": str(e),
            "result": None,
            "history": []
        }, ensure_ascii=False)


# 註冊 tool
registry.register(
    name="dual_layer_loop",
    toolset="dual-layer",
    schema={
        "name": "dual_layer_loop",
        "description": (
            "For complex multi-step tasks (analysis, comparison, evaluation, "
            "planning, research, etc. - Chinese keywords: 分析、比較、評估、研究、"
            "策劃、檢測、監控、搜尋、整理、彙整、設計、建構、多個、持續、深度): "
            "use High-LLM (Gemini) to plan the strategy, then Low-LLM to execute"
            " precise tool calls. Returns structured results with strategy + execution history."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The user's question or task"
                },
                "profile": {
                    "type": "string",
                    "description": "Hermes profile name (default: 'default')",
                    "default": "default"
                },
                "tools_json": {
                    "type": "string",
                    "description": "JSON string of available tools",
                    "default": "[]"
                }
            },
            "required": ["question"]
        }
    },
    handler=lambda args, **kw: dual_layer_loop(
        question=args.get("question", ""),
        profile=args.get("profile", "default"),
        tools_json=args.get("tools_json", "[]"),
    ),
    check_fn=check_requirements,
    requires_env=[],
)
