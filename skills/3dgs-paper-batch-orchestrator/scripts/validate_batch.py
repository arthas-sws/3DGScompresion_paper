#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def cn_ratio(text: str) -> float:
    cn = sum('\u4e00' <= c <= '\u9fff' for c in text)
    latin = sum(c.isascii() and c.isalpha() for c in text)
    return cn / max(cn + latin, 1)


def main() -> None:
    p = argparse.ArgumentParser(description='检查批次状态与汇总')
    p.add_argument('batch_dir', type=Path)
    p.add_argument('--manifest', type=Path)
    a = p.parse_args()
    manifest_path = a.manifest or a.batch_dir / 'manifest.json'
    status_path = a.batch_dir / 'status.json'
    if not manifest_path.is_file():
        raise SystemExit(f'找不到 manifest：{manifest_path}')
    if not status_path.is_file():
        raise SystemExit(f'找不到 status：{status_path}')

    manifest, status = load(manifest_path), load(status_path)
    papers = manifest.get('papers', [])
    errors, warnings = [], []
    ids = [x.get('id') for x in papers]
    if len(ids) != len(set(ids)):
        errors.append('manifest 中存在重复论文 ID')

    valid = failed = unfinished = 0
    for paper in papers:
        pid = paper['id']
        entry = status.get(pid)
        if entry is None:
            errors.append(f'{pid} 缺少状态')
            continue
        state = entry.get('status')
        final = a.batch_dir / 'items' / f'{pid}.md'
        if state == 'validated':
            valid += 1
            if not final.is_file():
                errors.append(f'{pid} 标记 validated，但缺少最终文件')
        elif str(state).startswith('failed'):
            failed += 1
        else:
            unfinished += 1

    summary_path = a.batch_dir / 'batch-summary.md'
    if summary_path.is_file():
        summary = summary_path.read_text(encoding='utf-8')
        if cn_ratio(summary) < 0.25:
            errors.append('批次总结中文比例过低')
        for pat in ['批次完成情况', '批次结论摘要', '单篇论文索引', '主要结果对比', '失败与缺失', '批次最终总结']:
            if not re.search(pat, summary):
                warnings.append(f'批次总结缺少：{pat}')
        for paper in papers:
            pid = paper['id']
            if status.get(pid, {}).get('status') == 'validated' and pid not in summary:
                warnings.append(f'批次总结可能遗漏已验证论文：{pid}')
    else:
        warnings.append('尚未生成 batch-summary.md')

    if failed and not (a.batch_dir / 'failed-items.md').is_file():
        warnings.append('存在失败项，但未生成 failed-items.md')

    result = {
        'batch_id': manifest.get('batch_id'), 'papers': len(papers),
        'validated': valid, 'failed': failed, 'unfinished': unfinished,
        'errors': errors, 'warnings': warnings,
        'status': 'FAIL' if errors else ('WARN' if warnings else 'PASS'),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(1 if errors else 0)


if __name__ == '__main__':
    main()
