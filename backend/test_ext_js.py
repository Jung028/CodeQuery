import json
from pathlib import Path
from tree_sitter import Language, Parser

# Build the Tree-sitter language libraries
Language.build_library(
    "build/my-languages.so",
    [
        "tree-sitter-javascript",
    ]
)

# Initialize the Tree-sitter parser for JavaScript
JS_LANGUAGE = Language("build/my-languages.so", "javascript")

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

    def walk(node, depth=0):
        indent = "  " * depth  # Indentation for nested nodes

        # Log all node types to debug
        print(f"{indent}Node type: {node.type}")

        # Capture function declarations (including arrow functions)
        if node.type == "function_declaration":
            print(f"{indent}Found function declaration!")
            name_node = node.child_by_field_name("name")
            params_node = node.child_by_field_name("parameters")
            params = [source_code[child.start_byte:child.end_byte] for child in params_node.children if child.type == "identifier"] if params_node else []
            results["functions"].append({
                "name": source_code[name_node.start_byte:name_node.end_byte] if name_node else "Unnamed",
                "params": params
            })
        # Capture arrow function parameters and check the structure
        elif node.type == "arrow_function":
            print(f"{indent}Found arrow function!")
            
            # Check if there are any children and inspect the structure of the arrow function node
            if node.children:
                for child in node.children:
                    print(f"{indent}Child type: {child.type}")  # Debug the child node types

                params_node = node.child_by_field_name("formal_parameters")
                
                # If a formal_parameters node is found, extract identifiers
                if params_node:
                    print(f"{indent}Found parameters node: {params_node}")
                    params = [source_code[child.start_byte:child.end_byte] for child in params_node.children if child.type == "identifier"]
                else:
                    params = []  # Default to empty if no parameters node is found

                print(f"{indent}Extracted parameters: {params}")
            else:
                params = []  # No parameters if no children exist
            
            results["functions"].append({
                "name": "Arrow Function",
                "params": params
            })


        elif node.type == "variable_declaration":
            print(f"{indent}Found variable declaration!")
            for child in node.children:
                if child.type == "variable_declarator":
                    name_node = child.child_by_field_name("name")
                    if name_node:
                        results["variables"].append({
                            "name": source_code[name_node.start_byte:name_node.end_byte]
                        })
        elif node.type == "import_statement":
            results["imports"].append({
                "text": source_code[node.start_byte:node.end_byte]
            })

        # Recursively walk through child nodes
        for child in node.children:
            walk(child, depth + 1)

    walk(root_node)
    return results

# ---------------- MAIN DRIVER ----------------
def test_extract_for_file():
    test_file_path = "repositories/mindhive-assessment/frontend/src/McdMap.js"  # The specific file to extract
    result = extract_javascript_info(test_file_path)

    # Output the result in JSON format
    output_path = "output_json/McdMap.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(f"✅ Extraction complete for {test_file_path}")
    print(f"Output saved to {output_path}")

if __name__ == "__main__":
    test_extract_for_file()
