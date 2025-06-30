#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文単位の平均CERのみを示した棒グラフ作成スクリプト
実験結果１の統計分析結果を示す際に使用
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

def create_sentence_cer_graph():
    """文単位の平均CERのみを示した棒グラフを作成する"""
    
    # ファイルパスの設定
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "statistical data"
    input_file = data_dir / "table2.csv"
    
    # データの読み込み
    df = pd.read_csv(input_file, skiprows=1)  # ヘッダー行をスキップ
    
    # 列名の正規化（12列に対応）
    df.columns = ['測定回', '目標文字列', '入力された文章', '編集距離', 'CER(％)', 
                  '入力時間（秒）', 'CPS（文字/秒）', '文字数', 'col9', 'col10', 'col11', 'col12']
    
    # CERの%記号を除去して数値に変換
    df['CER(％)'] = df['CER(％)'].str.replace('%', '').astype(float)
    
    # 文番号を追加（目標文字列から判定）
    target_mapping = {
        'なかの': 1,
        'ひなた': 2, 
        'ゆめをみる': 3,
        'あさになる': 4,
        'わたしはうたう': 5
    }
    
    df['文番号'] = df['目標文字列'].map(target_mapping)
    
    # 文番号ごとにグループ化して文単位平均CERを計算
    stats_list = []
    
    for sentence_num in range(1, 6):  # 文番号1-5
        sentence_data = df[df['文番号'] == sentence_num]
        
        # 基本情報
        target_text = sentence_data['目標文字列'].iloc[0]
        char_count = sentence_data['文字数'].iloc[0]
        
        # 文単位平均CER
        sentence_cer = sentence_data['CER(％)'].mean()
        
        # 統計情報を辞書に格納
        stats_dict = {
            '文番号': sentence_num,
            '目標文章': target_text,
            '文字数': char_count,
            '文単位平均CER（%）': round(sentence_cer, 2)
        }
        
        stats_list.append(stats_dict)
    
    # DataFrameに変換
    stats_df = pd.DataFrame(stats_list)
    
    # グラフ作成
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    
    # 日本語フォントの設定
    font_name = "MS Gothic"
    plt.rcParams['font.family'] = font_name
    
    # ファイルパスの設定
    graphs_dir = current_dir.parent / "statistical data" / "graphs"
    
    # 文単位平均CERの棒グラフ
    plt.figure(figsize=(10, 6))
    bars = plt.bar(stats_df['文番号'], stats_df['文単位平均CER（%）'], 
                   color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
    plt.xlabel('文番号')
    plt.ylabel('文単位平均CER（%）')
    plt.xticks(stats_df['文番号'], stats_df['目標文章'])  # 文番号を文章名に変更
    plt.ylim(0, 100)  # 縦軸を0-100%に設定
    plt.grid(True, alpha=0.3)
    
    # バーの上に値を表示
    for bar, value in zip(bars, stats_df['文単位平均CER（%）']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{value:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(graphs_dir / 'sentence_cer_graph.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 縦軸100%版も作成
    plt.figure(figsize=(10, 6))
    bars = plt.bar(stats_df['文番号'], stats_df['文単位平均CER（%）'], 
                   color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
    plt.xlabel('目標文章')
    plt.ylabel('文単位平均CER（%）')
    plt.xticks(stats_df['文番号'], stats_df['目標文章'])  # 文番号を文章名に変更
    plt.ylim(0, 100)  # 縦軸を0-100%に設定
    plt.grid(True, alpha=0.3)
    
    # バーの上に値を表示
    for bar, value in zip(bars, stats_df['文単位平均CER（%）']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{value:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(graphs_dir / 'sentence_cer_graph_100.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"文単位平均CERグラフを作成しました:")
    print(f"  - {graphs_dir / 'sentence_cer_graph.png'}")
    print(f"  - {graphs_dir / 'sentence_cer_graph_100.png'} (縦軸100%版)")
    
    # 統計表も表示
    print("\n=== 文単位平均CER統計表 ===")
    print(stats_df.to_string(index=False))
    
    # --- 平均CPSの算出 ---
    cps_list = []
    for sentence_num in range(1, 6):
        sentence_data = df[df['文番号'] == sentence_num]
        mean_cps = sentence_data['CPS（文字/秒）'].mean()
        cps_list.append(mean_cps)
    stats_df['平均CPS'] = cps_list

    # --- CER棒グラフ＋CPS折れ線グラフ ---
    plt.figure(figsize=(12, 7))
    ax1 = plt.gca()
    bars = ax1.bar(stats_df['文番号'], stats_df['文単位平均CER（%）'], 
                   color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'], label='文単位平均CER（%）')
    ax1.set_xlabel('目標文章')
    ax1.set_ylabel('文単位平均CER（%）')
    ax1.set_xticks(stats_df['文番号'])
    ax1.set_xticklabels(stats_df['目標文章'])
    ax1.set_ylim(0, 100)
    ax1.grid(True, alpha=0.3)
    for bar, value in zip(bars, stats_df['文単位平均CER（%）']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{value:.1f}%', ha='center', va='bottom')

    # 右軸にCPSの折れ線グラフ
    ax2 = ax1.twinx()
    ax2.plot(stats_df['文番号'], stats_df['平均CPS'], color='blue', marker='o', linewidth=2, label='平均CPS（文字/秒）')
    ax2.set_ylabel('平均CPS（文字/秒）', color='blue')
    ax2.tick_params(axis='y', labelcolor='blue')
    ax2.set_ylim(0, max(stats_df['平均CPS'].max() * 1.2, 2))

    # 凡例
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.title('文単位平均CERと平均CPSの推移')
    plt.tight_layout()
    plt.savefig(graphs_dir / 'sentence_cer_cps_graph.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"  - {graphs_dir / 'sentence_cer_cps_graph.png'} (CER棒＋CPS折れ線)")
    
    return stats_df

if __name__ == "__main__":
    # 文単位平均CERグラフの作成
    stats_df = create_sentence_cer_graph() 