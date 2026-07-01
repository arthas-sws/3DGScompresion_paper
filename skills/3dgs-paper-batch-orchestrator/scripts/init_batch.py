#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from datetime import datetime
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser(description='将论文 CSV 初始化为批次 JSON 和输出目录')
    p.add_argument('csv_file', type=Path)
    p.add_argument('--batch-id', required=True)
    p.add_argument('--mode', default='中文精读')
    p.add_argument('--parallel-workers', type=int, default=1)
    p.add_argument('--max-retries', type=int, default=2)
    p.add_argument('--output-dir', type=Path)
    p.add_argument('--output', type=Path, default=Path('batch.json'))
    a = p.parse_args()

    if not a.csv_file.is_file():
        raise SystemExit(f'找不到 CSV：{a.csv_file}')
    if not 1 <= a.parallel_workers <= 3:
        raise SystemExit('parallel_workers 必须在 1—3 之间')

    papers = []
    with a.csv_file.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        missing = {'title', 'source'} - set(reader.fieldnames or [])
        if missing:
            raise SystemExit('CSV 缺少列：' + ', '.join(sorted(missing)))
        for i, row in enumerate(reader, 1):
            papers.append({
                'id': (row.get('id') or f'P{i:03d}').strip(),
                'title': (row.get('title') or '').strip(),
                'source': (row.get('source') or '').strip(),
                'code': (row.get('code') or '').strip(),
                'notes': (row.get('notes') or '').strip(),
            })

    ids = [x['id'] for x in papers]
    if len(ids) != len(set(ids)):
        raise SystemExit('论文 ID 存在重复')

    out_dir = a.output_dir or Path('paper-batch-output') / a.batch_id
    payload = {
        'batch_id': a.batch_id,
        'created_at': datetime.now().isoformat(timespec='seconds'),
        'mode': a.mode,
        'language': 'zh-CN',
        'parallel_workers': a.parallel_workers,
        'max_retries': a.max_retries,
        'output_dir': str(out_dir),
        'papers': papers,
    }

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    for sub in ['items', 'validation', 'retry-prompts']:
        (out_dir / sub).mkdir(parents=True, exist_ok=True)
    (out_dir / 'manifest.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    status = {x['id']: {'status': 'pending', 'attempts': 0, 'title': x['title']} for x in papers}
    (out_dir / 'status.json').write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'已生成批次配置：{a.output}')
    print(f'论文数量：{len(papers)}')
    print(f'输出目录：{out_dir}')


if __name__ == '__main__':
    main()
