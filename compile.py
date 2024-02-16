import py_compile
import sys

def check_syntax(script_name):
    try:
        py_compile.compile(script_name)
        print("Syntax is correct.")
    except py_compile.PyCompileError as e:
        print("Syntax error:", e)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compile.py <script_name>")
    else:
        script_name = sys.argv[1]
        check_syntax(script_name)
