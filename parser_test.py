from velto_lexer import tokenize
from velto_parser import parse

source = """x = 10 + 20 * 2
say x
say "Hello Velto"
"""

tokens = tokenize(source)
tree = parse(tokens)

print(tree)
