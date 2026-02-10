import sys
import json
import base64
import time
from typing import Dict, Any

def run_test_case(func, test_case: Dict[str, Any]) -> Dict[str, Any]:
    input_data = test_case['input']
    expected = test_case['expected_output']
    
    start_time = time.time()
    # Prepare execution environment with typing
    import typing
    exec_globals = {
        'List': typing.List,
        'Dict': typing.Dict,
        'Optional': typing.Optional,
        'str': str,
        'int': int,
        'bool': bool,
        'float': float,
        'list': list,
        'dict': dict,
        'set': set,
    }
    
    # Capture stdout
    from io import StringIO
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    
    try:
        # Parse inputs
        # We handle inputs like 'nums = [1,2], target = 3'
        # Convert to kwargs dict
        try:
             # Basic safe eval environment
             parse_env = {"__builtins__": None, "dict": dict, "list": list, "str": str, "int": int, "bool": bool}
             kwargs = eval(f"dict({input_data})", parse_env, {})
             
             # Execute
             result = func(**kwargs)
        except Exception as e:
             # Fallback for simple single arg cases if eval fails or not in k=v format
             try:
                result = func(eval(input_data, parse_env, {}))
             except:
                raise ValueError(f"Failed to parse input or execute: {str(e)}")

        sys.stdout = old_stdout
        
        # Output comparison
        # Expected output is typically a JSON string or Python string repr
        try:
            # Try parsing expected as JSON first
            expected_val = json.loads(expected)
        except:
             try:
                 # Try parsing as python literal
                 expected_val = eval(expected, parse_env, {})
             except:
                 expected_val = expected # String comparison fallback

        output = str(result)
        
        # Compare objects if possible, otherwise string
        try:
            passed = result == expected_val
        except:
            passed = str(result).strip() == str(expected).strip()
        
        return {
            'test_case_id': test_case.get('id'),
            'passed': passed,
            'output': output,
            'expected': expected,
            'execution_time': (time.time() - start_time) * 1000,
            'error': None
        }
    except Exception as e:
        sys.stdout = old_stdout # Restore stdout if it wasn't restored
        return {
            'test_case_id': test_case.get('id'),
            'passed': False,
            'output': None,
            'expected': expected,
            'execution_time': (time.time() - start_time) * 1000,
            'error': str(e)
        }

if __name__ == '__main__':
    # Read payload from stdin or file
    # Format: { "code": "...", "test_cases": [...] }
    try:
        input_str = sys.stdin.read()
        data = json.loads(input_str)
        
        code = data['code']
        test_cases = data['test_cases']
        
        # Execute user code to define the function
        # We need to wrap it to avoid polluting namespace
        import typing
        local_scope = {
            'List': typing.List,
            'Dict': typing.Dict,
            'Optional': typing.Optional,
        }
        exec(code, local_scope, local_scope)
        
        if 'Solution' in local_scope:
            cls = local_scope['Solution']
            instance = cls()
            # Find the first public method
            method_name = [m for m in dir(instance) if not m.startswith('__')][0]
            solve_func = getattr(instance, method_name)
        elif 'solve' in local_scope:
            solve_func = local_scope['solve']
        else:
             print(json.dumps([{"error": "Function 'solve' or class 'Solution' not found"}]))
             sys.exit(1)

        results = []
        for tc in test_cases:
            res = run_test_case(solve_func, tc)
            results.append(res)
            
        print(json.dumps(results))
        
    except Exception as e:
        print(json.dumps({"error": f"System Error: {str(e)}"}))
        sys.exit(1)
