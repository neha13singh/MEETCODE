import sys
import json
import os
import subprocess
import time
import re
from typing import List, Dict, Any, Tuple

def run_command(cmd: List[str], timeout: int = 15) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired as e:
        return subprocess.CompletedProcess(cmd, 1, stdout=e.stdout or "", stderr="Timeout Expired (15s)")

def parse_input_to_java(val: Any) -> Tuple[str, str]:
    """Returns (java_type, java_literal)"""
    if isinstance(val, bool):
        return "boolean", str(val).lower()
    if isinstance(val, int):
        return "int", str(val)
    if isinstance(val, float):
        return "double", str(val)
    if isinstance(val, str):
        return "String", f'"{val}"'
    if isinstance(val, list):
        if not val:
            return "int[]", "new int[]{}"
        inner_type, _ = parse_input_to_java(val[0])
        literals = [parse_input_to_java(v)[1] for v in val]
        return f"{inner_type}[]", f"new {inner_type}[]{{{', '.join(literals)}}}"
    return "Object", "null"

def parse_input_to_cpp(val: Any) -> Tuple[str, str]:
    """Returns (cpp_type, cpp_literal)"""
    if isinstance(val, bool):
        return "bool", str(val).lower()
    if isinstance(val, int):
        return "int", str(val)
    if isinstance(val, float):
        return "double", str(val)
    if isinstance(val, str):
        return "string", f'"{val}"'
    if isinstance(val, list):
        if not val:
            return "vector<int>", "{}"
        inner_type, _ = parse_input_to_cpp(val[0])
        literals = [parse_input_to_cpp(v)[1] for v in val]
        return f"vector<{inner_type}>", f"{{{', '.join(literals)}}}"
    return "auto", "nullptr"

def get_method_info(code: str, lang: str) -> Tuple[str, List[str]]:
    """Extract method name and param names from code using simple regex."""
    if lang == "java":
        # Find public method in Solution class
        # Look for public [ReturnType] [MethodName]([Params])
        match = re.search(r"public\s+([\w\[\]<>? ]+)\s+(\w+)\s*\(([^)]*)\)", code)
        if match:
            ret_type = match.group(1).strip()
            method_name = match.group(2)
            params_raw = match.group(3)
            # Param names are after types: int nums -> nums
            params = [p.strip().split()[-1] for p in params_raw.split(",") if p.strip()]
            return method_name, params, ret_type
    elif lang == "cpp":
        # Look for [ReturnType] [MethodName]([Params])
        # We allow spaces in return type for things like 'unsigned int' or 'long long'
        match = re.search(r"([\w\[\]<>?* ]+)\s+(\w+)\s*\(([^)]*)\)\s*\{", code)
        if match:
            ret_type = match.group(1).strip()
            # If it matched 'public:', skip it and search again
            if ret_type == "public":
                match = re.search(r"([\w\[\]<>?* ]+)\s+(\w+)\s*\(([^)]*)\)\s*\{", code[match.end():])
                if match:
                    ret_type = match.group(1).strip()
                    method_name = match.group(2)
                    params_raw = match.group(3)
                else:
                    return "solve", [], "void"
            else:
                method_name = match.group(2)
                params_raw = match.group(3)
            
            # vector<int>& nums -> nums
            params = [p.strip().split()[-1].replace("&", "").replace("*", "") for p in params_raw.split(",") if p.strip()]
            return method_name, params, ret_type
    return "solve", [], "void"

def solve_java(code: str, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # 1. Write Solution.java
    if "class Solution" not in code:
        code = "public class Solution {\n" + code + "\n}"
    
    with open("Solution.java", "w") as f:
        f.write(code)
    
    method_name, param_names, ret_type = get_method_info(code, "java")
    
    # 2. Generate Main.java
    main_code = [
        "import java.util.*;",
        "public class Main {",
        "    private static String __stringify(Object obj) {",
        "        if (obj == null) return \"null\";",
        "        if (obj instanceof Object[]) return Arrays.deepToString((Object[]) obj);",
        "        if (obj instanceof int[]) return Arrays.toString((int[]) obj);",
        "        if (obj instanceof long[]) return Arrays.toString((long[]) obj);",
        "        if (obj instanceof double[]) return Arrays.toString((double[]) obj);",
        "        if (obj instanceof boolean[]) return Arrays.toString((boolean[]) obj);",
        "        if (obj instanceof char[]) return Arrays.toString((char[]) obj);",
        "        return String.valueOf(obj);",
        "    }",
        "    public static void main(String[] args) {",
        "        Solution sol = new Solution();"
    ]
    
    for idx, tc in enumerate(test_cases):
        try:
            parse_env = {"dict": dict, "list": list, "str": str, "int": int, "bool": bool}
            kwargs = eval(f"dict({tc['input']})", {"__builtins__": None}, parse_env)
        except:
            kwargs = {}

        main_code.append(f"        try {{")
        main_code.append(f"            long start = System.currentTimeMillis();")
        
        args_literals = []
        for name in param_names:
            val = kwargs.get(name)
            _, literal = parse_input_to_java(val)
            args_literals.append(literal)
        
        if ret_type == "void":
            main_code.append(f"            sol.{method_name}({', '.join(args_literals)});")
            main_code.append(f"            Object res = \"void\";")
        else:
            main_code.append(f"            Object res = sol.{method_name}({', '.join(args_literals)});")
            
        main_code.append(f"            long end = System.currentTimeMillis();")
        main_code.append(f"            System.out.println(\"__RESULT_{idx}__:\" + __stringify(res) + \"|TIME:\" + (end-start));")
        main_code.append(f"        }} catch (Exception e) {{")
        main_code.append(f"            System.out.println(\"__ERROR_{idx}__:\" + e.getMessage());")
        main_code.append(f"        }}")
        
    main_code.append("    }\n}")
    
    with open("Main.java", "w") as f:
        f.write("\n".join(main_code))

    # 3. Compile and Run
    comp = run_command(["javac", "Solution.java", "Main.java"])
    if comp.returncode != 0:
        return [{"error": "Compile Error", "details": comp.stderr}]
    
    run = run_command(["java", "Main"])
    output = run.stdout + run.stderr
    
    results = []
    for idx, tc in enumerate(test_cases):
        res_match = re.search(fr"__RESULT_{idx}__:([^|]+)\|TIME:(\d+)", output)
        err_match = re.search(fr"__ERROR_{idx}__:(.*)", output)
        
        if res_match:
            val = res_match.group(1).strip()
            time_ms = int(res_match.group(2))
            # Clean up Java's Arrays.toString which adds space after comma [1, 2] -> [1,2] for comparison
            normalized_output = val.replace(", ", ",")
            expected = str(tc['expected_output']).strip().replace(", ", ",")
            passed = normalized_output == expected
            
            results.append({
                "test_case_id": tc.get("id"),
                "passed": passed,
                "output": val,
                "expected": tc["expected_output"],
                "execution_time": time_ms,
                "error": None
            })
        elif err_match:
            results.append({
                "test_case_id": tc.get("id"),
                "passed": False,
                "error": err_match.group(1).strip()
            })
        else:
            results.append({"error": "No output for test case", "test_case_id": tc.get("id")})
            
    return results

def solve_cpp(code: str, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # 1. Write solution.cpp
    # Include printing helpers
    helpers = """
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <unordered_map>
#include <map>
#include <set>
#include <unordered_set>
#include <stack>
#include <queue>
#include <cmath>
using namespace std;

template<typename T>
void __print_val(const T& val) { cout << val; }

void __print_val(const bool& val) { cout << (val ? "true" : "false"); }
void __print_val(const string& val) { cout << val; }

template<typename T>
void __print_val(const vector<T>& val) {
    cout << "[";
    for(size_t i=0; i<val.size(); ++i) {
        __print_val(val[i]);
        if(i < val.size()-1) cout << ",";
    }
    cout << "]";
}
"""
    full_code = helpers + "\n" + code
    
    method_name, param_names, ret_type = get_method_info(code, "cpp")
    
    main_code = [full_code, "int main() {", "    Solution sol;"]
    
    for idx, tc in enumerate(test_cases):
        try:
            parse_env = {"dict": dict, "list": list, "str": str, "int": int, "bool": bool}
            kwargs = eval(f"dict({tc['input']})", {"__builtins__": None}, parse_env)
        except:
            kwargs = {}

        main_code.append(f"    try {{")
        args_vars = []
        for i, name in enumerate(param_names):
            val = kwargs.get(name)
            cpp_type, literal = parse_input_to_cpp(val)
            var_name = f"a{i}"
            main_code.append(f"        {cpp_type} {var_name} = {literal};")
            args_vars.append(var_name)
            
        if ret_type == "void":
            main_code.append(f"        sol.{method_name}({', '.join(args_vars)});")
            main_code.append(f"        cout << \"__RESULT_{idx}__:void\" << endl;")
        else:
            main_code.append(f"        auto res = sol.{method_name}({', '.join(args_vars)});")
            main_code.append(f"        cout << \"__RESULT_{idx}__:\";")
            main_code.append(f"        __print_val(res);")
            main_code.append(f"        cout << endl;")
        
        main_code.append(f"    }} catch (...) {{")
        main_code.append(f"        cout << \"__ERROR_{idx}__: Exception\" << endl;")
        main_code.append(f"    }}")
        
    main_code.append("    return 0;\n}")
    
    with open("main.cpp", "w") as f:
        f.write("\n".join(main_code))
        
    comp = run_command(["g++", "-O3", "main.cpp", "-o", "solution"])
    if comp.returncode != 0:
        return [{"error": "Compile Error", "details": comp.stderr}]
        
    run = run_command(["./solution"])
    output = run.stdout + run.stderr
    
    results = []
    for idx, tc in enumerate(test_cases):
        res_match = re.search(fr"__RESULT_{idx}__:(.*)", output)
        err_match = re.search(fr"__ERROR_{idx}__:(.*)", output)
        
        if res_match:
            val = res_match.group(1).strip()
            # Normalize for comparison
            normalized_output = val.replace(" ", "")
            expected = str(tc['expected_output']).strip().replace(" ", "").replace("True", "true").replace("False", "false")
            passed = normalized_output == expected
            
            results.append({
                "test_case_id": tc.get("id"),
                "passed": passed,
                "output": val,
                "expected": tc["expected_output"],
                "execution_time": 0,
                "error": None
            })
        elif err_match:
            results.append({
                "test_case_id": tc.get("id"),
                "passed": False, 
                "output": None,
                "expected": tc["expected_output"],
                "error": err_match.group(1).strip()
            })
        else:
            results.append({"error": "No output for test case", "test_case_id": tc.get("id")})
            
    return results

if __name__ == "__main__":
    try:
        input_data = sys.stdin.read()
        payload = json.loads(input_data)
        
        code = payload.get("code", "")
        test_cases = payload.get("test_cases", [])
        lang = os.environ.get("LANGUAGE", "python")
        
        if lang == "java":
            print(json.dumps(solve_java(code, test_cases)))
        elif lang == "cpp":
            print(json.dumps(solve_cpp(code, test_cases)))
        else:
            print(json.dumps([{"error": f"Language {lang} not supported by compiled runner"}]))
            
    except Exception as e:
        print(json.dumps([{"error": f"Internal Runner Error: {str(e)}"}]))

