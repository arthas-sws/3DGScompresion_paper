#!/usr/bin/env python3
"""检查中文论文报告是否包含结果汇报和必要结构。"""

from __future__ import annotations
import argparse
import re
from pathlib import Path

COMMON_REQUIRED = {
    "汇报摘要": [r"汇报摘要", r"核心速览", r"审稿结论摘要"],
    "主要结果": [r"主要结果", r"结果总表", r"定量结果"],
    "结果解读": [r"结果解读", r"结果证明了什么", r"实验结果审计"],
    "局限性": [r"局限", r"失败案例", r"适用边界"],
    "最终总结": [r"最终汇报总结", r"总体评价", r"最终审稿总结", r"一句话结论"],
}

PROFILE_REQUIRED = {
    "精读": [r"方法", r"代码", r"实验设置", r"消融", r"可复现"],
    "速读": [r"关键创新", r"主要结果", r"局限"],
    "审稿": [r"主要问题", r"实验结果审计", r"给作者的问题"],
    "复现": [r"环境", r"数据集", r"训练命令", r"评估命令", r"目标结果"],
    "对比": [r"方法对比", r"结果对比", r"可比性", r"综合结果总结"],
}


def has_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("--profile", choices=list(PROFILE_REQUIRED), default="精读")
    args = parser.parse_args()

    if not args.report.is_file():
        raise SystemExit(f"找不到报告：{args.report}")

    text = args.report.read_text(encoding="utf-8")
    errors = []
    warnings = []

    for name, patterns in COMMON_REQUIRED.items():
        if not has_any(text, patterns):
            errors.append(f"缺少必要部分：{name}")

    for pattern in PROFILE_REQUIRED[args.profile]:
        if not re.search(pattern, text, re.IGNORECASE):
            warnings.append(f"未检测到与“{pattern}”相关的内容。")

    if re.search(r"\b(?:PSNR|SSIM|LPIPS|FPS|MB|GB|ms|ATE|RPE)\b", text, re.I):
        evidence = [r"\[论文", r"\[补充材料", r"\[代码", r"Table\s*\d+", r"Fig\.", r"Eq\."]
        if not has_any(text, evidence):
            warnings.append("检测到指标或单位，但未检测到明显证据标记。")

    if not re.search(r"论文未报告|无法核实|N/A|未提供|待核实", text):
        warnings.append("未检测到缺失信息标记；请确认没有静默省略未报告内容。")

    chinese = sum("\u4e00" <= c <= "\u9fff" for c in text)
    latin = sum(c.isascii() and c.isalpha() for c in text)
    if latin > 0 and chinese / max(latin, 1) < 0.08:
        warnings.append("报告中文比例偏低，可能没有按默认中文输出。")

    print(f"检查模式：{args.profile}")
    if errors:
        print("\n错误：")
        for item in errors:
            print(f"- {item}")
    if warnings:
        print("\n警告：")
        for item in warnings:
            print(f"- {item}")
    if not errors and not warnings:
        print("未发现结构性问题。")

    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
