import json


def truncate_jsonl(input_file, output_file, start_lines, num_lines):
    with open(input_file) as reader, open(output_file, 'w') as writer:
        for i, line in enumerate(reader):
            if i >= num_lines:
                break
            if i >= start_lines:
                p = json.loads(line)
                p["task_id"]=(i-start_lines)
                writer.write((json.dumps(p) + "\n"))


input_jsonl_file = "../data/codecontests_test.jsonl"
output_jsonl_file = "../data/cut_8590.jsonl"
start_lines = 85
num_lines_to_truncate = 90

truncate_jsonl(input_jsonl_file, output_jsonl_file, start_lines, num_lines_to_truncate)
