import json
import csv
import os
import numpy as np
from datetime import datetime

def extract_sus_detailed():
    # 実験データファイルのディレクトリ
    data_dir = "experimental data/0627/measurement data"
    output_file = "experimental data/0627/statistical data/sus_score.csv"
    
    # SUSスコアデータを格納するリスト
    sus_data = []
    
    # ディレクトリ内の全てのJSONファイルを処理
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(data_dir, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 必要な情報を抽出
                participant_id = data.get('participantId', 'N/A')
                timestamp = data.get('timestamp', 'N/A')
                sus_score = data.get('surveySummary', {}).get('sus_score', 'N/A')
                
                # SUS設問の回答を抽出
                sus_responses = data.get('surveyData', {}).get('sus', {})
                
                # タイムスタンプを時刻のみに変換
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_only = dt.strftime('%H:%M:%S')
                except:
                    time_only = 'N/A'
                
                sus_data.append({
                    'participant_id': participant_id,
                    'timestamp': timestamp,
                    'time_only': time_only,
                    'sus_score': sus_score,
                    'q1': sus_responses.get('q1', 'N/A'),
                    'q2': sus_responses.get('q2', 'N/A'),
                    'q3': sus_responses.get('q3', 'N/A'),
                    'q4': sus_responses.get('q4', 'N/A'),
                    'q5': sus_responses.get('q5', 'N/A'),
                    'q6': sus_responses.get('q6', 'N/A'),
                    'q7': sus_responses.get('q7', 'N/A'),
                    'q8': sus_responses.get('q8', 'N/A'),
                    'q9': sus_responses.get('q9', 'N/A'),
                    'q10': sus_responses.get('q10', 'N/A'),
                    'filename': filename
                })
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    # タイムスタンプでソート
    sus_data.sort(key=lambda x: x['timestamp'])
    
    # 統計計算
    valid_scores = [float(item['sus_score']) for item in sus_data if item['sus_score'] != 'N/A']
    valid_responses = {}
    for q in range(1, 11):
        valid_responses[f'q{q}'] = [float(item[f'q{q}']) for item in sus_data if item[f'q{q}'] != 'N/A']
    
    stats = {}
    if valid_scores:
        stats['sus_score'] = {
            'mean': np.mean(valid_scores),
            'min': np.min(valid_scores),
            'max': np.max(valid_scores),
            'std': np.std(valid_scores, ddof=1),
            'var': np.var(valid_scores, ddof=1)
        }
    
    for q in range(1, 11):
        if valid_responses[f'q{q}']:
            stats[f'q{q}'] = {
                'mean': np.mean(valid_responses[f'q{q}']),
                'min': np.min(valid_responses[f'q{q}']),
                'max': np.max(valid_responses[f'q{q}']),
                'std': np.std(valid_responses[f'q{q}'], ddof=1),
                'var': np.var(valid_responses[f'q{q}'], ddof=1)
            }
    
    # CSVファイルに出力
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['測定者', 'SUSスコア', '設問1', '設問2', '設問3', '設問4', '設問5', 
                     '設問6', '設問7', '設問8', '設問9', '設問10', '日時']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # ヘッダーを書き込み
        writer.writeheader()
        
        # データを書き込み
        for row in sus_data:
            writer.writerow({
                '測定者': row['participant_id'],
                'SUSスコア': row['sus_score'],
                '設問1': row['q1'],
                '設問2': row['q2'],
                '設問3': row['q3'],
                '設問4': row['q4'],
                '設問5': row['q5'],
                '設問6': row['q6'],
                '設問7': row['q7'],
                '設問8': row['q8'],
                '設問9': row['q9'],
                '設問10': row['q10'],
                '日時': row['time_only']
            })
        
        # 統計行を追加
        if 'sus_score' in stats:
            writer.writerow({
                '測定者': '平均',
                'SUSスコア': f"{stats['sus_score']['mean']:.2f}",
                '設問1': f"{stats['q1']['mean']:.2f}" if 'q1' in stats else '',
                '設問2': f"{stats['q2']['mean']:.2f}" if 'q2' in stats else '',
                '設問3': f"{stats['q3']['mean']:.2f}" if 'q3' in stats else '',
                '設問4': f"{stats['q4']['mean']:.2f}" if 'q4' in stats else '',
                '設問5': f"{stats['q5']['mean']:.2f}" if 'q5' in stats else '',
                '設問6': f"{stats['q6']['mean']:.2f}" if 'q6' in stats else '',
                '設問7': f"{stats['q7']['mean']:.2f}" if 'q7' in stats else '',
                '設問8': f"{stats['q8']['mean']:.2f}" if 'q8' in stats else '',
                '設問9': f"{stats['q9']['mean']:.2f}" if 'q9' in stats else '',
                '設問10': f"{stats['q10']['mean']:.2f}" if 'q10' in stats else '',
                '日時': ''
            })
            
            writer.writerow({
                '測定者': '最大',
                'SUSスコア': f"{stats['sus_score']['max']:.2f}",
                '設問1': f"{stats['q1']['max']:.2f}" if 'q1' in stats else '',
                '設問2': f"{stats['q2']['max']:.2f}" if 'q2' in stats else '',
                '設問3': f"{stats['q3']['max']:.2f}" if 'q3' in stats else '',
                '設問4': f"{stats['q4']['max']:.2f}" if 'q4' in stats else '',
                '設問5': f"{stats['q5']['max']:.2f}" if 'q5' in stats else '',
                '設問6': f"{stats['q6']['max']:.2f}" if 'q6' in stats else '',
                '設問7': f"{stats['q7']['max']:.2f}" if 'q7' in stats else '',
                '設問8': f"{stats['q8']['max']:.2f}" if 'q8' in stats else '',
                '設問9': f"{stats['q9']['max']:.2f}" if 'q9' in stats else '',
                '設問10': f"{stats['q10']['max']:.2f}" if 'q10' in stats else '',
                '日時': ''
            })
            
            writer.writerow({
                '測定者': '最小',
                'SUSスコア': f"{stats['sus_score']['min']:.2f}",
                '設問1': f"{stats['q1']['min']:.2f}" if 'q1' in stats else '',
                '設問2': f"{stats['q2']['min']:.2f}" if 'q2' in stats else '',
                '設問3': f"{stats['q3']['min']:.2f}" if 'q3' in stats else '',
                '設問4': f"{stats['q4']['min']:.2f}" if 'q4' in stats else '',
                '設問5': f"{stats['q5']['min']:.2f}" if 'q5' in stats else '',
                '設問6': f"{stats['q6']['min']:.2f}" if 'q6' in stats else '',
                '設問7': f"{stats['q7']['min']:.2f}" if 'q7' in stats else '',
                '設問8': f"{stats['q8']['min']:.2f}" if 'q8' in stats else '',
                '設問9': f"{stats['q9']['min']:.2f}" if 'q9' in stats else '',
                '設問10': f"{stats['q10']['min']:.2f}" if 'q10' in stats else '',
                '日時': ''
            })
            
            writer.writerow({
                '測定者': '標準偏差',
                'SUSスコア': f"{stats['sus_score']['std']:.2f}",
                '設問1': f"{stats['q1']['std']:.2f}" if 'q1' in stats else '',
                '設問2': f"{stats['q2']['std']:.2f}" if 'q2' in stats else '',
                '設問3': f"{stats['q3']['std']:.2f}" if 'q3' in stats else '',
                '設問4': f"{stats['q4']['std']:.2f}" if 'q4' in stats else '',
                '設問5': f"{stats['q5']['std']:.2f}" if 'q5' in stats else '',
                '設問6': f"{stats['q6']['std']:.2f}" if 'q6' in stats else '',
                '設問7': f"{stats['q7']['std']:.2f}" if 'q7' in stats else '',
                '設問8': f"{stats['q8']['std']:.2f}" if 'q8' in stats else '',
                '設問9': f"{stats['q9']['std']:.2f}" if 'q9' in stats else '',
                '設問10': f"{stats['q10']['std']:.2f}" if 'q10' in stats else '',
                '日時': ''
            })
            
            writer.writerow({
                '測定者': '分散',
                'SUSスコア': f"{stats['sus_score']['var']:.2f}",
                '設問1': f"{stats['q1']['var']:.2f}" if 'q1' in stats else '',
                '設問2': f"{stats['q2']['var']:.2f}" if 'q2' in stats else '',
                '設問3': f"{stats['q3']['var']:.2f}" if 'q3' in stats else '',
                '設問4': f"{stats['q4']['var']:.2f}" if 'q4' in stats else '',
                '設問5': f"{stats['q5']['var']:.2f}" if 'q5' in stats else '',
                '設問6': f"{stats['q6']['var']:.2f}" if 'q6' in stats else '',
                '設問7': f"{stats['q7']['var']:.2f}" if 'q7' in stats else '',
                '設問8': f"{stats['q8']['var']:.2f}" if 'q8' in stats else '',
                '設問9': f"{stats['q9']['var']:.2f}" if 'q9' in stats else '',
                '設問10': f"{stats['q10']['var']:.2f}" if 'q10' in stats else '',
                '日時': ''
            })
    
    print(f"詳細なSUSデータを {output_file} に出力しました")
    print(f"処理したファイル数: {len(sus_data)}")
    
    # コンソールに統計情報を表示
    if valid_scores:
        print(f"\nSUSスコア統計:")
        print(f"  平均: {stats['sus_score']['mean']:.2f}")
        print(f"  最小: {stats['sus_score']['min']:.2f}")
        print(f"  最大: {stats['sus_score']['max']:.2f}")
        print(f"  標準偏差: {stats['sus_score']['std']:.2f}")
        print(f"  分散: {stats['sus_score']['var']:.2f}")
        print(f"  有効データ数: {len(valid_scores)}")

if __name__ == "__main__":
    extract_sus_detailed() 