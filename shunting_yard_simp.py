#!/usr/bin/env python3
"""
Convierte expresiones regulares infijas a postfix, construye un árbol sintáctico
y lo renderiza con Graphviz, primero expandiendo '+' y '?' de forma recursiva.

Uso:
    python shunting_yard_tree.py expresiones.txt

Genera un PNG "tree_<número>.png" por cada línea procesada.
"""

import sys

from graphviz import Digraph


# ——— Paso 0: expandir '+' y '?' recursivamente ———
def expand_plus_question(expr: str) -> str:
    """
    Recorre expr y convierte:
      X+ → XX*
      X? → (X|ε)
    donde X es:
      1) una secuencia escapada: \X
      2) un grupo completo: ( ... )
      3) un literal simple
    Para los grupos, se llama recursivamente sobre su contenido.
    """
    i, n = 0, len(expr)
    out = ""

    def is_escaped(pos):
        # True si el char en expr[pos] está precedido por un número impar de '\'
        cnt = 0
        k = pos - 1
        while k >= 0 and expr[k] == '\\':
            cnt += 1
            k -= 1
        return (cnt % 2) == 1

    while i < n:
        # 1) escape "\X"
        if expr[i] == '\\' and i+1 < n:
            token = expr[i:i+2]
            i += 2

        # 2) grupo "( ... )"
        elif expr[i] == '(' and not is_escaped(i):
            start = i
            depth = 1
            i += 1
            while i < n and depth > 0:
                if expr[i] == '(' and not is_escaped(i):
                    depth += 1
                elif expr[i] == ')' and not is_escaped(i):
                    depth -= 1
                i += 1
            # extraemos el contenido interno sin los paréntesis
            inner = expr[start+1:i-1]
            # expandimos recursivamente ese interior
            token = "(" + expand_plus_question(inner) + ")"

        # 3) literal
        else:
            token = expr[i]
            i += 1

        # ¿le sigue un '+' o un '?' (no escapado)?
        if i < n and not is_escaped(i) and expr[i] in ['+', '?']:
            op = expr[i]
            i += 1
            if op == '+':
                # X+ → XX*
                out += token + token + '*'
            else:  # op == '?'
                # X? → (X|ε)
                out += f"({token}|ε)"
        else:
            out += token

    return out

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
    output, stack, pasos = [], [], []
    for token in tokens:
        if token.startswith('\\') or (
           len(token)==1 and (token.isalnum() or token in ['_','[',']','{','}','ε'])
        ):
            output.append(token)
            pasos.append((f"operand {token}", output.copy(), stack.copy()))
        elif token == '(':
            stack.append(token)
            pasos.append(("push (", output.copy(), stack.copy()))
        elif token == ')':
            while stack and stack[-1] != '(':
                op = stack.pop(); output.append(op)
                pasos.append(("pop for )", output.copy(), stack.copy()))
            if stack and stack[-1] == '(':
                stack.pop()
                pasos.append(("pop (", output.copy(), stack.copy()))
            else:
                pasos.append(("ignore unmatched )", output.copy(), stack.copy()))
        elif token in ['|','.','*','+','?']:
            while stack and precedence(stack[-1]) >= precedence(token):
                if stack[-1] == '(':
                    break
                op = stack.pop(); output.append(op)
                pasos.append((f"pop op {op}", output.copy(), stack.copy()))
            stack.append(token)
            pasos.append((f"push op {token}", output.copy(), stack.copy()))
        else:
            pasos.append((f"ignore {token}", output.copy(), stack.copy()))

    while stack:
        op = stack.pop(); output.append(op)
        pasos.append((f"pop end {op}", output.copy(), stack.copy()))

    return output, pasos

# ——— Paso 3: construir árbol sintáctico ———
class RegexNode:
    def __init__(self, value, left=None, right=None):
        self.value, self.left, self.right = value, left, right

def build_syntax_tree(postfix_tokens):
    stack = []
    for tok in postfix_tokens:
        if tok in ('*','+','?'):
            child = stack.pop()
            stack.append(RegexNode(tok, left=child))
        elif tok in ('.','|'):
            right = stack.pop(); left = stack.pop()
            stack.append(RegexNode(tok, left=left, right=right))
        else:
            stack.append(RegexNode(tok))
    return stack.pop()

# ——— Paso 4: visualizar con Graphviz ———
def visualize_with_graphviz(root, filename='tree'):
    dot = Digraph(format='png')
    dot.attr(rankdir='BT')   # raíz arriba, hojas abajo (puedes omitir si es por defecto)
    count = 0

    def visit(node):
        nonlocal count
        nid = f"n{count}"
        count += 1
        dot.node(nid, label=node.value)
        # primero procesamos recursivamente los hijos…
        if node.left:
            lid = visit(node.left)
            # …y dibujamos la flecha desde el hijo hacia este nodo
            dot.edge(lid, nid)
        if node.right:
            rid = visit(node.right)
            dot.edge(rid, nid)
        return nid

    visit(root)
    dot.render(filename, cleanup=True)

# ——— Función principal ———
def procesar_archivo(path):
    with open(path, encoding='utf-8') as f:
        idx = 1
        for linea in f:
            expr = linea.strip()
            if not expr or expr.startswith('#'):
                continue

            # 0) Expandir '+' y '?'
            expr2 = expand_plus_question(expr)
            print(f"\n=== Línea {idx} ===")
            print("Infijo original   :", expr)
            print("Infijo expandido  :", expr2)

            # 1) Concatenación explícita
            tokens = insert_concatenation(expr2)
            print("Tokens (+ concat) :", ''.join(tokens))

            # 2) Postfix
            postfix, pasos = shunting_yard(tokens)
            print("Postfix           :", ''.join(postfix))

            # Pasos internos (opcional)
            for a,o,p in pasos:
                print(f"  {a:12} | out={''.join(o):15} | stk={''.join(p)}")

            # 3) Árbol
            root = build_syntax_tree(postfix)
            png = f"tree_simplified_{idx}"
            visualize_with_graphviz(root, filename=png)
            print(f"Árbol guardado en : {png}.png")

            idx += 1

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python shunting_yard_tree.py <archivo_expresiones.txt>")
        sys.exit(1)
    procesar_archivo(sys.argv[1])
