import json

def extract_path_from_data(file_path: str) -> list:
    """
    Extracts the completion_path from data.jsonl
    The idea is extract the full path to use it in the
    agent.

    Args:
        file_path (str): The full path to the file.

    Returns:
        list: A list of completion_path values extracted from the file.
    """

    completion_paths = []
    with open(file_path, 'r') as file:
        for line in file:
            data = json.loads(line)
            if 'completion_path' in data:
                completion_paths.append(data['completion_path'])

    return completion_paths

def add_path_to_prompt() -> None:
    """
    Adds the completion_path to each element in prompt_elements.jsonl
    by matching it with the corresponding path from data.jsonl.
    
     Returns:
        None
    """
    
    completion_paths = extract_path_from_data('../data.jsonl')
    
    with open('../prompt/prompt_elements.jsonl', 'r') as infile:
        prompt_elements = [json.loads(line) for line in infile]

    for element, path in zip(prompt_elements, completion_paths):
        element['completion_path'] = path

    with open('../prompt/prompt_elements.jsonl', 'w') as outfile:
        for element in prompt_elements:
            outfile.write(json.dumps(element) + '\n')

add_path_to_prompt()