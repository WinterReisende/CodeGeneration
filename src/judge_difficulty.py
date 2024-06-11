from into import stream_jsonl, read_problems, read_file
from src.agent import GPTAgent


def generate_prompt(problems):
    prompt_remind = read_file('../prompt/judge_difficulty.txt')
    prompt_0 = ""
    for i in range(len(problems)):
        prompt_0 += "\n\nproblem"
        prompt_0 += str(i)
        prompt_0 += ":\n"
        prompt_0 += problems[i]
    messages = [
        {"role": "system", "content": prompt_remind},
        {"role": "user", "content": prompt_0},
    ]
    return messages


def judge():
    problems = []
    problems_0 = read_problems(f"../data/cut_5.jsonl")
    for i in range(len(problems_0)):
        problems.append(problems_0[i]["prompt"])
    problems_1 = read_problems(f"../data/cut_2025.jsonl")
    for i in range(len(problems_1)):
        problems.append(problems_1[i]["prompt"])
    problems_2 = read_problems(f"../data/cut_8590.jsonl")
    for i in range(len(problems_2)):
        problems.append(problems_2[i]["prompt"])
    problems_3 = read_problems(f"../data/cut_100105.jsonl")
    for i in range(len(problems_3)):
        problems.append(problems_3[i]["prompt"])
    print(len(problems))
    message = generate_prompt(problems)
    model = "gpt-4-1106-preview"
    generator = GPTAgent(model)
    # Replace the following line with your actual code to generate response
    response, completion_tokens, prompt_tokens = generator(message, 4096, 0.2, "xxxxxxxxxx")
    # sample = {"task_id": task_id, "completion": response}
    print(response)
    print("prompt tokens:"+str(prompt_tokens))
    print("completion tokens:" + str(completion_tokens))
    with open("../results/difficulty_judge_20.txt", 'w') as file:
        file.write(response)

judge()
