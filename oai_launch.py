from openai_handler import openai_generate
from judge import get_boxed_text
from datasets import load_dataset
from datetime import datetime
import os
import json

def evaluate_openai_model(hf_dataset_address: str, openai_model: str, trail_run=False):
    # Load the dataset
    dataset = load_dataset(hf_dataset_address)
    
    # Generate filename for results
    current_date = datetime.now().strftime("%Y-%m-%d")
    dataset_name = hf_dataset_address.split("/")[-1]
    filename = f"{openai_model}-evaluation-{dataset_name}-{current_date}.jsonl"
    
    # Ensure the 'results' directory exists
    os.makedirs('results', exist_ok=True)
    
    correct_array = []
    total_count = 0
    
    with open(os.path.join('results', filename), 'w') as f:
        # Assuming the dataset has a 'train' split. Adjust if needed.
        for i, item in enumerate(dataset['train']):
            if trail_run and i>=3:  # Stop after processing 5 rows
                break
            prompt = item['prompt']
            # Generate output using the OpenAI model
            output = openai_generate([prompt], model=openai_model)[0]
            
            # Evaluate using get_boxed_text
            expected_output = item.get('output') or item.get('answer', '')
            evaluation_result = get_boxed_text(expected_output, output)
            
            correct_array.append(bool(evaluation_result))
            total_count += 1
            
            result = {
                "output": output,
                "expected_output": expected_output,
                "evaluation_result": evaluation_result
            }
            # Write each result as a separate line in JSONL format
            f.write(json.dumps(result) + '\n')
    
    accuracy = (sum(correct_array) / total_count) * 100 if total_count > 0 else 0
    print(f"Evaluation data for {dataset_name} saved to results/{filename}")
    print(f"Accuracy: {accuracy:.2f}%")
    
    # Generate separate JSON with correct array information
    correct_info_filename = f"{openai_model}-correct-info-{dataset_name}-{current_date}.json"
    with open(os.path.join('results', correct_info_filename), 'w') as f:
        json.dump({"correct_array": correct_array}, f)
    print(f"Correct array information saved to results/{correct_info_filename}")

    return accuracy
import argparse

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Evaluate OpenAI model on a Hugging Face dataset.')
    parser.add_argument('--dataset', type=str, default='jyothir/code-hard', help='Hugging Face dataset address')
    parser.add_argument('--model', type=str, default='gpt-4o', help='OpenAI model name')
    parser.add_argument('--trail_run', action='store_true', help='Run a trail with only 5 samples')

    # Parse arguments
    args = parser.parse_args()

    # Example usage with command-line arguments
    accuracy = evaluate_openai_model(args.dataset, args.model, args.trail_run)
    print(f"Final accuracy: {accuracy:.2f}%")

if __name__ == "__main__":
    main()
