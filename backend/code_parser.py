import ast

def parse_python_file(file_path):
    """ Parse a Python file and return the AST tree """
    with open(file_path, 'r') as file:
        code = file.read()

    tree = ast.parse(code)
    return tree

def extract_code_info(tree):
    """ Extract functions, classes, variables, imports, and comments from the AST """
    code_info = {
        "functions": [],
        "classes": [],
        "variables": [],
        "imports": [],
        "comments": []
    }

    for node in ast.walk(tree):
        # Extract Functions
        if isinstance(node, ast.FunctionDef):
            function = {
                "name": node.name,
                "arguments": [arg.arg for arg in node.args.args],
                "return_type": None,  # AST does not directly provide return types, can be added with typing module
                "docstring": ast.get_docstring(node)
            }
            code_info["functions"].append(function)
        
        # Extract Classes
        elif isinstance(node, ast.ClassDef):
            class_info = {
                "name": node.name,
                "methods": [],
                "docstring": ast.get_docstring(node)
            }
            code_info["classes"].append(class_info)

        # Extract Variables
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    code_info["variables"].append({
                        "name": target.id,
                        "value": ast.dump(node.value)
                    })
        
        # Extract Imports
        elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            imports = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module]
            code_info["imports"].extend(imports)
        
        # Extract Comments
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
            code_info["comments"].append(node.value.s)

    return code_info
