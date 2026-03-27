import os
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from typing import List, Dict, Any

# Initialize Parser
PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def semantic_search(file_path: str, query_type: str = "summary") -> str:
    """
    Perform structural search using Tree-sitter.
    query_type: 'summary' (list all funcs/classes), 'find' (lookup name).
    """
    if not os.path.exists(file_path):
        return f"❌ File not found: {file_path}"
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        tree = parser.parse(bytes(content, "utf8"))
        root_node = tree.root_node
        
        results = []
        
        # Simple recursive visitor
        def traverse(node):
            if node.type == "function_definition":
                # Find name
                for child in node.children:
                    if child.type == "identifier":
                        results.append(f"𝑓 {content[child.start_byte:child.end_byte]} (line {node.start_point[0] + 1})")
                        break
            elif node.type == "class_definition":
                for child in node.children:
                    if child.type == "identifier":
                        results.append(f"🏛️ {content[child.start_byte:child.end_byte]} (line {node.start_point[0] + 1})")
                        break
            
            for child in node.children:
                traverse(child)
                
        traverse(root_node)
        
        if not results:
            return f"ℹ️  No formal definitions found in {file_path}."
            
        header = f"🔍 Structural Map: {file_path}\n"
        return header + "\n".join(results)
        
    except Exception as e:
        return f"❌ Semantic Error: {str(e)}"
