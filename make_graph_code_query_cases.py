import json
import argparse

counters = {}

def to_graph_coder(d: dict):
    path_tuple = d['completion_path'].split('/')
    folder_name = path_tuple[0]
    counter = counters.get(folder_name, 1)
    counters[folder_name] = counter + 1

    graph_coder_format = {
        "prompt": d['contexts_above'] + d['input_code'],
        "metadata": {
            "task_id": folder_name + '/' + str(counter),
            "ground_truth": "",
            "fpath_tuple": path_tuple,
            "line_no": d['contexts_above'].count('\n') + 1,
        },
    }
    return graph_coder_format


def from_prompt_elements_to_graph_coder(from_file: str, to_file: str) -> None:
    with open(from_file, 'r', encoding='utf-8') as infile, open(to_file, 'w', encoding='utf-8') as outfile:
        for line in infile:
            data = to_graph_coder(json.loads(line))
            json_line = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            outfile.write(json_line + '\n')



def main() -> None:
    parser = argparse.ArgumentParser(description="Convert prompt elements to GraphCoder format")
    parser.add_argument('--from_file', type=str, required=True, help="Input file with prompt elements")
    parser.add_argument('--to_file', type=str, required=True, help="Output file in GraphCoder format")
    args = parser.parse_args()

    print('Converting prompt elements to GraphCoder format...')
    from_prompt_elements_to_graph_coder(args.from_file, args.to_file)
    print('Conversion completed.')

if __name__ == "__main__":
    main()
