from velto_lexer import tokenize
from velto_parser import parse

source = """a = 10
b = 20
c = a + b * 3

say c

if_value = c > 50
say if_value
"""

tokens = tokenize(source)
tree = parse(tokens)

print(tree)
