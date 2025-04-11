import pandas as pd

def export_selected_columns(input_path, output_path):
    # 1. 讀取 CSV 檔案
    df = pd.read_csv(input_path)

    # 2. 選取特定欄位
    selected_columns = [
        "experiment.1.player.seat",
        "moralcost.1.player.name",
        "moralcost.1.player.id_number",
        "moralcost.1.player.student_id",
        "moralcost.1.player.address"
    ]
    df_selected = df[selected_columns]

    # 3. 匯出為 UTF-8-BOM CSV
    df_selected.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"✅ 成功匯出：{output_path}")

input_path = "/Users/dylan/Desktop/all_apps_wide-2025-04-10.csv"
output_path = "/Users/dylan/Desktop/test250410_selected.csv"

export_selected_columns(input_path, output_path)
