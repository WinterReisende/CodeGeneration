'''import argparse
import gzip
import os
from pprint import pprint

import pandas as pd
from tqdm import tqdm
import json
import os.path as osp
import numpy as np  # 添加NumPy的导入


def read_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data.append(json.loads(line))
    return data


def write_jsonl(filename, data, append=False):
    if append:
        mode = 'ab'
    else:
        mode = 'wb'
    filename = os.path.expanduser(filename)
    if filename.endswith(".gz"):
        with open(filename, mode) as fp:
            with gzip.GzipFile(fileobj=fp, mode='wb') as gzfp:
                for x in data:
                    # 将NumPy数组转换为列表
                    x['input_output'] = json.dumps(json.loads(x['input_output']))
                    gzfp.write(x)
    else:
        with open(filename, mode) as fp:
            for x in data:
                # 将NumPy数组转换为列表
                x['input_output'] = json.dumps(json.loads(x['input_output']))
                fp.write(json.dumps(x)+ "\n")


def main(pd_paths, json_path, language=3):
    # ...

pd: [
           'name', 'description', 'public_tests', 'private_tests',
           'generated_tests', 'source', 'difficulty', 'solutions',
           'incorrect_solutions', 'cf_contest_id', 'cf_index', 'cf_points',
           'cf_rating', 'cf_tags', 'is_description_translated',
           'untranslated_description', 'time_limit', 'memory_limit_bytes',
           'input_file', 'output_file'
       ]
       json: [
           'id',
           'instruction',
           'input_output',
           'output',
    ]

    assert not osp.exists(json_path), json_path
    if osp.exists(json_path):
        print(f'rm {json_path}')
        os.system(f'rm {json_path}')

    index = 0
    results = []
    for pd_path in tqdm(pd_paths):
        df = pd.read_parquet(pd_path)

        for _, row in df.iterrows():

            row_dict = row.to_dict()
            # get solution
            output = None
            for lan, sol in zip(row['solutions']['language'],
                                row['solutions']['solution']):
                if lan == language:
                    # 将NumPy数组转换为列表
                    output = sol.tolist() if isinstance(sol, np.ndarray) else sol
            if not output:
                continue

            tests = row['public_tests']
            input_output = {
                'inputs': list(tests['input']),
                'outputs': list(tests['output']),
            }

            data = {
                'id': index,
                'instruction': row['description'],
                'input_output': json.dumps(input_output),
                'output': output,
                **row_dict
            }
            index += 1
            results.append(data)

        write_jsonl(json_path, results)
        print(json_path, len(results))

    write_jsonl(json_path, results)
    print(json_path, len(results))


def create_base_codecontest(src, dst):
    pd_path = [
        f'{src}/test-00000-of-00001-9c49eeff30aacaa8.parquet'
    ]
    json_path = f'{dst}/codecontests_test_all_inf.jsonl'
    main(pd_path, json_path)

    pd_path = [
        f'{src}/valid-00000-of-00001-5e672c5751f060d3.parquet'
    ]
    json_path = f'{dst}/codecontests_val_all_inf.jsonl'
    main(pd_path, json_path)


create_base_codecontest('../data', '../data')
data = read_jsonl("../data/codecontests_test_all_inf.jsonl")
pprint(data[1])
'''


import argparse
import gzip
import os
from pprint import pprint

import pandas as pd
from tqdm import tqdm
import json
import os.path as osp


def read_jsonl(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data.append(json.loads(line))
    return data

def write_jsonl(filename, data, append=False):
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


def main(pd_paths, json_path, language=3):
    '''
    pd: [
        'name', 'description', 'public_tests', 'private_tests',
        'generated_tests', 'source', 'difficulty', 'solutions',
        'incorrect_solutions', 'cf_contest_id', 'cf_index', 'cf_points',
        'cf_rating', 'cf_tags', 'is_description_translated',
        'untranslated_description', 'time_limit', 'memory_limit_bytes',
        'input_file', 'output_file'
    ]
    json: [
        'id',
        'instruction',
        'input_output',
        'output',
    ]
    '''
    assert not osp.exists(json_path), json_path
    if osp.exists(json_path):
        print(f'rm {json_path}')
        os.system(f'rm {json_path}')

    index = 0
    results = []
    for pd_path in tqdm(pd_paths):
        df = pd.read_parquet(pd_path)

        for _, row in df.iterrows():

            # get solution
            output = None
            for lan, sol in zip(row['solutions']['language'],
                                row['solutions']['solution']):
                if lan == language:
                    output = sol
            if not output:
                continue

            public_tests = row['public_tests']
            input_output = {
                'inputs': list(public_tests['input']),
                'outputs': list(public_tests['output']),
            }

            private_tests = row['private_tests']
            private_input_output = {
                'inputs': list(private_tests['input']),
                'outputs': list(private_tests['output']),
            }

            data = {
                'task_id': index,
                'prompt': row['description'],
                'public_input_output': json.dumps(input_output),
                'private_input_output': json.dumps(private_input_output),
                'right_solution': output,
                'generated_tests': row['generated_tests'],
                'source': row['source'],
                'difficulty': row['difficulty'],
                'solutions': row['solutions'],
                'incorrect_solutions': row['incorrect_solutions'],
                'cf_contest_id': row['cf_contest_id'],
                'cf_index': row['cf_index'],
                'cf_points': row['cf_points'],
                'cf_rating': row['cf_rating'],
                'cf_tags': row['cf_tags'],
                'is_description_translated': row['is_description_translated'],
                'untranslated_description': row['untranslated_description'],
                'time_limit': row['time_limit'],
                'memory_limit_bytes': row['memory_limit_bytes'],
                'input_file': row['input_file'],
                'output_file': row['output_file'],

            }
            index += 1
            results.append(data)

    write_jsonl(json_path, results)
    print(json_path, len(results))


def create_base_codecontest(src, dst):
    pd_path = [
        f'{src}/test-00000-of-00001-9c49eeff30aacaa8.parquet'
    ]
    json_path = f'{dst}/codecontests_test_all.jsonl'
    main(pd_path, json_path)

    pd_path = [
        f'{src}/valid-00000-of-00001-5e672c5751f060d3.parquet'
    ]
    json_path = f'{dst}/codecontests_val_all.jsonl'
    main(pd_path, json_path)

create_base_codecontest('../data', '../data')

data = read_jsonl("../data/codecontests_test_all.jsonl")
pprint(data[1])


