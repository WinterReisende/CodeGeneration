import os
from src.into import read_problems, llms_generation, run_code, final_count
from src.execution import create_public_code, check_correctness
from src.final_count import process_file
from src.read_json import get_txt


def run_main(dataset, max_round, try_times):
    model = "gpt-4-1106-preview"
    file_name = (dataset + "_" + str(try_times))
    save_path = os.path.join(".", "results", file_name, "tokens_count.txt")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(os.path.join(".", "results", file_name, "tokens_count.txt"), 'w') as file:
        file.write("")
    problems_0 = read_problems(f"./data/{dataset}.jsonl")
    llms_generation("analyze", problems_0, 0, model, "python", file_name, num_samples_per_task=2)
    problems_1 = read_problems(f"./results/{dataset}_{str(try_times)}/analyze_0/{dataset}_{str(try_times)}.jsonl")
    llms_generation("solve", problems_1, 0, model, "python", file_name, num_samples_per_task=3, temperature=0.8)
    problems_2 = read_problems(f"./results/{dataset}_{str(try_times)}/solve_0/{dataset}_{str(try_times)}.jsonl")
    llms_generation("code_multi", problems_2, 0, model, "python", file_name, num_samples_per_task=1)
    problems_3 = read_problems(f"./results/{dataset}_{str(try_times)}/code_multi_0/{dataset}_{str(try_times)}.jsonl")
    run_code(problems_3, "public", 0, file_name, 5.0)
    for i in range(max_round):
        problems_x = read_problems(f"./results/{dataset}_{str(try_times)}/error_{i}/{dataset}_{str(try_times)}.jsonl")
        llms_generation("correct", problems_x, i, model, "python", file_name, num_samples_per_task=1, temperature=0.8)
        problems_x = read_problems(f"./results/{dataset}_{str(try_times)}/correct_{i}/{dataset}_{str(try_times)}.jsonl")
        llms_generation("correct_code", problems_x, i, model, "python", file_name, num_samples_per_task=1, temperature=0.8)
        problems_3 = read_problems(f"./results/{dataset}_{str(try_times)}/correct_code_{i}/{dataset}_{str(try_times)}.jsonl")
        run_code(problems_3, "public", (i+1), file_name, 5.0)
    problems_4 = read_problems(f"./results/{file_name}/error_{max_round}/{file_name}.jsonl")
    run_code(problems_4, "private", max_round, file_name, 60.0)
    problems_5 = read_problems(f"./results/{file_name}/error_final/{file_name}.jsonl")
    final_count(problems_5, max_round, file_name)
    input_file = f"./results/{file_name}/tokens_count.txt"
    output_file = f"./results/{file_name}/final_tokens_count.txt"
    process_file(input_file, output_file)
    get_txt(file_name)


def only_run_code(dataset, max_round, try_times):
    file_name = (dataset + "_" + str(try_times))
    problems_3 = read_problems(f"./results/{file_name}/code_multi_{0}/{file_name}.jsonl")
    run_code(problems_3, "public", 0, file_name, 5.0)
    for i in range(max_round):
        problems_3 = read_problems(f"./results/{file_name}/correct_code_{i}/{file_name}.jsonl")
        run_code(problems_3, "public", i+1, file_name, 5.0)
    problems_4 = read_problems(f"./results/{file_name}/error_{max_round}/{file_name}.jsonl")
    run_code(problems_4, "private", max_round, file_name, 60.0)
    problems_5 = read_problems(f"./results/{file_name}/error_final/{file_name}.jsonl")
    final_count(problems_5, max_round, file_name)
    input_file = f"./results/{file_name}/tokens_count.txt"
    output_file = f"./results/{file_name}/final_tokens_count.txt"
    process_file(input_file, output_file)
    get_txt(file_name)


def run_main_simple(dataset, max_round, try_times):
    model = "gpt-4-1106-preview"
    file_name = (dataset + "_" + str(try_times))
    save_path = os.path.join(".", "results", file_name, "tokens_count.txt")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(os.path.join(".", "results", file_name, "tokens_count.txt"), 'w') as file:
        file.write("")
    problems_0 = read_problems(f"./data/{dataset}.jsonl")
    # llms_generation("analyze", problems_0, 0, model, "python", file_name, num_samples_per_task=2)
    # problems_1 = read_problems(f"./results/{dataset}_{str(try_times)}/analyze_0/{dataset}_{str(try_times)}.jsonl")
    llms_generation("solve", problems_0, 0, model, "python", file_name, num_samples_per_task=1, temperature=0.8)
    problems_2 = read_problems(f"./results/{dataset}_{str(try_times)}/solve_0/{dataset}_{str(try_times)}.jsonl")
    llms_generation("code", problems_2, 0, model, "python", file_name, num_samples_per_task=1)
    problems_3 = read_problems(f"./results/{dataset}_{str(try_times)}/code_0/{dataset}_{str(try_times)}.jsonl")
    run_code(problems_3, "public", 0, file_name, 5.0)
    for i in range(max_round):
        problems_x = read_problems(f"./results/{dataset}_{str(try_times)}/error_{i}/{dataset}_{str(try_times)}.jsonl")
        llms_generation("correct", problems_x, i, model, "python", file_name, num_samples_per_task=1, temperature=0.8)
        problems_x = read_problems(f"./results/{dataset}_{str(try_times)}/correct_{i}/{dataset}_{str(try_times)}.jsonl")
        llms_generation("correct_code", problems_x, i, model, "python", file_name, num_samples_per_task=1, temperature=0.8)
        problems_3 = read_problems(f"./results/{dataset}_{str(try_times)}/correct_code_{i}/{dataset}_{str(try_times)}.jsonl")
        run_code(problems_3, "public", (i+1), file_name, 5.0)
    problems_4 = read_problems(f"./results/{file_name}/error_{max_round}/{file_name}.jsonl")
    run_code(problems_4, "private", max_round, file_name, 60.0)
    problems_5 = read_problems(f"./results/{file_name}/error_final/{file_name}.jsonl")
    final_count(problems_5, max_round, file_name)
    input_file = f"./results/{file_name}/tokens_count.txt"
    output_file = f"./results/{file_name}/final_tokens_count.txt"
    process_file(input_file, output_file)
    get_txt(file_name)


if __name__ == '__main__':
    # only_run_code    run_main
    # run_main_simple("cut_5", 3, 1024)
    model = "gpt-4-1106-preview"
    dataset = "cut_8590"
    try_times = 0
    max_round = 3
    file_name = (dataset + "_" + str(try_times))
    problems_1 = read_problems(f"./results/{dataset}_{str(try_times)}/analyze_0/{dataset}_{str(try_times)}.jsonl")
    llms_generation("correct_analysis", problems_1, 0, model, "python", file_name, num_samples_per_task=2, temperature=0.8)
    get_txt(file_name)
    '''dataset = "cut_2025"
    try_times = 2
    max_round = 3
    file_name = (dataset + "_" + str(try_times))
    problems_4 = read_problems(f"./results/{file_name}/error_{max_round}/{file_name}.jsonl")
    run_code(problems_4, "private_show", max_round, file_name, 60.0)
    model = "gpt-4-1106-preview"
    dataset = "cut_100105"
    try_times = 2
    max_round = 3
    i = 2
    file_name = "cut_100105_2"
    save_path = os.path.join(".", "results", file_name, "tokens_count.txt")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    problems_x = read_problems(f"./results/{dataset}_{str(try_times)}/correct_{i}/{dataset}_{str(try_times)}.jsonl")
    llms_generation("correct_code", problems_x, i, model, "python", file_name, num_samples_per_task=1, temperature=0.2)
    problems_3 = read_problems(
        f"./results/{dataset}_{str(try_times)}/correct_code_{i}/{dataset}_{str(try_times)}.jsonl")
    run_code(problems_3, "public", (i + 1), file_name, 5.0)
    problems_4 = read_problems(f"./results/{file_name}/error_{max_round}/{file_name}.jsonl")
    run_code(problems_4, "private", max_round, file_name, 60.0)
    problems_5 = read_problems(f"./results/{file_name}/error_final/{file_name}.jsonl")
    final_count(problems_5, max_round, file_name)
    input_file = f"./results/{file_name}/tokens_count.txt"
    output_file = f"./results/{file_name}/final_tokens_count.txt"
    process_file(input_file, output_file)
    get_txt(file_name)'''
