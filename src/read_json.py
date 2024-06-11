import json
import os
import functools


def process_json(dataset, json_data):
    task_id = json_data.get("task_id")

    for key, item in json_data.items():
        if task_id is not None:
            folder_name = f"./results/{dataset}/txt_show/task_{task_id}"
            os.makedirs(folder_name, exist_ok=True)
            txt_file_path = os.path.join(folder_name, f"{key}.txt")
            with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                item = json_data[key]
                txt_file.write(str(item))
                txt_file.write("\n\n")


def get_txt(file_name):
    # file_name = "cut_2025_3"
    json_file_path = f"./results/{file_name}/correct_analysis_0/{file_name}.jsonl"  # 请替换为你的实际 JSON 文件路径
    # json_file_path = "../data/codecontests_val.jsonl"
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        for line in json_file:
            json_data = json.loads(line)
            process_json(file_name, json_data)
    print("Files created successfully.")
