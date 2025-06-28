import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import os

# フォント名を明示的に指定
font_name = "MS Gothic"
sns.set_style("whitegrid")

def load_sus_data():
    """SUSデータを読み込む"""
    file_path = "experimental data/0627/statistical data/sus_score.csv"
    
    # CSVファイルを読み込み、統計行を除外
    df = pd.read_csv(file_path, encoding='utf-8')
    
    # 統計行（平均、最大、最小、標準偏差、分散）を除外
    stats_keywords = ['平均', '最大', '最小', '標準偏差', '分散']
    df_data = df[~df['測定者'].isin(stats_keywords)].copy()
    
    return df_data

def calculate_detailed_stats(df):
    """詳細な統計情報を計算"""
    stats_results = {}
    
    # SUSスコアの統計
    sus_scores = df['SUSスコア'].astype(float)
    stats_results['sus_score'] = {
        '平均': sus_scores.mean(),
        '中央値': sus_scores.median(),
        '標準偏差': sus_scores.std(),
        '分散': sus_scores.var(),
        '最小値': sus_scores.min(),
        '最大値': sus_scores.max(),
        '四分位範囲': sus_scores.quantile(0.75) - sus_scores.quantile(0.25),
        '歪度': stats.skew(sus_scores),
        '尖度': stats.kurtosis(sus_scores)
    }
    
    # 各設問の統計
    for i in range(1, 11):
        col_name = f'設問{i}'
        if col_name in df.columns:
            question_data = df[col_name].astype(float)
            stats_results[f'q{i}'] = {
                '平均': question_data.mean(),
                '中央値': question_data.median(),
                '標準偏差': question_data.std(),
                '分散': question_data.var(),
                '最小値': question_data.min(),
                '最大値': question_data.max()
            }
    
    return stats_results

def create_visualizations(df):
    """データの可視化を作成"""
    output_dir = "experimental data/0627/statistical data/graphs"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. SUSスコアのヒストグラム
    plt.figure(figsize=(10, 6))
    plt.hist(df['SUSスコア'].astype(float), bins=8, alpha=0.7, color='skyblue', edgecolor='black')
    plt.title("SUSスコアの分布", fontname=font_name, fontsize=14, fontweight='bold')
    plt.xlabel("SUSスコア", fontname=font_name, fontsize=12)
    plt.ylabel("頻度", fontname=font_name, fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/sus_score_histogram.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. SUSスコアのボックスプロット
    plt.figure(figsize=(8, 6))
    plt.boxplot(df['SUSスコア'].astype(float), patch_artist=True, 
                boxprops=dict(facecolor='lightblue', alpha=0.7))
    plt.title("SUSスコアのボックスプロット", fontname=font_name, fontsize=14, fontweight='bold')
    plt.ylabel("SUSスコア", fontname=font_name, fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/sus_score_boxplot.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. 各設問の回答分布
    fig, axes = plt.subplots(2, 5, figsize=(20, 10))
    axes = axes.flatten()
    
    for i in range(1, 11):
        col_name = f'設問{i}'
        if col_name in df.columns:
            question_data = df[col_name].astype(float)
            axes[i-1].hist(question_data, bins=5, alpha=0.7, color='lightcoral', edgecolor='black')
            axes[i-1].set_title(f'設問 {i}', fontname=font_name, fontsize=12, fontweight='bold')
            axes[i-1].set_xlabel('回答', fontname=font_name, fontsize=10)
            axes[i-1].set_ylabel('頻度', fontname=font_name, fontsize=10)
            axes[i-1].grid(True, alpha=0.3)
            axes[i-1].set_xticks(range(1, 6))
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/questions_distribution.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. 設問間の相関行列
    question_cols = [f'設問{i}' for i in range(1, 11) if f'設問{i}' in df.columns]
    if len(question_cols) > 1:
        correlation_matrix = df[question_cols].astype(float).corr()
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": .8})
        plt.title("設問間の相関行列", fontname=font_name, fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(f"{output_dir}/questions_correlation.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    # 5. 時系列プロット
    plt.figure(figsize=(12, 6))
    plt.plot(range(1, len(df)+1), df['SUSスコア'].astype(float), 
             marker='o', linewidth=2, markersize=8, color='darkblue')
    plt.title("SUSスコアの時系列", fontname=font_name, fontsize=14, fontweight='bold')
    plt.xlabel("参加者の順序", fontname=font_name, fontsize=12)
    plt.ylabel("SUSスコア", fontname=font_name, fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/sus_score_timeseries.png", dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"グラフを {output_dir} に保存しました")

def generate_report(df, stats_results):
    """統計レポートを生成"""
    report_path = "experimental data/0627/statistical data/sus_analysis_report.txt"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=== SUS データ分析レポート ===\n\n")
        f.write(f"分析日時: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"データ数: {len(df)}件\n\n")
        
        f.write("=== SUSスコア統計情報 ===\n")
        sus_stats = stats_results['sus_score']
        for key, value in sus_stats.items():
            f.write(f"{key}: {value:.2f}\n")
        
        f.write("\n=== 各設問の統計情報 ===\n")
        for i in range(1, 11):
            if f'q{i}' in stats_results:
                f.write(f"\n設問{i}:\n")
                q_stats = stats_results[f'q{i}']
                for key, value in q_stats.items():
                    f.write(f"  {key}: {value:.2f}\n")
        
        f.write("\n=== データ詳細 ===\n")
        for idx, row in df.iterrows():
            f.write(f"参加者 {row['測定者']}: SUSスコア {row['SUSスコア']}, 時刻 {row['日時']}\n")
        
        # 正規性検定
        sus_scores = df['SUSスコア'].astype(float)
        shapiro_stat, shapiro_p = stats.shapiro(sus_scores)
        f.write(f"\n=== 正規性検定 (Shapiro-Wilk) ===\n")
        f.write(f"統計量: {shapiro_stat:.4f}\n")
        f.write(f"p値: {shapiro_p:.4f}\n")
        f.write(f"正規分布の仮定: {'棄却されない' if shapiro_p > 0.05 else '棄却される'} (α=0.05)\n")
    
    print(f"分析レポートを {report_path} に保存しました")

def main():
    """メイン関数"""
    print("SUSデータの分析を開始します...")
    
    # データ読み込み
    df = load_sus_data()
    print(f"データを読み込みました: {len(df)}件")
    
    # 統計計算
    stats_results = calculate_detailed_stats(df)
    print("統計情報を計算しました")
    
    # 可視化
    create_visualizations(df)
    print("グラフを作成しました")
    
    # レポート生成
    generate_report(df, stats_results)
    print("分析レポートを生成しました")
    
    # コンソール出力
    print("\n=== SUSスコア統計サマリー ===")
    sus_stats = stats_results['sus_score']
    print(f"平均: {sus_stats['平均']:.2f}")
    print(f"中央値: {sus_stats['中央値']:.2f}")
    print(f"標準偏差: {sus_stats['標準偏差']:.2f}")
    print(f"最小値: {sus_stats['最小値']:.2f}")
    print(f"最大値: {sus_stats['最大値']:.2f}")
    
    print("\n分析が完了しました！")

if __name__ == "__main__":
    main() 