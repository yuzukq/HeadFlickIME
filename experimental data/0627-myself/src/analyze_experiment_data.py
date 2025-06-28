import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

font_name = "MS Gothic"

# matplotlibの日本語フォント設定
plt.rcParams['font.family'] = font_name
plt.rcParams['axes.unicode_minus'] = False  # マイナス記号の文字化け防止

# データディレクトリの設定 - 絶対パスを使用
current_dir = Path(__file__).parent
data_dir = current_dir / ".." / "measurement data"
output_dir = current_dir / ".." / "statistical data"
graphs_dir = current_dir / ".." / "statistical data" / "graphs"

# 出力ディレクトリの作成
output_dir.mkdir(exist_ok=True)
graphs_dir.mkdir(exist_ok=True)

def load_experiment_data():
    """全実験データを読み込む"""
    all_data = []
    
    # パスの確認
    print(f"データディレクトリ: {data_dir.absolute()}")
    print(f"データディレクトリが存在するか: {data_dir.exists()}")
    
    json_files = list(data_dir.glob("*.json"))
    print(f"見つかったJSONファイル数: {len(json_files)}")
    
    if len(json_files) == 0:
        print("警告: JSONファイルが見つかりませんでした")
        print("利用可能なファイル:")
        if data_dir.exists():
            for file in data_dir.iterdir():
                print(f"  - {file.name}")
        return []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                experiment_id = json_file.stem
                for exp_data in data['experimentData']:
                    exp_data['experiment_id'] = experiment_id
                    exp_data['timestamp'] = data['timestamp']
                    all_data.append(exp_data)
        except Exception as e:
            print(f"エラー: {json_file} の読み込みに失敗: {e}")
    
    print(f"読み込んだ実験データ数: {len(all_data)}")
    return all_data

def analyze_character_lines():
    """文字行別の分析を行う"""
    data = load_experiment_data()
    
    if len(data) == 0:
        print("警告: データが読み込まれませんでした")
        return pd.DataFrame()
    
    # 文字行の定義
    char_lines = {
        'あ行': ['あ', 'い', 'う', 'え', 'お'],
        'か行': ['か', 'き', 'く', 'け', 'こ'],
        'さ行': ['さ', 'し', 'す', 'せ', 'そ'],
        'た行': ['た', 'ち', 'つ', 'て', 'と'],
        'な行': ['な', 'に', 'ぬ', 'ね', 'の'],
        'は行': ['は', 'ひ', 'ふ', 'へ', 'ほ'],
        'ま行': ['ま', 'み', 'む', 'め', 'も'],
        'や行': ['や', 'ゆ', 'よ'],
        'ら行': ['ら', 'り', 'る', 'れ', 'ろ'],
        'わ行': ['わ', 'を', 'ん']
    }
    
    # 各文字がどの行に属するかを判定する関数
    def get_char_line(char):
        for line_name, chars in char_lines.items():
            if char in chars:
                return line_name
        return 'その他'
    
    # 各文字の分析結果を格納
    char_analysis = []
    
    for exp_data in data:
        original_text = exp_data['originalText']
        input_text = exp_data['inputText']
        input_time = exp_data['inputTime']
        accuracy = exp_data['accuracy']
        msd = exp_data['msd']
        
        # 各文字について分析
        for i, (orig_char, input_char) in enumerate(zip(original_text, input_text)):
            char_line = get_char_line(orig_char)
            is_correct = orig_char == input_char
            
            char_analysis.append({
                'experiment_id': exp_data['experiment_id'],
                'sentence_index': exp_data['sentenceIndex'],
                'original_text': original_text,
                'input_text': input_text,
                'char_index': i,
                'original_char': orig_char,
                'input_char': input_char,
                'char_line': char_line,
                'is_correct': is_correct,
                'input_time': input_time,
                'accuracy': accuracy,
                'msd': msd,
                'char_time_per_char': input_time / len(original_text)
            })
    
    df = pd.DataFrame(char_analysis)
    print(f"文字分析データフレームの形状: {df.shape}")
    if len(df) > 0:
        print(f"文字行の種類: {df['char_line'].unique()}")
    return df

def create_summary_table():
    """実験結果のサマリーテーブルを作成"""
    data = load_experiment_data()
    
    if len(data) == 0:
        print("警告: データが読み込まれませんでした")
        return pd.DataFrame()
    
    summary_data = []
    for exp_data in data:
        summary_data.append({
            'experiment_id': exp_data['experiment_id'],
            'sentence_index': exp_data['sentenceIndex'],
            'original_text': exp_data['originalText'],
            'input_text': exp_data['inputText'],
            'input_time': exp_data['inputTime'],
            'speed': exp_data['speed'],
            'accuracy': exp_data['accuracy'],
            'msd': exp_data['msd'],
            'cer': exp_data['cer'],
            'char_count': len(exp_data['originalText'])
        })
    
    df = pd.DataFrame(summary_data)
    
    # CSVファイルとして保存（保存時のみ列名を日本語に変更）
    df_japanese = df.rename(columns={
        'experiment_id': '実験ID',
        'sentence_index': '文番号',
        'original_text': '元テキスト',
        'input_text': '入力テキスト',
        'input_time': '入力時間（秒）',
        'speed': '入力速度（文字/分）',
        'accuracy': '正解率（%）',
        'msd': 'MSD',
        'cer': 'CER',
        'char_count': '文字数'
    })
    
    output_file = output_dir / "experiment_summary.csv"
    df_japanese.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    return df

def analyze_direction_patterns():
    """縦方向・横方向の移動パターン分析"""
    data = load_experiment_data()
    
    if len(data) == 0:
        print("警告: データが読み込まれませんでした")
        return pd.DataFrame()
    
    # 縦方向移動のみの文字列
    vertical_only = ['なかの']  # 縦方向のみ
    horizontal_only = ['ひなた']  # 横方向のみ
    
    direction_analysis = []
    
    for exp_data in data:
        original_text = exp_data['originalText']
        input_text = exp_data['inputText']
        input_time = exp_data['inputTime']
        accuracy = exp_data['accuracy']
        msd = exp_data['msd']
        
        # 移動方向の判定
        if original_text in vertical_only:
            direction = '縦方向のみ'
        elif original_text in horizontal_only:
            direction = '横方向のみ'
        else:
            direction = '複合方向'
        
        direction_analysis.append({
            'experiment_id': exp_data['experiment_id'],
            'sentence_index': exp_data['sentenceIndex'],
            'original_text': original_text,
            'input_text': input_text,
            'direction': direction,
            'input_time': input_time,
            'accuracy': accuracy,
            'msd': msd,
            'char_count': len(original_text),
            'time_per_char': input_time / len(original_text)
        })
    
    return pd.DataFrame(direction_analysis)

def create_visualizations(char_df, summary_df, direction_df):
    """グラフの作成"""
    
    # データが空の場合はスキップ
    if len(char_df) == 0 or len(summary_df) == 0 or len(direction_df) == 0:
        print("警告: データが不足しているため、グラフを作成できません")
        return
    
    # 文字行の順序を定義
    char_lines_order = ['あ行', 'か行', 'さ行', 'た行', 'な行', 'は行', 'ま行', 'や行', 'ら行', 'わ行']
    
    # 2. 文字行別の正解率
    plt.figure(figsize=(12, 8))
    accuracy_by_line = char_df.groupby('char_line')['is_correct'].mean().reindex(char_lines_order)
    accuracy_by_line = accuracy_by_line.dropna()
    
    if len(accuracy_by_line) > 0:
        bars = plt.bar(accuracy_by_line.index, accuracy_by_line.values * 100, color='skyblue')
        plt.title('文字行別の正解率', fontname=font_name, fontsize=16)
        plt.xlabel('文字行', fontname=font_name, fontsize=14)
        plt.ylabel('正解率（%）', fontname=font_name, fontsize=14)
        plt.xticks(rotation=45, fontname=font_name)
        
        # バーの上に値を表示
        for bar, value in zip(bars, accuracy_by_line.values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{value*100:.1f}%', ha='center', va='bottom', fontname=font_name)
        
        plt.tight_layout()
        plt.savefig(graphs_dir / "char_line_accuracy_bar.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    # 3. 移動方向別の入力時間比較
    plt.figure(figsize=(10, 6))
    direction_means = direction_df.groupby('direction')['time_per_char'].mean()
    direction_stds = direction_df.groupby('direction')['time_per_char'].std()
    
    if len(direction_means) > 0:
        bars = plt.bar(direction_means.index, direction_means.values, 
                       yerr=direction_stds.values, capsize=5, color=['lightcoral', 'lightgreen', 'lightblue'])
        plt.title('移動方向別の1文字あたりの入力時間', fontname=font_name, fontsize=16)
        plt.xlabel('移動方向', fontname=font_name, fontsize=14)
        plt.ylabel('入力時間（秒/文字）', fontname=font_name, fontsize=14)
        plt.xticks(fontname=font_name)
        
        # バーの上に値を表示
        for bar, value, std in zip(bars, direction_means.values, direction_stds.values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{value:.3f}±{std:.3f}', ha='center', va='bottom', fontname=font_name)
        
        plt.tight_layout()
        plt.savefig(graphs_dir / "direction_input_time_comparison.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    # 4. 実験回数別の学習効果
    plt.figure(figsize=(12, 6))
    
    # 実験IDを時系列順にソート
    summary_df['experiment_order'] = summary_df['experiment_id'].str.extract(r'(\d{4}-\d{2}-\d{2})').astype(str)
    summary_df = summary_df.sort_values('experiment_order')
    
    # 実験回数別の平均入力時間
    experiment_avg = summary_df.groupby('experiment_order').agg({
        'input_time': 'mean',
        'accuracy': 'mean',
        'msd': 'mean'
    }).reset_index()
    
    if len(experiment_avg) > 0:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 入力時間の推移
        ax1.plot(range(1, len(experiment_avg) + 1), experiment_avg['input_time'], 'o-', linewidth=2, markersize=8)
        ax1.set_title('実験回数別の平均入力時間', fontname=font_name, fontsize=14)
        ax1.set_xlabel('実験回数', fontname=font_name, fontsize=12)
        ax1.set_ylabel('平均入力時間（秒）', fontname=font_name, fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # 精度の推移
        ax2.plot(range(1, len(experiment_avg) + 1), experiment_avg['accuracy'], 'o-', linewidth=2, markersize=8, color='orange')
        ax2.set_title('実験回数別の平均精度', fontname=font_name, fontsize=14)
        ax2.set_xlabel('実験回数', fontname=font_name, fontsize=12)
        ax2.set_ylabel('平均精度（%）', fontname=font_name, fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(graphs_dir / "learning_effect_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()

def create_detailed_analysis_report(char_df, summary_df, direction_df):
    """詳細な分析レポートを作成"""
    
    report_lines = []
    report_lines.append("=== HeadFlickIME 実験データ分析レポート ===")
    report_lines.append("")
    
    if len(summary_df) == 0:
        report_lines.append("警告: データが読み込まれませんでした")
        return report_lines
    
    # 基本統計
    report_lines.append("【基本統計】")
    report_lines.append(f"総実験回数: {len(summary_df['experiment_id'].unique())}")
    report_lines.append(f"総入力文字列数: {len(summary_df)}")
    report_lines.append(f"平均入力時間: {summary_df['input_time'].mean():.3f}秒")
    report_lines.append(f"平均精度: {summary_df['accuracy'].mean():.1f}%")
    report_lines.append(f"平均MSD: {summary_df['msd'].mean():.2f}")
    report_lines.append("")
    
    if len(char_df) > 0:
        # 文字行別分析
        report_lines.append("【文字行別分析】")
        char_line_stats = char_df.groupby('char_line').agg({
            'char_time_per_char': ['mean', 'std'],
            'is_correct': 'mean'
        }).round(4)
        
        for line in ['あ行', 'か行', 'さ行', 'た行', 'な行', 'は行', 'ま行', 'や行', 'ら行', 'わ行']:
            if line in char_line_stats.index:
                mean_time = char_line_stats.loc[line, ('char_time_per_char', 'mean')]
                std_time = char_line_stats.loc[line, ('char_time_per_char', 'std')]
                accuracy = char_line_stats.loc[line, ('is_correct', 'mean')] * 100
                report_lines.append(f"{line}: 平均時間 {mean_time:.3f}±{std_time:.3f}秒/文字, 正解率 {accuracy:.1f}%")
        
        report_lines.append("")
        
        # 左右比較分析
        report_lines.append("【左右比較分析】")
        left_lines = ['あ行', 'か行', 'た行', 'な行', 'は行', 'ま行', 'や行']  # 左側の文字行
        right_lines = ['さ行', 'ら行', 'わ行']  # 右側の文字行
        
        left_data = char_df[char_df['char_line'].isin(left_lines)]
        right_data = char_df[char_df['char_line'].isin(right_lines)]
        
        if len(left_data) > 0 and len(right_data) > 0:
            left_time = left_data['char_time_per_char'].mean()
            right_time = right_data['char_time_per_char'].mean()
            left_acc = left_data['is_correct'].mean() * 100
            right_acc = right_data['is_correct'].mean() * 100
            
            report_lines.append(f"左側文字行（あ行、か行、た行、な行、は行、ま行、や行）:")
            report_lines.append(f"  平均時間: {left_time:.3f}秒/文字, 正解率: {left_acc:.1f}%")
            report_lines.append(f"右側文字行（さ行、ら行、わ行）:")
            report_lines.append(f"  平均時間: {right_time:.3f}秒/文字, 正解率: {right_acc:.1f}%")
            
            if left_time > right_time:
                report_lines.append(f"左側の方が {left_time - right_time:.3f}秒/文字 遅い（体感と一致）")
            else:
                report_lines.append(f"右側の方が {right_time - left_time:.3f}秒/文字 遅い（体感と逆）")
        
        report_lines.append("")
    
    if len(direction_df) > 0:
        # 移動方向別分析
        report_lines.append("【移動方向別分析】")
        direction_stats = direction_df.groupby('direction').agg({
            'time_per_char': ['mean', 'std'],
            'accuracy': ['mean', 'std']
        }).round(3)
        
        for direction in direction_stats.index:
            mean_time = direction_stats.loc[direction, ('time_per_char', 'mean')]
            std_time = direction_stats.loc[direction, ('time_per_char', 'std')]
            mean_acc = direction_stats.loc[direction, ('accuracy', 'mean')]
            std_acc = direction_stats.loc[direction, ('accuracy', 'std')]
            report_lines.append(f"{direction}: 平均時間 {mean_time:.3f}±{std_time:.3f}秒/文字, 精度 {mean_acc:.1f}±{std_acc:.1f}%")
        
        report_lines.append("")
    
    # 学習効果分析
    report_lines.append("【学習効果分析】")
    experiment_avg = summary_df.groupby('experiment_id').agg({
        'input_time': 'mean',
        'accuracy': 'mean'
    }).sort_index()
    
    if len(experiment_avg) > 1:
        first_time = experiment_avg['input_time'].iloc[0]
        last_time = experiment_avg['input_time'].iloc[-1]
        improvement = ((first_time - last_time) / first_time) * 100
        
        report_lines.append(f"初回平均入力時間: {first_time:.3f}秒")
        report_lines.append(f"最終回平均入力時間: {last_time:.3f}秒")
        report_lines.append(f"改善率: {improvement:.1f}%")
    
    # レポートをファイルに保存
    with open(output_dir / "analysis_report.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    return report_lines

def main():
    """メイン処理"""
    print("実験データの解析を開始します...")
    
    try:
        # データの読み込みと分析
        char_df = analyze_character_lines()
        summary_df = create_summary_table()
        direction_df = analyze_direction_patterns()
        
        if len(char_df) == 0:
            print("エラー: データが読み込まれませんでした。パスを確認してください。")
            return
        
        print(f"文字分析データフレームの列: {char_df.columns.tolist()}")
        
        # 文字行別の統計をCSVに保存
        char_stats = char_df.groupby('char_line').agg({
            'char_time_per_char': ['mean', 'std', 'count'],
            'is_correct': 'mean'
        }).round(4)
        char_stats.columns = ['平均時間', '標準偏差', 'データ数', '正解率']
        char_stats.to_csv(output_dir / "char_line_statistics.csv", encoding='utf-8-sig')
        
        # 移動方向別の統計をCSVに保存
        direction_stats = direction_df.groupby('direction').agg({
            'time_per_char': ['mean', 'std'],
            'accuracy': ['mean', 'std'],
            'msd': ['mean', 'std']
        }).round(3)
        direction_stats.columns = ['平均1文字時間', '1文字時間標準偏差', '平均正解率', '正解率標準偏差', '平均MSD', 'MSD標準偏差']
        direction_stats.to_csv(output_dir / "direction_statistics.csv", encoding='utf-8-sig')
        
        # グラフの作成
        print("グラフを作成中...")
        create_visualizations(char_df, summary_df, direction_df)
        
        # 詳細レポートの作成
        print("分析レポートを作成中...")
        report = create_detailed_analysis_report(char_df, summary_df, direction_df)
        
        print("解析完了！")
        print(f"結果は {output_dir} に保存されました")
        print(f"グラフは {graphs_dir} に保存されました")
        
        # レポートの内容を表示
        print("\n=== 分析レポート ===")
        for line in report:
            print(line)
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
