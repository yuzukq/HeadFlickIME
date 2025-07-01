import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ファイルパスの設定
base_dir = Path(__file__).parent.parent
input_file = base_dir / 'statistical data' / 'table4.csv'
graphs_dir = base_dir / 'statistical data' / 'graphs'
graphs_dir.mkdir(exist_ok=True)

# データの読み込み
df = pd.read_csv(input_file)

# 日本語フォントの設定
plt.rcParams['font.family'] = 'MS Gothic'

# 測定者ごとにデータを整理
participants = df['測定者'].unique()
nakano_cer = []
hinata_cer = []
nakano_cps = []
hinata_cps = []

for participant in participants:
    nakano_data = df[(df['測定者'] == participant) & (df['目標文字列'] == 'なかの')]
    if not nakano_data.empty:
        nakano_cer.append(nakano_data['CER(％)'].iloc[0])
        nakano_cps.append(nakano_data['CPS（文字/秒）'].iloc[0])
    else:
        nakano_cer.append(0)
        nakano_cps.append(0)
    hinata_data = df[(df['測定者'] == participant) & (df['目標文字列'] == 'ひなた')]
    if not hinata_data.empty:
        hinata_cer.append(hinata_data['CER(％)'].iloc[0])
        hinata_cps.append(hinata_data['CPS（文字/秒）'].iloc[0])
    else:
        hinata_cer.append(0)
        hinata_cps.append(0)

x = np.arange(len(participants))
width = 0.35

fig, ax1 = plt.subplots(figsize=(12, 8))

# グレースケールの配色
bar_color1 = '#222'
bar_color2 = '#888'

bars1 = ax1.bar(x - width/2, nakano_cer, width, label='なかの CER', color=bar_color1)
bars2 = ax1.bar(x + width/2, hinata_cer, width, label='ひなた CER', color=bar_color2)

ax1.set_xlabel('測定者', fontsize=12)
ax1.set_ylabel('CER (%)')
ax1.set_ylim(0, 100)
ax1.set_xticks(x)
ax1.set_xticklabels(participants, rotation=45, ha='right')
ax1.grid(True, alpha=0.3)

for bar, value in zip(bars1, nakano_cer):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
for bar, value in zip(bars2, hinata_cer):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{value:.1f}%', ha='center', va='bottom', fontsize=9)

# CPSの折れ線グラフ
ax2 = ax1.twinx()
ax2.plot(x, nakano_cps, color='black', marker='o', linewidth=2, label='なかの CPS', markerfacecolor='black', linestyle='-')
ax2.plot(x, hinata_cps, color='gray', marker='o', linewidth=2, label='ひなた CPS', markerfacecolor='gray', linestyle='-')
ax2.set_ylabel('CPS（文字/秒）', color='black')
ax2.tick_params(axis='y', labelcolor='black')
ax2.set_ylim(0, 1.00)

# 凡例
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.tight_layout()
plt.savefig(graphs_dir / 'cer_comparison_monochrome.png', dpi=300, bbox_inches='tight')
plt.close()

# 統計情報も表示
print("=== CER統計情報 ===")
print(f"なかのの平均CER: {np.mean(nakano_cer):.1f}%")
print(f"ひなたの平均CER: {np.mean(hinata_cer):.1f}%")
print(f"なかのの標準偏差: {np.std(nakano_cer):.1f}%")
print(f"ひなたの標準偏差: {np.std(hinata_cer):.1f}%")

# 統計情報をファイルに保存
with open(base_dir / 'statistical data' / 'cer_analysis_report.txt', 'w', encoding='utf-8') as f:
    f.write("=== CER分析レポート ===\n\n")
    f.write(f"なかのの平均CER: {np.mean(nakano_cer):.1f}%\n")
    f.write(f"ひなたの平均CER: {np.mean(hinata_cer):.1f}%\n")
    f.write(f"なかのの標準偏差: {np.std(nakano_cer):.1f}%\n")
    f.write(f"ひなたの標準偏差: {np.std(hinata_cer):.1f}%\n\n")
    f.write("=== 各測定者の詳細データ ===\n")
    for i, participant in enumerate(participants):
        f.write(f"{participant}: なかの={nakano_cer[i]:.1f}%, ひなた={hinata_cer[i]:.1f}%, なかのCPS={nakano_cps[i]:.2f}, ひなたCPS={hinata_cps[i]:.2f}\n")

print(f"グラフを作成しました: {graphs_dir / 'cer_comparison_monochrome.png'}") 