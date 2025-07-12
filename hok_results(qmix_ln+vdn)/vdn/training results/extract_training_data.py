#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 GameCore 训练日志 cout.txt 中抽取每个 episode 的最终 Monster HP，
并导出到 Excel 表格
"""

import re
from pathlib import Path
import pandas as pd


def parse_cout(file_path: Path) -> pd.DataFrame:
    """
    解析 cout.txt，返回 DataFrame，列为 Episode 和 Monster_HP
    """
    episode_records = []          # [(episode_idx, monster_hp), ...]
    cur_ep = None                 # 当前 episode 编号
    cur_hp = None                 # 当前 episode 最新记录到的 HP

    # 正则准备
    ep_re = re.compile(r'Cur episode[^\d]*(\d+)')
    hp_re = re.compile(r'Monster HP = (\d+)')

    with file_path.open('r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # 1) 检测 episode 开始
            m_ep = ep_re.search(line)
            if m_ep:
                # 遇到下一条 episode 前，如果上一条已完整记录，先保存
                if cur_ep is not None and cur_hp is not None:
                    episode_records.append((cur_ep, cur_hp))
                cur_ep = int(m_ep.group(1))
                cur_hp = None          # 重置
                continue

            # 2) 更新本行记录到的 Monster HP（只要出现就记录，Game Over 前的最后一次会留下来）
            m_hp = hp_re.search(line)
            if m_hp:
                cur_hp = int(m_hp.group(1))
                continue

            # 3) 如果遇到 Game Over 行，视为本 episode 结束
            if 'Game Over' in line and cur_ep is not None:
                # 有可能某些 episode 没有 Monster HP 行；确保不丢失索引
                episode_records.append((cur_ep, cur_hp if cur_hp is not None else -1))
                cur_ep, cur_hp = None, None

    # 文件末尾如果还有悬空的 episode（没有显式 Game Over），也补上
    if cur_ep is not None and cur_hp is not None:
        episode_records.append((cur_ep, cur_hp))

    return pd.DataFrame(episode_records, columns=['Episode', 'Monster_HP'])


def main():
    log_file = Path('cout.txt')        # 如有其它路径请修改
    if not log_file.exists():
        raise FileNotFoundError(f'找不到日志文件: {log_file.resolve()}')

    df = parse_cout(log_file)

    # 按 Episode 升序保证顺序一致
    df.sort_values('Episode', inplace=True)
    df.reset_index(drop=True, inplace=True)

    # 导出 Excel
    out_path = Path('monster_hp_summary.xlsx')
    df.to_excel(out_path, index=False)
    print(f'✅ 解析完成，已保存到 {out_path.resolve()}')


if __name__ == '__main__':
    main()
