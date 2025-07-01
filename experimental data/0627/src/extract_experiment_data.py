import json
import csv
import os
from pathlib import Path

def extract_experiment_data():
    """
    実験データからsentenceIndex 1-2のデータを抽出してCSVファイルを作成する
    """
    # パスの設定
    measurement_data_dir = Path("../measurement data")
    output_dir = Path("../statistical data")
    output_file = output_dir / "extracted_experiment_data.csv"
    
    # 出力ディレクトリが存在しない場合は作成
    output_dir.mkdir(exist_ok=True)
    
    # 抽出するデータを格納するリスト
    extracted_data = []
    
    # すべてのJSONファイルを処理
    for json_file in measurement_data_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            participant_id = data.get("participantId", "")
            
            # experimentDataからsentenceIndex 1-2のデータを抽出
            for experiment in data.get("experimentData", []):
                sentence_index = experiment.get("sentenceIndex", 0)
                
                # sentenceIndex 1-2のみを抽出
                if sentence_index in [1, 2]:
                    extracted_row = {
                        "participantId": participant_id,
                        "sentenceIndex": sentence_index,
                        "originalText": experiment.get("originalText", ""),
                        "inputText": experiment.get("inputText", ""),
                        "inputTime": experiment.get("inputTime", 0),
                        "msd": experiment.get("msd", 0),
                        "cer": experiment.get("cer", 0)
                    }
                    extracted_data.append(extracted_row)
                    
        except Exception as e:
            print(f"エラー: {json_file}の処理中にエラーが発生しました: {e}")
    
    # CSVファイルに書き出し
    if extracted_data:
        fieldnames = ["participantId", "sentenceIndex", "originalText", "inputText", "inputTime", "msd", "cer"]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(extracted_data)
        
        print(f"データ抽出完了: {len(extracted_data)}件のデータを{output_file}に保存しました")
        print(f"処理したファイル数: {len(list(measurement_data_dir.glob('*.json')))}")
    else:
        print("抽出されたデータがありません")

if __name__ == "__main__":
    extract_experiment_data() 