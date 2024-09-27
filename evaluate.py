import json
import os
from judge import get_boxed_text
from datasets import load_dataset

def evaluate_accuracy(file_path: str, dataset_address: str) -> float:
    # Load the dataset
    dataset = load_dataset(dataset_address)
    
    correct_count = 0
    total_count = 0
    correct_array = []

    with open(file_path, 'r') as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            output = data.get('output', '')
            
            # Get expected output from the dataset
            expected_output = dataset['train'][i].get('output') or dataset['train'][i].get('answer', '')
            
            # Evaluate using get_boxed_text
            evaluation_result = get_boxed_text(expected_output, output)
            print(evaluation_result)
            
            correct_array.append(bool(evaluation_result))
            if evaluation_result:
                correct_count += 1
            total_count += 1

    accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
    return accuracy, correct_array

def main():
    file_paths = [
        'results/o1-preview-output-code-hard-2024-09-26.jsonl',
        'results/o1-mini-output-code-hard-2024-09-26.jsonl'
    ]
    dataset_address = 'jyothir/code-hard'  # Adjust this if the dataset is different
    
    accuracies = {}
    
    for file_path in file_paths:
        accuracy, correct_array = evaluate_accuracy(file_path, dataset_address)
        model_name = file_path.split('-')[1]  # Extract model name from file path
        accuracies[model_name] = accuracy

        # Generate separate JSON with correct array information
        correct_info_filename = f"{model_name}-correct-info-code-hard-2024-09-26.json"
        
        with open(os.path.join('results', correct_info_filename), 'w') as f:
            json.dump({"correct_array": correct_array}, f)
        print(f"Correct array information saved to results/{correct_info_filename}")

    # Print accuracies of both models at the end
    print("\nFinal Accuracies:")
    for model, accuracy in accuracies.items():
        print(f"{model.capitalize()} model: {accuracy:.2f}%")

if __name__ == "__main__":
    main()



