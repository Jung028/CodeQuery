import os
import json
import ast
from pathlib import Path
from tree_sitter import Language, Parser

# Build the Tree-sitter language library for JavaScript
Language.build_library(
    "build/my-languages.so",
    [
        "tree-sitter-javascript"
    ]
)
JS_LANGUAGE = Language("build/my-languages.so", "javascript")

# ---------------- PYTHON PARSING ----------------
def extract_python_info(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=file_path)
        except SyntaxError:
            return {"error": "SyntaxError in file", "file": file_path}

    results = {
        "file": file_path,
        "language": "python",
        "functions": [],
        "classes": [],
        "imports": [],
        "variables": [],
        "comments": []
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            results["functions"].append({
                "name": node.name,
                "args": [arg.arg for arg in node.args.args],
                "docstring": ast.get_docstring(node),
                "returns": ast.unparse(node.returns) if node.returns else None
            })
        elif isinstance(node, ast.ClassDef):
            results["classes"].append({
                "name": node.name,
                "docstring": ast.get_docstring(node),
                "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            })
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            results["imports"].append({
                "module": getattr(node, "module", ""),
                "names": [n.name for n in node.names]
            })
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    results["variables"].append({
                        "name": target.id,
                        "value": ast.unparse(node.value)
                    })

    return results

# ---------------- JAVASCRIPT PARSING ----------------
def extract_javascript_info(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()

    parser = Parser()
    parser.set_language(JS_LANGUAGE)
    tree = parser.parse(bytes(source_code, "utf8"))

    root_node = tree.root_node
    results = {
        "file": file_path,
        "language": "javascript",
        "functions": [],
        "variables": [],
        "imports": []
    }

    # Debugging: Print the root node type and its children
    print(f"Root Node Type: {root_node.type}")
    print(f"Root Node Start Byte: {root_node.start_byte}, End Byte: {root_node.end_byte}")
    
    def walk(node, depth=0):
        indent = "  " * depth  # Indentation for nested nodes
        print(f"{indent}Visiting Node: {node.type} (start_byte: {node.start_byte}, end_byte: {node.end_byte})")

        # Detailed debug output for each type of node
        if node.type == "function_declaration":
            print(f"{indent}  Found function declaration!")
            name_node = node.child_by_field_name("name")
            params_node = node.child_by_field_name("parameters")
            if name_node:
                print(f"{indent}    Function Name: {source_code[name_node.start_byte:name_node.end_byte]}")
            if params_node:
                params = [source_code[child.start_byte:child.end_byte] for child in params_node.children if child.type == "identifier"]
                print(f"{indent}    Function Params: {params}")
            results["functions"].append({
                "name": source_code[name_node.start_byte:name_node.end_byte] if name_node else "Unnamed",
                "params": params
            })
        elif node.type == "variable_declaration":
            print(f"{indent}  Found variable declaration!")
            for child in node.children:
                if child.type == "variable_declarator":
                    name_node = child.child_by_field_name("name")
                    if name_node:
                        print(f"{indent}    Variable Name: {source_code[name_node.start_byte:name_node.end_byte]}")
                    results["variables"].append({
                        "name": source_code[name_node.start_byte:name_node.end_byte] if name_node else "Unnamed"
                    })
        elif node.type == "import_statement":
            print(f"{indent}  Found import statement!")
            results["imports"].append({
                "text": source_code[node.start_byte:node.end_byte]
            })

        # Recursively walk through child nodes
        for child in node.children:
            walk(child, depth + 1)

    walk(root_node)
    return results

# ---------------- MAIN DRIVER ----------------
def get_code_files(directory, extensions=(".py", ".js")):
    code_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extensions):
                code_files.append(os.path.join(root, file))
    return code_files

def main():
    source_dir = "repositories/mindhive-assessment"
    output_dir = "output_json"
    os.makedirs(output_dir, exist_ok=True)

    code_files = get_code_files(source_dir)
    print(f"📂 Found {len(code_files)} files to process")

    for full_path in code_files:
        relative_path = os.path.relpath(full_path, source_dir)
        output_path = os.path.join(output_dir, relative_path) + ".json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if full_path.endswith(".py"):
            result = extract_python_info(full_path)
        elif full_path.endswith(".js"):
            result = extract_javascript_info(full_path)
        else:
            continue

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(f"✅ Saved JSON for {relative_path}")

    print("\n🎉 All done!")

if __name__ == "__main__":
    main()
