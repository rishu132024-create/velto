from velto_lexer import tokenize
from velto_parser import parse
from velto_ast import run_ast

source = """a = 10
b = 20

say a < b
say a == b
say a != b
say b >= a
"""

tokens = tokenize(source)
tree = parse(tokens)

run_ast(tree)
