#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取训练日志 cout.txt 中每个 `my_main Recent Stats` 块的核心指标：
  Episode、monster_last_hp_mean、grad_norm、
  loss_td / td_error_abs（二选一）、return_mean
保存为 Excel 或 CSV
"""

import re
import sys
from pathlib import Path
import pandas as pd


# ----------------------------- 核心解析 ----------------------------- #
def parse_recent_stats(file_path: Path) -> pd.DataFrame:
    """
    返回 DataFrame：
    Episode | Monster_HP | Grad_Norm | Loss | Return_Mean
    """
    # 正则
    ep_re  = re.compile(r'Episode:\s+(\d+)')
    hp_re  = re.compile(r'monster_last_hp_mean:\s*([0-9.+-eE]+)')
    gn_re  = re.compile(r'grad_norm:\s*([0-9.+-eE]+)')
    loss_re = re.compile(r'loss_td:\s*([0-9.+-eE]+)')
    td_re   = re.compile(r'td_error_abs:\s*([0-9.+-eE]+)')
    ret_re  = re.compile(r'return_mean:\s*([0-9.+-eE]+)')

    records = []

    with file_path.open('r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if 'my_main Recent Stats' in line:
            # 先抓 Episode
            m_ep = ep_re.search(line)
            episode = int(m_ep.group(1)) if m_ep else -1

            # 默认缺失值
            monster_hp = -1.0
            grad_norm  = float('nan')
            loss_val   = float('nan')
            return_mean = 0.0

            # 继续向下读取直到遇到空行或文件结束
            i += 1
            while i < n and lines[i].strip():
                l = lines[i]

                if (m := hp_re.search(l)):
                    monster_hp = float(m.group(1))
                if (m := gn_re.search(l)):
                    grad_norm = float(m.group(1))
                if (m := loss_re.search(l)):
                    loss_val = float(m.group(1))
                # 若没有 loss_td，则用 td_error_abs
                if pd.isna(loss_val) and (m := td_re.search(l)):
                    loss_val = float(m.group(1))
                if (m := ret_re.search(l)):
                    return_mean = float(m.group(1))

                i += 1

            records.append((episode, monster_hp, grad_norm, loss_val, return_mean))

        else:
            i += 1

    cols = ['Episode', 'Monster_HP', 'Grad_Norm', 'Loss', 'Return_Mean']
    return pd.DataFrame(records, columns=cols)


# ---------------------------- 主函数 ---------------------------- #
def main() -> None:
    # 支持命令行：python extract_recent_stats.py [cout.txt] [out.xlsx]
    log_file = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('cout.txt')
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('recent_stats_summary.xlsx')

    if not log_file.exists():
        raise FileNotFoundError(f'找不到日志文件: {log_file.resolve()}')

    df = parse_recent_stats(log_file).sort_values('Episode').reset_index(drop=True)

    # 按扩展名自动选择格式
    if out_path.suffix.lower() in {'.csv', '.txt'}:
        df.to_csv(out_path, index=False)
    else:
        df.to_excel(out_path, index=False)

    print(f'✅ 解析完成，已保存到 {out_path.resolve()}')


if __name__ == '__main__':
    main()
