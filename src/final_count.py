def calculate_cost(task_numbers, prompt_tokens, completion_tokens):
    cost = (prompt_tokens / 1000) * 0.01 + (completion_tokens / 1000) * 0.03
    return cost, cost / task_numbers


def process_line(line):
    parts = line.split()
    task_numbers = int(parts[1])
    prompt_tokens = int(parts[3])
    completion_tokens = int(parts[5])

    cost, cost_per_problem = calculate_cost(task_numbers, prompt_tokens, completion_tokens)

    result_line = f"{line.strip()} cost: {cost:.5f}  cost_per_problem: {cost_per_problem:.6f}\n"

    return cost, cost_per_problem


def process_file(input_file, output_file):
    total_cost = 0
    total_cost_per_problem = 0

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        m = 2
        t = 1
        for line in infile:
            if t == 1:
                t = 2
                outfile.write(line)
                continue
            t = 1
            cost, cost_per_problem = process_line(line)
            outfile.write(line.strip() + f"  cost: {cost:.5f}  \tcost_per_problem: {cost_per_problem:.6f}\n")
            total_cost += cost
            total_cost_per_problem += m * cost_per_problem
            if m == 2:
                m = 3
            elif m == 3:
                m = 1

        outfile.write(f"\nTotal Cost: {total_cost:.5f}\nTotal Cost Per Problem: {total_cost_per_problem:.6f}\n")


if __name__ == "__main__":
    input_file = "../results/cut_2025_2/tokens_count.txt"
    output_file = "../results/cut_2025_2/final_tokens_count.txt"

    process_file(input_file, output_file)
