from velto_lexer import tokenize

source = """say "Hello Velto"

x = 10 + 20

if x > 20:
    say x
"""

tokens = tokenize(source)

for token in tokens:
    print(token)
