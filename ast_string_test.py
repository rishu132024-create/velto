from velto_lexer import tokenize
from velto_parser import parse
from velto_ast import run_ast

source = """name = "Velto"
message = "Hello " + name

say name
say message
"""

tokens = tokenize(source)
tree = parse(tokens)

run_ast(tree)
