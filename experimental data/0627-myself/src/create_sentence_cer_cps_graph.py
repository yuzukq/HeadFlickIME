#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
table2.csvを元に、目標文章ごとに平均CER（%）の棒グラフ＋平均CPS（文字/秒）の折れ線グラフ（ツイン軸）を描画するスクリプト
実験結果の当家データTable2を元に作成
平均CERと平均CPSにたいして議論
縦方向，横方向のみの入力で完結する「なかの」「ひなた」はエラー率が０だったことが推察できる．
単一方向の入力に対する精度が高いと言える．しかし中でも縦方向の入力のほうが速度が高くなっている
文字数に着目した際に，「ゆめをみる」と「あさになる」はともに五文字で構成されているが，「あさになる」の入力のほうが
精度，速度ともに優れていることがわかる．

"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ファイルパスの設定
data_dir = Path(__file__).parent.parent / "statistical data"
input_file = data_dir / "table2.csv"
graphs_dir = data_dir / "graphs"

# データの読み込み
df = pd.read_csv(input_file)

# 日本語フォントの設定
plt.rcParams['font.family'] = 'MS Gothic'

# グラフ作成
plt.figure(figsize=(12, 7))
ax1 = plt.gca()
bars = ax1.bar(df['目標文章'], df['平均CER（%）'], color=['#222', '#555', '#888', '#bbb', '#888'], label='平均CER（%）')
ax1.set_xlabel('目標文章')
ax1.set_ylabel('平均CER（%）')
ax1.set_ylim(0, 100)
ax1.grid(True, alpha=0.3)
for bar, value in zip(bars, df['平均CER（%）']):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{value:.1f}%', ha='center', va='bottom')

# 右軸にCPSの折れ線グラフ
ax2 = ax1.twinx()
ax2.plot(df['目標文章'], df['平均CPS（文字/秒）'], color='black', marker='o', linewidth=2, label='平均CPS（文字/秒）', markerfacecolor='black')
ax2.set_ylabel('平均CPS（文字/秒）', color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax2.set_ylim(0, 1.00)

# 凡例
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

# ドキュメント側でキャプションを設定するため非表示．
# plt.title('目標文章ごとの平均CERと平均CPS')
plt.tight_layout()
plt.savefig(graphs_dir / 'sentence_cer_cps_graph.png', dpi=300, bbox_inches='tight')
plt.close()

print(f"グラフを作成しました: {graphs_dir / 'sentence_cer_cps_graph.png'}") 