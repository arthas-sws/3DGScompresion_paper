#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

REQUIRED = {
    '汇报摘要': [r'汇报摘要', r'核心速览', r'审稿结论摘要'],
    '核心贡献': [r'核心贡献', r'一句话.*贡献', r'工作总结'],
    '方法分析': [r'方法', r'技术路线', r'系统流程'],
    '实验设置': [r'实验设置', r'评估设置', r'实验协议'],
    '主要结果': [r'主要结果', r'结果总表', r'定量结果', r'实验结果'],
    '结果解读': [r'结果证明了什么', r'结果解读', r'结果汇报总结'],
    '局限性': [r'局限', r'失败案例', r'适用边界'],
    '代码状态': [r'代码', r'仓库', r'可复现'],
    '最终总结': [r'最终汇报总结', r'总体评价', r'一句话结论', r'最终审稿总结'],
}
DEEP = {
    '效率与存储': [r'效率', r'存储', r'显存', r'模型大小', r'计算代价'],
    '消融实验': [r'消融'],
    '未证明内容': [r'尚未证明', r'没有证明', r'不能证明', r'证据不足'],
}
EN_HEAD = re.compile(r'^#{1,6}\s+(Summary|Introduction|Background|Method|Methods|Experiments?|Results?|Limitations?|Conclusion|Discussion|Reproducibility)\b', re.I | re.M)
METRIC = re.compile(r'\b(?:PSNR|SSIM|LPIPS|FPS|ATE|RPE|MB|GB|ms|dB|hours?)\b', re.I)
EVIDENCE = [r'\[论文', r'\[补充材料', r'\[代码', r'\bTable\s*[A-Za-z]?\d+', r'\bFig(?:ure)?\.?\s*\d+', r'\bEq(?:uation)?\.?\s*\d+', r'论文未报告', r'无法.*核实', r'未提供']


def any_match(text: str, pats: list[str]) -> bool:
    return any(re.search(x, text, re.I) for x in pats)


def main() -> None:
    p = argparse.ArgumentParser(description='校验单篇中文论文报告')
    p.add_argument('report', type=Path)
    p.add_argument('--mode', default='中文精读')
    p.add_argument('--min-chinese', type=int)
    p.add_argument('--min-ratio', type=float, default=0.25)
    p.add_argument('--json-output', type=Path)
    a = p.parse_args()
    if not a.report.is_file():
        raise SystemExit(f'找不到报告：{a.report}')

    text = a.report.read_text(encoding='utf-8')
    cn = sum('\u4e00' <= c <= '\u9fff' for c in text)
    latin = sum(c.isascii() and c.isalpha() for c in text)
    ratio = cn / max(cn + latin, 1)
    min_cn = a.min_chinese or (500 if ('精炼' in a.mode or '速读' in a.mode) else 1200)
    errors, warnings = [], []

    if cn < min_cn:
        errors.append(f'中文字符不足：{cn} < {min_cn}')
    if ratio < a.min_ratio:
        errors.append(f'中文比例过低：{ratio:.3f} < {a.min_ratio:.3f}')
    en_count = len(EN_HEAD.findall(text))
    if en_count >= 3:
        errors.append(f'英文主章节标题过多：{en_count} 个')
    for name, pats in REQUIRED.items():
        if not any_match(text, pats):
            errors.append(f'缺少必要部分：{name}')
    if '精读' in a.mode or '审稿' in a.mode:
        for name, pats in DEEP.items():
            if not any_match(text, pats):
                warnings.append(f'未检测到深度分析部分：{name}')
    if METRIC.search(text) and not any_match(text, EVIDENCE):
        errors.append('包含指标或单位，但未检测到论文、补充材料或代码证据位置')
    if not re.search(r'\|.+\|', text):
        warnings.append('未检测到 Markdown 表格，可能缺少结果总表')
    if not re.search(r'论文未报告|未提供|无法.*核实|待核实|N/A', text):
        warnings.append('未检测到缺失信息标记，请确认没有静默省略')

    status = 'FAIL' if errors else ('WARN' if warnings else 'PASS')
    result = {
        'file': str(a.report), 'mode': a.mode, 'status': status,
        'chinese_characters': cn, 'latin_characters': latin,
        'chinese_ratio': round(ratio, 4), 'english_heading_count': en_count,
        'errors': errors, 'warnings': warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if a.json_output:
        a.json_output.parent.mkdir(parents=True, exist_ok=True)
        a.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    raise SystemExit(1 if status == 'FAIL' else 0)


if __name__ == '__main__':
    main()
