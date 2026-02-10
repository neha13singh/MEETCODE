
import json
import sys
from typing import Dict, Any, List

# Simulating the runner.py logic with local adjustments to debug

def parse_input(input_str: str) -> Dict[str, Any]:
    # Heuristic: split by commas not inside brackets
    # This is a complex parser challenge. For now, let's assume we can eval it?
    # NO, evaling "nums = [1,2], target = 9" is tricky in python.
    # Better: Pre-process input string into kwargs dict
    
    # User input examples: "nums = [2,7,11,15], target = 9"
    # We want to call func(nums=[2,7,11,15], target=9)
    
    # HACK: Wrap in dict syntax and eval?
    # "{nums = [2,7...]}" is invalid.
    # "dict(nums = [2,7...])" -> eval("dict(" + input_str + ")") might work!
    
    try:
        # Construct a call to a dummy function or dict constructor
        # Note: this is dangerous if input is malicious, but we are inside a docker container
        # Let's try to extract key-values.
        
        # Safe-ish way: eval the string as arguments to a lambda
        # lambda nums, target: (nums, target) 
        # But we don't know the arg names in advance? 
        # Actually we don't strictly *need* to know arg names if we just pass as kwargs
        
        pass
    except Exception:
        pass
    return {}

data = {
    "code": """
class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        print("Running twoSum")
        d = {}
        for i, n in enumerate(nums):
            diff = target - n
            if diff in d:
                return [d[diff], i]
            d[n] = i
        return []
    """,
    "test_cases": [
        {
            "id": "1",
            "input": "nums = [2,7,11,15], target = 9",
            "expected_output": "[0,1]"
        }
    ]
}

def reproduce():
    code = data['code']
    test_cases = data['test_cases']
    
    local_scope = {}
    try:
        exec(code, {}, local_scope)
        
        # Check for Solution class
        if 'Solution' in local_scope:
            cls = local_scope['Solution']
            instance = cls()
            # Find the method - usually the one that isn't __init__
            method_name = [m for m in dir(instance) if not m.startswith('__')][0]
            solve_func = getattr(instance, method_name)
            print(f"Found method: {method_name}")
        elif 'solve' in local_scope:
            solve_func = local_scope['solve']
        else:
            print("No Solution class or solve function found")
            return

        for tc in test_cases:
            input_str = tc['input']
            # TRYING TO PARSE INPUT
            # input_str is "nums = [2,7,11,15], target = 9"
            
            # Technique: eval("dict(" + input_str + ")")
            try:
                # We need to trust the input format somewhat.
                kwargs = eval(f"dict({input_str})", {"__builtins__": None, "dict": dict, "list": list}, {})
                print(f"Parsed kwargs: {kwargs}")
                
                result = solve_func(**kwargs)
                print(f"Result: {result}")
                
                # Check match
                expected = json.loads(tc['expected_output']) # Parse JSON expected
                # If result is list, compare lists
                
                print(f"Match: {result == expected}")
                
            except Exception as e:
                print(f"Error parsing/running: {e}")

    except Exception as e:
        print(f"Exec faied: {e}")

if __name__ == "__main__":
    reproduce()
