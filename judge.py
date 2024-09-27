import re
# Regular expression pattern to match numbers \boxed{number}
pattern = re.compile(r'\\boxed{([-+]?[0-9]*\.?[0-9]+)}')

import math

def is_number(s):
    if isinstance(s, bool):
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False
def get_boxed_text(answer, generated_text):
    boxed_text = re.findall(r'\\boxed{(.*?)}', generated_text)
    print("$$$$$$$$$$",boxed_text, answer);
    if not boxed_text:
        return False
    if type(answer) == list:
        answer = str(answer)
    try:
        answer = answer.strip()
    except AttributeError:
        # Handle the case where answer is not a string
        pass
    if isinstance(answer, bool):
        converted_answer = answer
    elif is_number(answer):
        converted_answer = int(float(answer)) if float(answer).is_integer() else float(answer)
    elif answer.lower() in ['true', 'false'] :
        converted_answer = answer.lower() == 'true'
    elif answer.startswith('[') and answer.endswith(']'):
        try:
            converted_answer = eval(answer)
        except (SyntaxError, NameError):
            converted_answer = [float(x) if is_number(x) else str(x) for x in answer.strip('[]').split()]

    else:
        converted_answer = answer.strip()
    
    try:
        if answer.startswith("'"):
            answer = answer[1:-1]
    except AttributeError:
        pass

    margin = 1e-6  # Use an even stricter margin for comparisons

    for text in boxed_text:
        if text == answer:
            return True
        text = text.strip()
        if text.startswith("'"):
            text = text[1:-1]
        
        # Boolean Check
        if isinstance(converted_answer, bool):
            if text.lower() in ['true', 'false']:
                text_bool = text.lower() == 'true'
                if text_bool == converted_answer:
                    return True
            continue
        
        # Integer and Float Check
        elif isinstance(converted_answer, (int, float)):
            if is_number(text):
                text_num = float(text)
                if isinstance(converted_answer, int):
                    if abs(text_num - converted_answer) < margin:
                        return True
                else:
                    if math.isclose(text_num, converted_answer, rel_tol=margin, abs_tol=margin):
                        return True
        
        # List Check
        elif isinstance(converted_answer, list):
            try:
                # Try to evaluate the text as a list
                # remove all \\
                text = text.replace('\\ ', '')
                try:
                    text_list = eval(text)
                except SyntaxError:
                    text_list = [float(x) if is_number(x) else str(x) for x in text.strip('[]').split()]
                
                if converted_answer == text_list:
                    return True
                if isinstance(text_list, list) and len(text_list) == len(converted_answer):
                    # Compare each element
                    for a, b in zip(text_list, converted_answer):
                        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                            if not math.isclose(a, b, rel_tol=margin, abs_tol=margin):
                                break
                        elif str(a).strip() != str(b).strip():
                            break
                    else:
                        return True
            except (SyntaxError, NameError, ValueError):
                # If eval fails, try splitting by comma
                text_list = [item.strip() for item in text.split(',')]
                if len(text_list) == len(converted_answer):
                    for a, b in zip(text_list, converted_answer):
                        if is_number(a) and isinstance(b, (int, float)):
                            if not math.isclose(float(a), b, rel_tol=margin, abs_tol=margin):
                                break
                        elif a.lower() in ['true', 'false'] and isinstance(b, bool):
                            if (a.lower() == 'true') != b:
                                break
                        elif str(a).strip() != str(b).strip():
                            break
                    else:
                        return True
        
        # String Check
        else:
            if text.strip() == str(converted_answer).strip():
                return True
        
    return False

# Test cases for lists
def test_get_boxed_text_lists():
    # Test case 1: Exact match
    assert get_boxed_text("[1, 2, 3]", r"\boxed{[1, 2, 3]}") == True

    # Test case 2: Different order
    assert get_boxed_text("[1, 2, 3]", r"\boxed{[3, 2, 1]}") == False

    # Test case 3: Close float values
    assert get_boxed_text("[1.000, 2.000, 3.000]", r"\boxed{[1.0, 2.0, 3.0]}") == True

    # Test case 4: Mixed types
    assert get_boxed_text("[1, 'a', True]", r"\boxed{[1, 'a', True]}") == True

    # Test case 5: Nested lists
    assert get_boxed_text("[[1, 2], [3, 4]]", r"\boxed{[[1, 2], [3, 4]]}") == True

    # Test case 6: Empty list
    assert get_boxed_text("[]", r"\boxed{[]}") == True

    # Test case 7: List with one element
    assert get_boxed_text("[42]", r"\boxed{[42]}") == True

    # Test case 8: Large list
    large_list = list(range(1000))
    assert get_boxed_text(str(large_list), r"\boxed{" + str(large_list) + "}") == True

    # Test case 9: List with special characters
    assert get_boxed_text("['!@#', '$%^', '&*()']", r"\boxed{['!@#', '$%^', '&*()']}") == True

    # Test case 10: List with None values
    assert get_boxed_text("[None, 1, None]", r"\boxed{[None, 1, None]}") == True

    print("All list test cases passed!")

# Run the test cases
# test_get_boxed_text_lists()




def code_output_compare(answer, generated_text):
    # remove unnecessary space after comma and new line from answer and generated text
    answer = answer.strip().replace('\n', '').replace(' ', '')
    generated_text = generated_text.strip().replace('\n', '').replace(' ', '')
    if answer in generated_text:
        return True
    else:
        return False


