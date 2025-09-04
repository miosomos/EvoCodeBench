import json
from utils import load_json_data
from argparse import ArgumentParser
import tiktoken

def make_an_extended_block(retrieved_context):
    content = retrieved_context[0]
    # put the file path in the comment
    f_path_comment = f'# The below code fragment can be found in:\n'
    f_paths_str = '# '+'/'.join(retrieved_context[-2]) + '\n'
    # put code lines in the comment
    code_lines = content.splitlines(keepends=True)
    content_lines_comment = [f'# {line.rstrip()}\n' for line in code_lines]
    # aggregate the comment and the code lines
    seperator = '# ' + '-' * 50 + '\n'
    block_str = "".join([f_path_comment, f_paths_str, seperator] + content_lines_comment + [seperator])
    return block_str

def build_retrieval_prompt(case, max_top_k):
    # retrieved example
    num_chosen_context = 0
    retrival_blocks = []
    top_k_context = case['top_k_context']
    for i in range(1, len(top_k_context) + 1):
        retrieval_context = top_k_context[-i]
        if num_chosen_context >= max_top_k:
            break
        block_str = make_an_extended_block(retrieval_context)
        retrival_blocks.insert(0, block_str)
        num_chosen_context += 1
    return ''.join(retrival_blocks)

def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--prompt_element_file", type=str, default='prompt/prompt_elements.jsonl')
    parser.add_argument("--gc_file", type=str)
    parser.add_argument("--output_file", type=str)
    parser.add_argument("--context_window", type=int, default=16384)
    parser.add_argument("--max_tokens", type=int, default=500)
    return parser.parse_args()


def produce_prompt(args, d, tokenizer, gc):
    template = open(f'prompt/template/graph_coder/ChatLM.txt', 'r').read()

    prompt = template.format(
        function_name=d['function_name'],
        context=build_retrieval_prompt(gc, 10),
        contexts_above=d['contexts_above'],
        contexts_below=d['contexts_below'],
        input_code=d['input_code']
    )

    return prompt


def main():
    args = parse_args()
    prompt_elements = load_json_data(args.prompt_element_file)
    gc_file = load_json_data(args.gc_file)
    tokenizer = tiktoken.encoding_for_model("gpt-4")

    with open(args.output_file, 'w') as out:
        for d, gc in zip(prompt_elements, gc_file):
            prompt = produce_prompt(args, d, tokenizer, gc)
            out.write(json.dumps({'namespace': d['namespace'], 'prompt': prompt}) + '\n')

if __name__ == '__main__':
    main()
