class Token:
    def __init__(self, token_type, value, line):
        self.token_type = token_type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.token_type}, {self.value!r}, line={self.line})"


class LexerError(Exception):
    pass


class Lexer:
    KEYWORDS = {
        "say",
        "if",
        "else",
        "while",
        "for",
        "in",
        "function",
        "return",
        "import",
        "true",
        "false",
        "none"
    }

    TWO_CHAR_OPERATORS = {
        "==",
        "!=",
        "<=",
        ">="
    }

    ONE_CHAR_OPERATORS = {
        "+",
        "-",
        "*",
        "/",
        "%",
        "<",
        ">",
        "="
    }

    DELIMITERS = {
        "(",
        ")",
        "[",
        "]",
        ":",
        ","
    }

    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.tokens = []
        self.indent_stack = [0]

    def current_char(self):
        if self.position >= len(self.source):
            return None
        return self.source[self.position]

    def peek_char(self):
        if self.position + 1 >= len(self.source):
            return None
        return self.source[self.position + 1]

    def advance(self):
        self.position += 1

    def add_token(self, token_type, value):
        self.tokens.append(Token(token_type, value, self.line))

    def read_number(self):
        start = self.position
        dot_count = 0

        while self.current_char() is not None:
            char = self.current_char()

            if char.isdigit():
                self.advance()
                continue

            if char == ".":
                dot_count += 1

                if dot_count > 1:
                    break

                self.advance()
                continue

            break

        value = self.source[start:self.position]

        if value == ".":
            raise LexerError(
                f"Invalid number at line {self.line}"
            )

        self.add_token("NUMBER", value)

    def read_identifier(self):
        start = self.position

        while self.current_char() is not None:
            char = self.current_char()

            if char.isalnum() or char == "_":
                self.advance()
            else:
                break

        value = self.source[start:self.position]

        if value in self.KEYWORDS:
            self.add_token("KEYWORD", value)
        else:
            self.add_token("IDENTIFIER", value)

    def read_string(self):
        quote = self.current_char()
        self.advance()

        value = ""

        while self.current_char() is not None:
            char = self.current_char()

            if char == quote:
                self.advance()
                self.add_token("STRING", value)
                return

            if char == "\\":
                self.advance()

                next_char = self.current_char()

                if next_char is None:
                    break

                escapes = {
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    "\\": "\\",
                    '"': '"',
                    "'": "'"
                }

                value += escapes.get(next_char, next_char)
                self.advance()
                continue

            if char == "\n":
                raise LexerError(
                    f"Unterminated string at line {self.line}"
                )

            value += char
            self.advance()

        raise LexerError(
            f"Unterminated string at line {self.line}"
        )

    def handle_indentation(self):
        spaces = 0

        while self.current_char() == " ":
            spaces += 1
            self.advance()

        if self.current_char() == "\n" or self.current_char() is None:
            return

        if self.current_char() == "\t":
            raise LexerError(
                f"Tabs are not supported at line {self.line}"
            )

        current_indent = self.indent_stack[-1]

        if spaces > current_indent:
            self.indent_stack.append(spaces)
            self.add_token("INDENT", spaces)

        elif spaces < current_indent:
            while spaces < self.indent_stack[-1]:
                self.indent_stack.pop()
                self.add_token("DEDENT", spaces)

            if spaces != self.indent_stack[-1]:
                raise LexerError(
                    f"Invalid indentation at line {self.line}"
                )

    def tokenize(self):
        at_line_start = True

        while self.current_char() is not None:
            char = self.current_char()

            if at_line_start:
                self.handle_indentation()
                at_line_start = False

                char = self.current_char()

                if char is None:
                    break

                if char == "\n":
                    self.advance()
                    self.add_token("NEWLINE", "\n")
                    self.line += 1
                    at_line_start = True
                    continue

            if char in " \r":
                self.advance()
                continue

            if char == "\n":
                self.advance()
                self.add_token("NEWLINE", "\n")
                self.line += 1
                at_line_start = True
                continue

            if char in "\"'":
                self.read_string()
                continue

            if char.isdigit():
                self.read_number()
                continue

            if char.isalpha() or char == "_":
                self.read_identifier()
                continue

            two_char = char + (self.peek_char() or "")

            if two_char in self.TWO_CHAR_OPERATORS:
                self.add_token("OPERATOR", two_char)
                self.advance()
                self.advance()
                continue

            if char in self.ONE_CHAR_OPERATORS:
                self.add_token("OPERATOR", char)
                self.advance()
                continue

            if char in self.DELIMITERS:
                self.add_token("DELIMITER", char)
                self.advance()
                continue

            raise LexerError(
                f"Unexpected character {char!r} at line {self.line}"
            )

        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.add_token("DEDENT", 0)

        self.add_token("EOF", None)

        return self.tokens


def tokenize(source):
    lexer = Lexer(source)
    return lexer.tokenize()
