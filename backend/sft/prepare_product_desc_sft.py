import pandas as pd
import json
from pathlib import Path
from sklearn.model_selection import train_test_split

base = Path(__file__).resolve().parent

csv_path = base / "product_description_generation" / "test.csv"

df = pd.read_csv(csv_path).dropna(subset=["text1", "text2"]).copy()
df["text1"] = df["text1"].astype(str).str.strip()
df["text2"] = df["text2"].astype(str).str.strip()
df = df[(df["text1"] != "") & (df["text2"] != "")].drop_duplicates(subset=["text1", "text2"]).reset_index(drop=True)

instruction = "你是电商商品文案生成助手。请根据输入的商品卖点词，生成一段自然、流畅、适合商品展示的中文商品描述。"


def to_records(sub_df):
    records = []
    for _, row in sub_df.iterrows():
        records.append({
            "instruction": instruction,
            "input": f"商品卖点词：{row['text1']}",
            "output": row["text2"]
        })
    return records


# 8/1/1 split
train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42, shuffle=True)
val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, shuffle=True)

train_records = to_records(train_df)
val_records = to_records(val_df)
test_records = to_records(test_df)

train_path = base / "sft_json" / "shop_listing_sft_train.json"
val_path = base / "sft_json" / "shop_listing_sft_val.json"
test_path = base / "sft_json" / "shop_listing_sft_test.json"

for path, records in [(train_path, train_records), (val_path, val_records), (test_path, test_records)]:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

dataset_info = {
    "shop_listing_sft_train": {
        "file_name": "shop_listing_sft_train.json",
        "columns": {
            "prompt": "instruction",
            "query": "input",
            "response": "output"
        }
    },
    "shop_listing_sft_val": {
        "file_name": "shop_listing_sft_val.json",
        "columns": {
            "prompt": "instruction",
            "query": "input",
            "response": "output"
        }
    },
    "shop_listing_sft_test": {
        "file_name": "shop_listing_sft_test.json",
        "columns": {
            "prompt": "instruction",
            "query": "input",
            "response": "output"
        }
    }
}

dataset_info_path = base /"sft_json" / "llamafactory_dataset_info.json"
with open(dataset_info_path, "w", encoding="utf-8") as f:
    json.dump(dataset_info, f, ensure_ascii=False, indent=2)

summary = {
    "total_rows_after_clean": len(df),
    "train": len(train_records),
    "val": len(val_records),
    "test": len(test_records),
    "files": [
        str(train_path),
        str(val_path),
        str(test_path),
        str(dataset_info_path),
    ]
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
