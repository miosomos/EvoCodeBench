from openai import OpenAI
import os
from tqdm import tqdm
import time, json
import multiprocessing
import argparse
import anthropic

with open('system_prompt.txt', 'r') as f:
    SYSTEM_PROMPT = f.read().strip()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt_file', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('--model', type=str, required=True)
    parser.add_argument('--moda', type=float, required=True)
    parser.add_argument('--api_key_file', type=str, required=True)

    parser.add_argument('--T', type=float)
    parser.add_argument('--top_p', type=float)
    parser.add_argument('--N', type=int)
    
    return parser.parse_args()


def load_api(path: str):
    api_keys = []
    with open(path, 'r') as f:
        for line in f:
            key = line.strip()
            api_keys.append(key)
    return api_keys


def load_file(path):
    finished_ids = []
    with open(path, 'r') as f:
        for line in f.readlines():
            finished_ids.append(json.loads(line)['namespace'])
    return finished_ids


def gpt_completion(item):
    # idx, prompt_block, api_key, params, output_path = item 
    idx, args, prompt_block, api_key, output_path = item 
    if 'claude-sonnet-4-20250514' in args.model:
        pass
    elif 'claude-3.5-sonnet-20240620' in args.model:
        pass
    elif 'claude-3.7-sonnet-20250219' in args.model:
        pass
    elif 'claude-sonnet-4-20250514' in args.model:
        client = anthropic.Anthropic(api_key=api_key)
    else:
        client = OpenAI(api_key=api_key)
    if os.path.exists(output_path):
        finished_ids = load_file(output_path) 
        output_f = open(output_path, 'a')
    else:
        finished_ids = []
        output_f = open(output_path, 'w')
    print(f'Worker {idx} start', 'total:', len(prompt_block), 'finished:', len(finished_ids))
    for sample in tqdm(prompt_block, total=len(prompt_block), desc=f'Worker {idx}'):
        sample = json.loads(sample)
        prompt = sample['prompt']
        task_id = sample['namespace']
        if task_id in finished_ids:
            continue

        sample['completion'] = []
        while len(sample['completion']) < args.N:
            flag = False
            while not flag:
                try:
                    if 'claude-3.5-sonnet-20240620' in args.model or 'claude-3.7-sonnet-20250219' in args.model or 'claude-sonnet-4-20250514' in args.model:
                        for _ in range(args.N):
                            response = client.messages.create(
                                model=args.model,
                                max_tokens=4096,
                                system=SYSTEM_PROMPT,
                                messages=[
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=args.T,
                            )
                            sample['completion'].append(response.content[0].text)
                    else:
                        if args.T == 0:
                            response = client.chat.completions.create(
                                        model=args.model, 
                                        messages=[
                                            {'role': 'system', 'content': SYSTEM_PROMPT},
                                            {'role': 'user', 'content': prompt}
                                        ],
                                        temperature=args.T,
                                        n = args.N,
                                    )
                        elif args.T > 0:
                            response = client.chat.completions.create(
                                            model=args.model, 
                                            messages=[
                                                {'role': 'system', 'content': SYSTEM_PROMPT},
                                                {'role': 'user', 'content': prompt}
                                            ],
                                            temperature=args.T,
                                            n = args.N,
                                            top_p = args.top_p
                                    )
                        for choice in response.choices:
                            assert choice.message.role == 'assistant'
                            sample['completion'].append(choice.message.content)
                    flag = True
                except Exception as e:
                    print(f'Worker {idx}', e)
                    time.sleep(5)
            time.sleep(5)
        del sample['prompt']
        output_f.write(json.dumps(sample) + '\n')
        output_f.flush()


if __name__ == "__main__":
    args = parse_args()
    print(args)

    if args.model == 'gpt-3.5':
        args.model = 'gpt-3.5-turbo-1106'
    elif args.model == 'gpt-4':
        args.model = 'gpt-4-1106-preview'
    elif args.model == 'gpt-4o':
        args.model = 'gpt-4o-2024-08-06'
    elif args.model == 'gpt-4o-mini':
        args.model = 'gpt-4o-mini-2024-07-18'
    elif args.model == 'claude-3.5-sonnet':
        args.model = 'claude-3.5-sonnet-20240620'
    elif args.model == 'claude-3.7-sonnet':
        args.model = 'claude-3.7-sonnet-20250219'
    elif args.model == 'claude-4-sonnet':
        args.model = 'claude-sonnet-4-20250514'
    else:
        raise ValueError('Invalid model name')
    api_pool = load_api(args.api_key_file)

    if args.moda == 'greedy':
        args.T = 0
        args.top_p = None
        args.N = 1
    elif args.moda == 'sampling':
        args.T = 0.4
        args.top_p = 0.95
        args.N = 20
    
    with open(args.prompt_file, 'r') as f:
        prompt_file = f.readlines()

    task_block = []
    api_num = len(api_pool)
    l = len(prompt_file) // api_num
    for i in range(api_num):
        if i == api_num - 1:
            prompt_block = prompt_file[i*l:]
        else:
            prompt_block = prompt_file[i*l:(i+1)*l]
        api_key = api_pool[i]
        output_path = f'{args.output_dir}/completion_block{i}.jsonl'
        task_block.append((i, args, prompt_block, api_key, output_path))

    pool = multiprocessing.Pool(api_num)
    pool.map(gpt_completion, task_block)