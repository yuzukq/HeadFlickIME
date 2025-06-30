#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
標準偏差を使用した統計表作成スクリプト
目標文章、MSD標準偏差、平均CER、CPS、入力時間標準偏差の構成
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

def create_std_statistics():
    """標準偏差を使用した統計表を作成する"""
    
    # ファイルパスの設定
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "statistical data"
    input_file = data_dir / "figre1.csv"
    output_file = data_dir / "std_statistics.csv"
    
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
    
    # 文番号ごとにグループ化して統計を計算
    stats_list = []
    
    for sentence_num in range(1, 6):  # 文番号1-5
        sentence_data = df[df['文番号'] == sentence_num]
        
        # 基本情報
        target_text = sentence_data['目標文字列'].iloc[0]
        
        # 統計計算
        msd_std = sentence_data['編集距離'].std()  # MSDの標準偏差
        mean_cer = sentence_data['CER(％)'].mean()  # 平均CER（文章単位）
        mean_cps = sentence_data['CPS（文字/秒）'].mean()  # 平均CPS
        time_std = sentence_data['入力時間（秒）'].std()  # 入力時間の標準偏差
        
        # 統計情報を辞書に格納
        stats_dict = {
            '目標文章': target_text,
            'MSD標準偏差': round(msd_std, 3),
            '平均CER（%）': round(mean_cer, 2),
            '平均CPS（文字/秒）': round(mean_cps, 3),
            '入力時間標準偏差（秒）': round(time_std, 3)
        }
        
        stats_list.append(stats_dict)
    
    # DataFrameに変換
    stats_df = pd.DataFrame(stats_list)
    
    # CSVファイルとして保存
    stats_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"標準偏差統計表を作成しました: {output_file}")
    print("\n=== 標準偏差統計表 ===")
    print(stats_df.to_string(index=False))
    
    return stats_df

def create_std_statistics_graph(stats_df):
    """標準偏差統計グラフを作成する"""
    
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    
    # 日本語フォントの設定
    font_name = "MS Gothic"
    plt.rcParams['font.family'] = font_name
    
    # ファイルパスの設定
    current_dir = Path(__file__).parent
    graphs_dir = current_dir.parent / "statistical data" / "graphs"
    
    # グラフ1: MSD標準偏差の比較
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(1, 6), stats_df['MSD標準偏差'], 
                   color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
    plt.xlabel('文番号')
    plt.ylabel('MSD標準偏差')
    plt.xticks(range(1, 6), range(1, 6))
    plt.grid(True, alpha=0.3)
    
    # バーの上に値を表示
    for bar, value in zip(bars, stats_df['MSD標準偏差']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, 
                f'{value:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(graphs_dir / 'msd_std_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # グラフ2: 入力時間標準偏差の比較
    plt.figure(figsize=(10, 6))
    bars = plt.bar(range(1, 6), stats_df['入力時間標準偏差（秒）'], 
                   color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
    plt.xlabel('文番号')
    plt.ylabel('入力時間標準偏差（秒）')
    plt.xticks(range(1, 6), range(1, 6))
    plt.grid(True, alpha=0.3)
    
    # バーの上に値を表示
    for bar, value in zip(bars, stats_df['入力時間標準偏差（秒）']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
                f'{value:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(graphs_dir / 'time_std_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"標準偏差グラフを作成しました:")
    print(f"  - {graphs_dir / 'msd_std_comparison.png'}")
    print(f"  - {graphs_dir / 'time_std_comparison.png'}")

if __name__ == "__main__":
    # 標準偏差統計表の作成
    stats_df = create_std_statistics()
    
    # 標準偏差グラフの作成
    try:
        create_std_statistics_graph(stats_df)
    except ImportError:
        print("matplotlibがインストールされていないため、グラフの作成をスキップしました。")
    except Exception as e:
        print(f"グラフ作成中にエラーが発生しました: {e}") 