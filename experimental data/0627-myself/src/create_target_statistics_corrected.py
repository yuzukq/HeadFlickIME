#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目標文章ごとの統計表作成スクリプト（修正版）
文字単位の集計による正確なCER計算を行う
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path

def create_target_statistics_corrected():
    """文字単位の集計による正確なCER計算で統計表を作成する"""
    
    # ファイルパスの設定
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "statistical data"
    input_file = data_dir / "figre1.csv"
    output_file = data_dir / "target_statistics_corrected.csv"
    
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
        char_count = sentence_data['文字数'].iloc[0]
        
        # 文字単位の集計によるCER計算
        total_chars = sentence_data['文字数'].sum()  # 総文字数
        total_errors = sentence_data['編集距離'].sum()  # 総誤文字数
        corrected_cer = (total_errors / total_chars) * 100  # 文字単位のCER（%）
        
        # 従来の文単位平均CER（比較用）
        traditional_cer = sentence_data['CER(％)'].mean()
        
        # その他の統計計算
        mean_time = sentence_data['入力時間（秒）'].mean()
        var_time = sentence_data['入力時間（秒）'].var()
        mean_speed = sentence_data['CPS（文字/秒）'].mean()
        var_speed = sentence_data['CPS（文字/秒）'].var()
        
        # 測定回数
        measurement_count = len(sentence_data)
        
        # 統計情報を辞書に格納
        stats_dict = {
            '文番号': sentence_num,
            '目標文章': target_text,
            '文字数': char_count,
            '測定回数': measurement_count,
            '総文字数': total_chars,
            '総誤文字数': total_errors,
            '文字単位CER（%）': round(corrected_cer, 2),
            '文単位平均CER（%）': round(traditional_cer, 2),
            'CER差（%）': round(corrected_cer - traditional_cer, 2),
            '平均入力時間（秒）': round(mean_time, 3),
            '入力時間分散': round(var_time, 3),
            '平均入力速度（文字/秒）': round(mean_speed, 3),
            '入力速度分散': round(var_speed, 3)
        }
        
        stats_list.append(stats_dict)
    
    # DataFrameに変換
    stats_df = pd.DataFrame(stats_list)
    
    # CSVファイルとして保存
    stats_df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"修正版統計表を作成しました: {output_file}")
    print("\n=== 目標文章ごとの統計表（修正版）===")
    print(stats_df.to_string(index=False))
    
    # 計算方法の比較を表示
    print("\n=== 計算方法の比較 ===")
    for _, row in stats_df.iterrows():
        print(f"文番号{row['文番号']} ({row['目標文章']}):")
        print(f"  文字単位CER: {row['文字単位CER（%）']}%")
        print(f"  文単位平均CER: {row['文単位平均CER（%）']}%")
        print(f"  差: {row['CER差（%）']}%")
        print()
    
    return stats_df

def create_corrected_statistics_graph(stats_df):
    """修正版統計グラフを作成する"""
    
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    
    # 日本語フォントの設定
    font_name = "MS Gothic"
    plt.rcParams['font.family'] = font_name
    
    # ファイルパスの設定
    current_dir = Path(__file__).parent
    graphs_dir = current_dir.parent / "statistical data" / "graphs"
    
    # グラフ1: 文字単位CERと文単位平均CERの比較
    plt.figure(figsize=(12, 6))
    
    x = np.arange(len(stats_df))
    width = 0.35
    
    bars1 = plt.bar(x - width/2, stats_df['文字単位CER（%）'], width, 
                    label='文字単位CER', color='#FF6B6B', alpha=0.8)
    bars2 = plt.bar(x + width/2, stats_df['文単位平均CER（%）'], width, 
                    label='文単位平均CER', color='#4ECDC4', alpha=0.8)
    
    plt.xlabel('文番号')
    plt.ylabel('CER（%）')
    plt.title('計算方法によるCERの比較')
    plt.xticks(x, stats_df['文番号'])
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # バーの上に値を表示
    for bar, value in zip(bars1, stats_df['文字単位CER（%）']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
    
    for bar, value in zip(bars2, stats_df['文単位平均CER（%）']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(graphs_dir / 'cer_calculation_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # グラフ2: 文字単位CERのみの比較
    plt.figure(figsize=(10, 6))
    bars = plt.bar(stats_df['文番号'], stats_df['文字単位CER（%）'], 
                   color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'])
    plt.xlabel('文番号')
    plt.ylabel('文字単位CER（%）')
    plt.title('目標文章ごとの文字単位CER（%）')
    plt.xticks(stats_df['文番号'])
    plt.grid(True, alpha=0.3)
    
    # バーの上に値を表示
    for bar, value in zip(bars, stats_df['文字単位CER（%）']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{value:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(graphs_dir / 'target_cer_corrected.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"修正版グラフを作成しました:")
    print(f"  - {graphs_dir / 'cer_calculation_comparison.png'}")
    print(f"  - {graphs_dir / 'target_cer_corrected.png'}")

if __name__ == "__main__":
    # 修正版統計表の作成
    stats_df = create_target_statistics_corrected()
    
    # 修正版グラフの作成
    try:
        create_corrected_statistics_graph(stats_df)
    except ImportError:
        print("matplotlibがインストールされていないため、グラフの作成をスキップしました。")
    except Exception as e:
        print(f"グラフ作成中にエラーが発生しました: {e}") 