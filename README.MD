# Shunting Yard para Expresiones Regulares

Este proyecto implementa el algoritmo Shunting Yard para convertir expresiones regulares de notación infija a postfija, construir árboles sintácticos y visualizarlos usando Graphviz.

## Descripción

El programa procesa expresiones regulares y realiza los siguientes pasos:
1. **Inserción de concatenaciones explícitas**: Añade operadores de concatenación (`.`) donde sea necesario
2. **Algoritmo Shunting Yard**: Convierte la expresión infija a notación postfija
3. **Construcción del árbol sintáctico**: Crea un árbol binario a partir de la expresión postfija
4. **Visualización**: Genera imágenes PNG del árbol usando Graphviz

## Características

- Soporta operadores de expresiones regulares: `*`, `+`, `?`, `|`, `.`
- Maneja caracteres escapados con `\`
- Respeta la precedencia de operadores
- Genera visualizaciones de árboles sintácticos
- Procesa múltiples expresiones desde un archivo

## Precedencia de Operadores

1. `*`, `+`, `?` (precedencia más alta: 3)
2. `.` (concatenación: 2)
3. `|` (alternación: 1)

## Instalación

Instala las dependencias necesarias:

```bash
pip install graphviz
```

También necesitas tener Graphviz instalado en tu sistema:
- **Windows**: Descarga desde [graphviz.org](https://graphviz.org/download/)
- **Linux**: `sudo apt-get install graphviz`
- **macOS**: `brew install graphviz`

## Uso

```bash
python shunting_yard_regex.py expresiones.txt
```

### Formato del archivo de entrada

Crea un archivo de texto con una expresión regular por línea:

```
a*b+
(a|b)*c
a(b|c)*d
```

Las líneas vacías y las que comienzan con `#` son ignoradas.

## Salida

Para cada expresión, el programa muestra:
- La expresión original (infija)
- Los tokens con concatenaciones explícitas
- La expresión en notación postfija
- Los pasos del algoritmo Shunting Yard
- Genera un archivo PNG con el árbol sintáctico (`tree_1.png`, `tree_2.png`, etc.)

### Ejemplo de salida

```
=== Línea 1 ===
Infijo: a*b+
Tokens (+ concat): a*.b+
Postfix: a*b+.
  operand a    | out=a               | stk=
  push op *    | out=a               | stk=*
  operand b    | out=a*              | stk=
  push op +    | out=a*b             | stk=+
  pop end .    | out=a*b+            | stk=
  pop end +    | out=a*b+.           | stk=
Árbol sintáctico guardado en: tree_1.png
```

## Estructura del Código

- `insert_concatenation()`: Añade operadores de concatenación explícitos
- `shunting_yard()`: Implementa el algoritmo principal
- `build_syntax_tree()`: Construye el árbol sintáctico desde la notación postfija
- `visualize_with_graphviz()`: Genera la visualización del árbol
- `procesar_archivo()`: Función principal que coordina el procesamiento

## Archivos Generados

- `tree_N.png`: Imágenes de los árboles sintácticos (N = número de línea)
- Los archivos temporales de Graphviz se limpian automáticamente

## Limitaciones

- Requiere que Graphviz esté instalado en el sistema
- No valida sintaxis de expresiones regulares (puede generar errores con expresiones malformadas)
- Los caracteres especiales deben ser escapados apropiadamente

