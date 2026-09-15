from velto_lexer import tokenize
from velto_parser import parse
from velto_ast import run_ast

source = """x = 10 + 20 * 2
y = x - 5

say x
say y
say x + y
"""

tokens = tokenize(source)
tree = parse(tokens)

run_ast(tree)
