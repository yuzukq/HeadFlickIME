import json
import csv
import os
from datetime import datetime

def extract_sus_scores():
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
                
                # タイムスタンプを日時形式に変換（表示用）
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_time = timestamp
                
                sus_data.append({
                    'participant_id': participant_id,
                    'timestamp': timestamp,
                    'formatted_time': formatted_time,
                    'sus_score': sus_score,
                    'filename': filename
                })
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    # タイムスタンプでソート
    sus_data.sort(key=lambda x: x['timestamp'])
    
    # CSVファイルに出力
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['participant_id', 'timestamp', 'formatted_time', 'sus_score', 'filename']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # ヘッダーを書き込み
        writer.writeheader()
        
        # データを書き込み
        for row in sus_data:
            writer.writerow(row)
    
    print(f"SUSスコアデータを {output_file} に出力しました")
    print(f"処理したファイル数: {len(sus_data)}")
    
    # 統計情報を表示
    valid_scores = [float(item['sus_score']) for item in sus_data if item['sus_score'] != 'N/A']
    if valid_scores:
        print(f"SUSスコア統計:")
        print(f"  平均: {sum(valid_scores)/len(valid_scores):.2f}")
        print(f"  最小: {min(valid_scores):.2f}")
        print(f"  最大: {max(valid_scores):.2f}")
        print(f"  有効データ数: {len(valid_scores)}")

if __name__ == "__main__":
    extract_sus_scores() 