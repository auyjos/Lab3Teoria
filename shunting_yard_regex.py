#!/usr/bin/env python3
"""
Convierte expresiones regulares infijas a postfix, construye un árbol sintáctico
y lo renderiza con Graphviz.

Uso:
    python shunting_yard_tree.py expresiones.txt

Genera un PNG "tree_<número>.png" por cada línea procesada.
"""

import sys

from graphviz import Digraph


# ——— Paso 1: inserción de concatenaciones explícitas ———
def insert_concatenation(expr: str):
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i] == '\\' and i+1 < len(expr):
            tokens.append(expr[i:i+2])
            i += 2
        else:
            tokens.append(expr[i])
            i += 1

    result = []
    for j, tok in enumerate(tokens):
        if j > 0:
            prev = tokens[j-1]
            # si prev no es '|', '(', y tok no es operador ni ')', concatenar
            if prev not in ['|','('] and tok not in ['|',')','*','+','?']:
                result.append('.')
        result.append(tok)
    return result

# ——— Paso 2: Shunting-Yard ———
def precedence(op: str):
    if op in ('*','+','?'): return 3
    if op == '.':        return 2
    if op == '|':        return 1
    return 0

def shunting_yard(tokens):
    output = []
    stack  = []
    pasos  = []
    for token in tokens:
        # literals y escapes
        if token.startswith('\\') or (len(token)==1 and (token.isalnum() or token in ['_','[',']','{','}'])):
            output.append(token)
            pasos.append((f"operand {token}", output.copy(), stack.copy()))
        elif token == '(':
            stack.append(token)
            pasos.append(("push (", output.copy(), stack.copy()))
        elif token == ')':
            while stack and stack[-1] != '(':
                op = stack.pop()
                output.append(op)
                pasos.append(("pop for )", output.copy(), stack.copy()))
            if stack and stack[-1]=='(':
                stack.pop()
                pasos.append(("pop (", output.copy(), stack.copy()))
            else:
                pasos.append(("ignore unmatched )", output.copy(), stack.copy()))
        elif token in ['|','.','*','+','?']:
            while stack and precedence(stack[-1]) >= precedence(token):
                if stack[-1] == '(': break
                op = stack.pop()
                output.append(op)
                pasos.append((f"pop op {op}", output.copy(), stack.copy()))
            stack.append(token)
            pasos.append((f"push op {token}", output.copy(), stack.copy()))
        else:
            pasos.append((f"ignore {token}", output.copy(), stack.copy()))

    while stack:
        op = stack.pop()
        output.append(op)
        pasos.append((f"pop end {op}", output.copy(), stack.copy()))

    return output, pasos

# ——— Paso 3: construir árbol sintáctico ———
class RegexNode:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left  = left
        self.right = right

def build_syntax_tree(postfix_tokens):
    stack = []
    for tok in postfix_tokens:
        if tok in ('*','+','?'):
            child = stack.pop()
            stack.append(RegexNode(tok, left=child))
        elif tok in ('.','|'):
            right = stack.pop()
            left  = stack.pop()
            stack.append(RegexNode(tok, left=left, right=right))
        else:
            stack.append(RegexNode(tok))
    return stack.pop()

# ——— Paso 4: visualizar con Graphviz ———
def visualize_with_graphviz(root, filename='tree'):
    dot = Digraph(format='png')
    dot.attr(rankdir='BT')  # Bottom to Top (BT), puedes usar 'TB' para Top to Bottom
    count = 0
    def visit(node):
        nonlocal count
        nid = f"n{count}"
        count += 1
        dot.node(nid, label=node.value)
        if node.left:
            lid = visit(node.left)
            dot.edge(nid, lid)
        if node.right:
            rid = visit(node.right)
            dot.edge(nid, rid)
        return nid
    visit(root)
    dot.render(filename, cleanup=True)  # genera filename.png

# ——— Función principal ———
def procesar_archivo(path):
    with open(path, encoding='utf-8') as f:
        idx = 1
        for linea in f:
            expr = linea.strip()
            if not expr or expr.startswith('#'):
                continue

            print(f"\n=== Línea {idx} ===")
            print("Infijo:", expr)

            tokens = insert_concatenation(expr)
            print("Tokens (+ concat):", ''.join(tokens))

            postfix, pasos = shunting_yard(tokens)
            print("Postfix:", ''.join(postfix))

            # opcional: mostrar pasos
            for a,o,p in pasos:
                print(f"  {a:12} | out={''.join(o):15} | stk={''.join(p)}")

            # árbol
            root = build_syntax_tree(postfix)
            png_name = f"tree_{idx}"
            visualize_with_graphviz(root, filename=png_name)
            print(f"Árbol sintáctico guardado en: {png_name}.png")

            idx += 1

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python shunting_yard_tree.py <archivo_expresiones.txt>")
        sys.exit(1)
    procesar_archivo(sys.argv[1])

