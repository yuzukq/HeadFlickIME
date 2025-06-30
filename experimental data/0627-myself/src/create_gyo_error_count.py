#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
table1.csvをもとに、目標文字列と入力文字列を1文字ずつ比較し、目標文字の行ごとに誤り入力が何回あったかを集計し、CSVとグラフで出力するスクリプト
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# 行の分類
GYOS = {
    'あ行': set('あいうえお'),
    'か行': set('かきくけこ'),
    'さ行': set('さしすせそ'),
    'た行': set('たちつてと'),
    'な行': set('なにぬねの'),
    'は行': set('はひふへほ'),
    'ま行': set('まみむめも'),
    'や行': set('やゆよ'),
    'ら行': set('らりるれろ'),
    'わ行': set('わをん'),
}

def get_gyo(char):
    for gyo, chars in GYOS.items():
        if char in chars:
            return gyo
    return 'その他'

# ファイルパス設定
data_dir = Path(__file__).parent.parent / "statistical data"
input_file = data_dir / "table1.csv"
graphs_dir = data_dir / "graphs"
output_csv = data_dir / "table3.csv"

# データ読み込み
df = pd.read_csv(input_file, skiprows=1)

gyo_error_count = {gyo: 0 for gyo in GYOS}
gyo_total_count = {gyo: 0 for gyo in GYOS}

for idx, row in df.iterrows():
    target = str(row['目標文字列'])
    entered = str(row['入力された文章'])
    for i, orig_char in enumerate(target):
        gyo = get_gyo(orig_char)
        gyo_total_count[gyo] += 1
        if i < len(entered):
            if orig_char != entered[i]:
                gyo_error_count[gyo] += 1
        else:
            # 入力文字列が短い場合も誤りとカウント
            gyo_error_count[gyo] += 1

# CSV出力
df_out = pd.DataFrame({
    '行': list(GYOS.keys()),
    '誤り回数': [gyo_error_count[gyo] for gyo in GYOS],
    '出現数': [gyo_total_count[gyo] for gyo in GYOS]
})
df_out['誤り率（%）'] = df_out.apply(lambda row: (row['誤り回数'] / row['出現数'] * 100) if row['出現数'] > 0 else 0, axis=1)
df_out.to_csv(output_csv, index=False, encoding='utf-8-sig')
print(f'CSVを出力しました: {output_csv}')

# グラフ作成
font_name = "MS Gothic"
plt.rcParams['font.family'] = font_name
plt.figure(figsize=(10,6))
plt.bar(df_out['行'], df_out['誤り回数'], color='#888')
plt.xlabel('行', fontname=font_name)
plt.ylabel('誤り回数', fontname=font_name)
plt.title('行ごとの誤り入力回数', fontname=font_name)
plt.tight_layout()
plt.savefig(graphs_dir / 'gyo_error_count.png', dpi=300, bbox_inches='tight')
plt.close()
print(f'グラフを作成しました: {graphs_dir / "gyo_error_count.png"}')

# 誤り率の棒グラフ
plt.figure(figsize=(10,6))
plt.bar(df_out['行'], df_out['誤り率（%）'], color='#888')
plt.xlabel('行', fontname=font_name)
plt.ylabel('誤り率（%）', fontname=font_name)
plt.title('行ごとの誤り率', fontname=font_name)
plt.ylim(0, 100)
plt.tight_layout()
plt.savefig(graphs_dir / 'gyo_error_rate2.png', dpi=300, bbox_inches='tight')
plt.close()
print(f'誤り率グラフを作成しました: {graphs_dir / "gyo_error_rate2.png"}') 