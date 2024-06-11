import concurrent
import json
import re

from tqdm import tqdm
import openai
import backoff
import os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from typing import Iterable, Dict
import gzip
import json
import os
import argparse
from src.agent import GPTAgent
from src.execution import check_correctness

GEN_STOP_WORDS = {
    "python": ['deffffffffff'],
}

COR_STOP_WORDS = {
    "python": ['deffffffffff'],
}


def read_problems(problem_file: str) -> Dict[str, Dict]:
    return {task["task_id"]: task for task in stream_jsonl(problem_file)}


def stream_jsonl(filename: str) -> Iterable[Dict]:
    """
    Parses each jsonl line and yields it as a dictionary
    """
    if filename.endswith(".gz"):
        with open(filename, "rb") as gzfp:
            with gzip.open(gzfp, 'rt') as fp:
                for line in fp:
                    if any(not x.isspace() for x in line):
                        yield json.loads(line)
    else:
        with open(filename, "r") as fp:
            for line in fp:
                if any(not x.isspace() for x in line):
                    yield json.loads(line)


def write_jsonl(filename: str, data: Iterable[Dict], append: bool = False):
    """
    Writes an iterable of dictionaries to jsonl
    """
    if append:
        mode = 'ab'
    else:
        mode = 'wb'
    filename = os.path.expanduser(filename)
    if filename.endswith(".gz"):
        with open(filename, mode) as fp:
            with gzip.GzipFile(fileobj=fp, mode='wb') as gzfp:
                for x in data:
                    gzfp.write((json.dumps(x) + "\n").encode('utf-8'))
    else:
        with open(filename, mode) as fp:
            for x in data:
                fp.write((json.dumps(x) + "\n").encode('utf-8'))
                # 然后，对于 data 中的每个字典，将其转换为 JSON 格式的字符串，添加换行符，最后以 UTF-8 编码写入到文件中。


def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content


def code_generation_0(task_id, model, message, max_tokens, temperature, stop):
    generator = GPTAgent(model)
    # Replace the following line with your actual code to generate response
    response, completion_tokens, prompt_tokens = generator(message, max_tokens, temperature, stop)
    # sample = {"task_id": task_id, "completion": response}
    return task_id, response, completion_tokens, prompt_tokens


def generate_analyze_prompt(problem):
    prompt_remind = read_file('./prompt/analyze_and_remind.txt')
    problem_prompt = problem["prompt"]
    messages = [
        {"role": "user", "content": problem_prompt},
        {"role": "system", "content": prompt_remind},
    ]
    return messages


def generate_cor_analyze_prompt(problem):
    prompt_remind = read_file('./prompt/correct_analysis.txt')
    problem_prompt = problem["prompt"]
    analysis_0 = problem["analysis_0"]
    analysis_1 = problem["analysis_1"]
    messages = [
        {"role": "user", "content": problem_prompt},
        {"role": "user", "content": 'analysis 0:\n' + analysis_0 + '\nanalysis 1:\n' + analysis_1},
        {"role": "system", "content": prompt_remind},
    ]
    return messages


def generate_solve_prompt(problem):
    prompt_solve = read_file('./prompt/get_solution.txt')
    problem_prompt = problem["prompt"]
    # analysis_0 = problem["analysis_0"]
    # analysis_1 = problem["analysis_1"]
    messages = [
        {"role": "user", "content": "This is an really challenging programming problem:" + problem_prompt},
        # {"role": "user", "content": 'Here are crucial insights and hints regarding the problem and examples. \
        #        They have been written by two experienced teachers. Please consider them thoughtfully.\nanalysis 0:\n'
        #                            + analysis_0 + '\nanalysis 1:\n' + analysis_1},
        {"role": "system", "content": prompt_solve},
    ]
    return messages


def generate_code_prompt(problem):
    prompt_code = read_file('./prompt/get_code.txt')
    problem_prompt = problem["prompt"]
    solution = problem["solution_0"]
    # analysis_0 = problem["analysis_0"]
    # analysis_1 = problem["analysis_1"]
    messages = [
        {"role": "user", "content": problem_prompt},
        #{"role": "user", "content": 'Here are crucial insights and hints regarding the problem and examples. \
        #        They have been written by two experienced teachers. Please consider them thoughtfully.\nanalysis 0:\n'
        #                            + analysis_0 + '\nanalysis 1:\n' + analysis_1},
        {"role": "user", "content": 'Here is the solution from your colleagues:\n' + solution},
        {"role": "system", "content": prompt_code},
    ]
    return messages


def generate_code_multi_prompt(problem):
    prompt_code = read_file('./prompt/get_code_from_multiple_solutions.txt')
    problem_prompt = problem["prompt"]
    solution_0 = problem["solution_0"]
    solution_1 = problem["solution_1"]
    solution_2 = problem["solution_2"]
    # analysis_0 = problem["analysis_0"]
    # analysis_1 = problem["analysis_1"]
    messages = [
        {"role": "user", "content": problem_prompt},
        # {"role": "user", "content": 'Here are crucial insights and hints regarding the problem and examples. \
        #        They have been written by two experienced teachers. Please consider them thoughtfully.\nanalysis 0:\n'
        #                            + analysis_0 + '\nanalysis 1:\n' + analysis_1},
        {"role": "user", "content": 'Here are the solutions from your colleagues:\nsolution 0:' + solution_0
                                    + "solution 1:\n\n" + solution_1 + "solution 2:\n\n" + solution_2},
        {"role": "system", "content": prompt_code},
    ]
    return messages


def generate_cor_prompt(problem, round):
    prompt_cor = read_file('./prompt/correct.txt')
    problem_prompt = problem["prompt"]
    solution = problem["solution_0"]
    code = problem[("code_" + str(round))]
    match = re.search(r'```python\s+(.*?)(\s+```)', code, re.DOTALL)
    if match:
        imports_and_solution_function = match.group(1)  # 提取匹配的导入语句和函数代码
    else:
        return
    error_code = problem[("error_" + str(round))]
    # analysis_0 = problem["analysis_0"]
    # analysis_1 = problem["analysis_1"]
    messages = [

        {"role": "user", "content": problem_prompt},
        #{"role": "user", "content": 'Here are crucial insights and hints regarding the problem and examples. \
        #        They have been written by two experienced teachers. Please consider them thoughtfully.\nanalysis 0:\n'
        #                            + analysis_0 + '\nanalysis 1:\n' + analysis_1},
        # {"role": "user", "content": 'Here is the solution from your colleagues:\n' + solution},
        {"role": "user", "content": 'Here is the code from your colleagues:\n' + code},
        {"role": "user", "content":
            'This is the error message obtained when running the code on the public test samples:\n' + error_code},
        {"role": "system", "content": prompt_cor},
    ]
    return messages


def generate_cor_code_prompt(problem, round):
    prompt_code = read_file('./prompt/get_correct_code.txt')
    problem_prompt = problem["prompt"]
    solution = problem[("correct_"+str(round))]
    code = problem[("code_" + str(round))]
    match = re.search(r'```python\s+(.*?)(\s+```)', code, re.DOTALL)
    if match:
        imports_and_solution_function = match.group(1)  # 提取匹配的导入语句和函数代码
    else:
        return []
    messages = [
        {"role": "user", "content": problem_prompt},
        {"role": "user", "content": 'This is the old solution code, which contains some errors:\n' + imports_and_solution_function},
        {"role": "user", "content": 'This is the modification method and new solution provided by your colleague:\n' + solution},
        {"role": "system", "content": prompt_code},
    ]
    return messages


def llms_generation(task_type, problems, task_round, model, language, file_name="codecontests_test", num_samples_per_task=1,
                    max_tokens=4096,
                    temperature=0.8):
    stop = GEN_STOP_WORDS[language]
    samples = [[] for _ in range(len(problems))]

    with ThreadPoolExecutor(max_workers=os.cpu_count() * 3 or 1) as executor:
        tasks = []
        # 使用 submit 方法提交每个任务，返回一个 Future 对象
        for task_id in tqdm(problems, desc="Generating task: " + task_type + str(task_round), total=len(problems)):
            for _ in range(num_samples_per_task):
                if task_type == 'analyze':
                    message = generate_analyze_prompt(problems[task_id])
                elif task_type == 'correct_analysis':
                    message = generate_cor_analyze_prompt(problems[task_id])
                elif task_type == 'solve':
                    message = generate_solve_prompt(problems[task_id])
                elif task_type == 'code':
                    message = generate_code_prompt(problems[task_id])
                elif task_type == 'code_multi':
                    message = generate_code_multi_prompt(problems[task_id])
                elif task_type == 'correct':
                    message = generate_cor_prompt(problems[task_id], task_round)
                elif task_type == 'correct_code':
                    message = generate_cor_code_prompt(problems[task_id], task_round)
                if task_type == 'correct' and problems[task_id][("passed_" + str(task_round))] == True:
                    samples[task_id].append("NULL")
                    continue
                if task_type == 'correct_code' and problems[task_id][("passed_" + str(task_round))] == True:
                    samples[task_id].append(problems[task_id][("code_"+str(task_round))])
                    continue
                tasks.append((task_id, model, message, max_tokens, temperature, stop))

        futures = [executor.submit(code_generation_0, *task) for task in tasks]
        task_numbers = len(futures)
        completion_tokens_0 = 0
        prompt_tokens_0 = 0
        # 使用 as_completed 方法等待任务完成
        with tqdm(total=len(futures), desc='Processing Futures: ' + task_type + str(task_round)) as pbar:
            for future in concurrent.futures.as_completed(futures):
                try:
                    # 从 Future 对象中获取结果
                    task_id, response, completion_tokens, prompt_tokens = future.result()
                    samples[task_id].append(response)
                    completion_tokens_0 += completion_tokens
                    prompt_tokens_0 += prompt_tokens
                except Exception as e:
                    print(f"An error occurred: {e}")
                finally:
                    pbar.update(1)
    print(completion_tokens_0)
    print(prompt_tokens_0)
    with open(os.path.join(".", "results", file_name, "tokens_count.txt"), 'a') as file:
        file.write(f"{task_type}  \n\ttask_numbers: {task_numbers}    \tprompt_tokens: {prompt_tokens_0}  \t"
                   f"completion_tokens: {completion_tokens_0}\t\n")

    samples_1 = []
    for task_id in range(len(samples)):
        current_problem = problems[task_id]
        if task_type == "analyze":
            current_problem["analysis_0"] = samples[task_id][0]
            current_problem["analysis_1"] = samples[task_id][1]
        elif task_type == 'correct_analysis':
            current_problem["analysis_2"] = samples[task_id][0]
            current_problem["analysis_3"] = samples[task_id][1]
        elif task_type == "solve":
            if num_samples_per_task == 1:
                current_problem["solution_0"] = samples[task_id][0]
            else:
                for i in range(num_samples_per_task):
                    current_problem[("solution_"+str(i))] = samples[task_id][i]
        elif task_type == "code":
            current_problem["code_0"] = samples[task_id][0]
        elif task_type == "code_multi":
            current_problem["code_0"] = samples[task_id][0]
        elif task_type == "correct":
            current_problem[("correct_" + str(task_round))] = samples[task_id][0]
        elif task_type == "correct_code":
            current_problem[("code_" + str(task_round+1))] = samples[task_id][0]
        samples_1.append(current_problem)

    save_path = os.path.join(".", "results", file_name, (task_type+"_"+str(task_round)), f"{file_name}.jsonl")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    print("Write the code generation results to file :\n", save_path)
    write_jsonl(save_path, samples_1)


def run_code_0(task_id, problem, task_type, round, timeout):
    result_str, passed = check_correctness(problem, task_type, round, timeout)
    return task_id, result_str, passed


def run_code(problems, task_type, task_round, file_name="codecontests_test", timeout=5.0):
    samples_result = [[] for _ in range(len(problems))]
    samples_passed = [[] for _ in range(len(problems))]

    with ThreadPoolExecutor(max_workers=os.cpu_count() * 3 or 1) as executor:
        tasks = []
        # 使用 submit 方法提交每个任务，返回一个 Future 对象
        for task_id in tqdm(problems, desc="Generating code", total=len(problems)):
            tasks.append((task_id, problems[task_id], task_type, task_round, timeout))
        futures = [executor.submit(run_code_0, *task) for task in tasks]
        with tqdm(total=len(futures), desc='Processing Futures:' + task_type + str(task_round)) as pbar:
            for future in concurrent.futures.as_completed(futures):
                try:
                    task_id, result_str, passed = future.result()
                    samples_result[task_id].append(result_str)
                    samples_passed[task_id].append(passed)
                except Exception as e:
                    print(f"An error occurred: {e}")
                finally:
                    pbar.update(1)
    samples_1 = []
    for task_id in range(len(samples_result)):
        if task_type == 'public':
            key_0 = ("passed_" + str(task_round))
            key_1 = ("error_" + str(task_round))
        else:
            key_0 = "passed_final"
            key_1 = "error_final"
        problems[task_id][key_0] = samples_passed[task_id][0]
        problems[task_id][key_1] = samples_result[task_id][0]
        samples_1.append(problems[task_id])

    if task_type == 'public':
        save_path = os.path.join(".", "results", file_name, f"error_{str(task_round)}/{file_name}.jsonl")
    else:
        save_path = os.path.join(".", "results", file_name, f"error_final/{file_name}.jsonl")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    count_passed_problems(samples_passed, os.path.join(".", "results", file_name, "passed_info.txt"))
    print("Write the code generation results to file :\n", save_path)
    write_jsonl(save_path, samples_1)


def count_passed_problems(samples_passed, output_file):
    passed_count = 0
    failed_count = 0

    with open(output_file, 'w') as file:
        for idx, passed_list in enumerate(samples_passed):
            if passed_list and passed_list[0]:
                passed_count += 1
                file.write(f"Problem {idx}: Passed\n")
            else:
                failed_count += 1
                file.write(f"Problem {idx}: Failed\n")
        file.write(f"\nTotal Passed: {passed_count}\n")
        file.write(f"Total Failed: {failed_count}\n")

    print(f"Total Passed: {passed_count}")
    print(f"Total Failed: {failed_count}")
    print(f"Results written to: {output_file}")


def final_count(problems, task_round, file_name="codecontests_test"):
    passed_count = 0
    failed_count = 0
    with open(os.path.join(".", "results", file_name, "final_count.txt"), 'w') as file:
        for i in range(len(problems)):
            file.write(f"Problem {str(i)}:")
            for j in range(task_round+1):
                file.write(f" {str(0 if not problems[i][('passed_'+str(j))] else 1)} ")
            file.write(f" final test:")
            file.write(f" {str(0 if not problems[i]['passed_final'] else 1)} \n")
            if problems[i]['passed_final']:
                passed_count += 1
            else:
                failed_count += 1
        file.write(f"\nTotal Passed: {passed_count}\n")
        file.write(f"Total Failed: {failed_count}\n")

    print(f"Total Passed: {passed_count}")
    print(f"Total Failed: {failed_count}")

