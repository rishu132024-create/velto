from velto_lexer import tokenize


class Program:
    def __init__(self, statements):
        self.statements = statements


class NumberNode:
    def __init__(self, value, line=None):
        self.value = value
        self.line = line


class StringNode:
    def __init__(self, value, line=None):
        self.value = value
        self.line = line


class BooleanNode:
    def __init__(self, value, line=None):
        self.value = value
        self.line = line


class NoneNode:
    def __init__(self, line=None):
        self.value = None
        self.line = line


class IdentifierNode:
    def __init__(self, name, line=None):
        self.name = name
        self.line = line


class ListNode:
    def __init__(self, elements, line=None):
        self.elements = elements
        self.line = line


class DictionaryNode:
    def __init__(self, pairs, line=None):
        self.pairs = pairs
        self.line = line


class IndexNode:
    def __init__(self, value, index, line=None):
        self.value = value
        self.index = index
        self.line = line


class BinaryOpNode:
    def __init__(self, left, operator, right, line=None):
        self.left = left
        self.operator = operator
        self.right = right
        self.line = line


class AssignmentNode:
    def __init__(self, name, value, line=None):
        self.name = name
        self.value = value
        self.line = line


class IndexAssignmentNode:
    def __init__(self, value, index, expression, line=None):
        self.value = value
        self.index = index
        self.expression = expression
        self.line = line


class SayNode:
    def __init__(self, expression, line=None):
        self.expression = expression
        self.line = line


class ExpressionStatementNode:
    def __init__(self, expression, line=None):
        self.expression = expression
        self.line = line


class IfNode:
    def __init__(self, condition, body, else_body=None, line=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body
        self.line = line


class WhileNode:
    def __init__(self, condition, body, line=None):
        self.condition = condition
        self.body = body
        self.line = line


class ForNode:
    def __init__(self, variable, iterable, body, line=None):
        self.variable = variable
        self.iterable = iterable
        self.body = body
        self.line = line


class BreakNode:
    def __init__(self, line=None):
        self.line = line


class ContinueNode:
    def __init__(self, line=None):
        self.line = line


class FunctionDefNode:
    def __init__(self, name, parameters, body, line=None):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.line = line


class CallNode:
    def __init__(self, name, arguments, line=None):
        self.name = name
        self.arguments = arguments
        self.line = line


class ReturnNode:
    def __init__(self, expression=None, line=None):
        self.expression = expression
        self.line = line


class ImportNode:
    def __init__(self, module, line=None):
        self.module = module
        self.line = line


class ParserError(Exception):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        super().__init__(message)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current(self):
        if self.position >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.position]

    def peek(self, offset=1):
        index = self.position + offset

        if index >= len(self.tokens):
            return self.tokens[-1]

        return self.tokens[index]

    def advance(self):
        token = self.current()

        if self.position < len(self.tokens) - 1:
            self.position += 1

        return token

    def match(self, token_type, value=None):
        token = self.current()

        if token.type != token_type:
            return False

        if value is not None and token.value != value:
            return False

        self.advance()
        return True

    def expect(self, token_type, value=None):
        token = self.current()

        if token.type != token_type:
            raise ParserError(
                f"Expected {token_type}, got {token.type}",
                token.line
            )

        if value is not None and token.value != value:
            raise ParserError(
                f"Expected '{value}', got '{token.value}'",
                token.line
            )

        self.advance()
        return token

    def skip_newlines(self):
        while self.current().type in {"NEWLINE"}:
            self.advance()

    def skip_dictionary_layout(self):
        while self.current().type in {"NEWLINE", "INDENT", "DEDENT"}:
            self.advance()

    def parse(self):
        statements = []

        self.skip_newlines()

        while self.current().type != "EOF":
            if self.current().type == "DEDENT":
                self.advance()
                continue

            statements.append(self.parse_statement())
            self.skip_newlines()

        return Program(statements)

    def parse_statement(self):
        token = self.current()
        line = token.line

        if token.type == "KEYWORD":
            if token.value == "say":
                return self.parse_say()

            if token.value == "if":
                return self.parse_if()

            if token.value == "while":
                return self.parse_while()

            if token.value == "for":
                return self.parse_for()

            if token.value == "function":
                return self.parse_function()

            if token.value == "return":
                return self.parse_return()

            if token.value == "break":
                self.advance()
                return BreakNode(line)

            if token.value == "continue":
                self.advance()
                return ContinueNode(line)

            if token.value == "import":
                return self.parse_import()

        if token.type == "IDENTIFIER":
            if (
                self.peek().type == "OPERATOR"
                and self.peek().value == "="
            ):
                return self.parse_assignment()

            expression = self.parse_expression()

            return ExpressionStatementNode(
                expression,
                getattr(expression, "line", line)
            )

        raise ParserError(
            "Invalid expression",
            line
        )

    def parse_import(self):
        token = self.expect("KEYWORD", "import")

        module = self.expect(
            "IDENTIFIER"
        ).value

        return ImportNode(
            module,
            token.line
        )

    def parse_say(self):
        token = self.expect(
            "KEYWORD",
            "say"
        )

        expression = self.parse_expression()

        return SayNode(
            expression,
            token.line
        )

    def parse_assignment(self):
        name_token = self.expect("IDENTIFIER")

        self.expect(
            "OPERATOR",
            "="
        )

        value = self.parse_expression()

        return AssignmentNode(
            name_token.value,
            value,
            name_token.line
        )

    def parse_if(self):
        token = self.expect(
            "KEYWORD",
            "if"
        )

        condition = self.parse_expression()

        self.expect(
            "DELIMITER",
            ":"
        )

        body = self.parse_block()

        else_body = None

        self.skip_newlines()

        if (
            self.current().type == "KEYWORD"
            and self.current().value == "else"
        ):
            self.advance()

            self.expect(
                "DELIMITER",
                ":"
            )

            else_body = self.parse_block()

        return IfNode(
            condition,
            body,
            else_body,
            token.line
        )

    def parse_while(self):
        token = self.expect(
            "KEYWORD",
            "while"
        )

        condition = self.parse_expression()

        self.expect(
            "DELIMITER",
            ":"
        )

        body = self.parse_block()

        return WhileNode(
            condition,
            body,
            token.line
        )

    def parse_for(self):
        token = self.expect(
            "KEYWORD",
            "for"
        )

        variable = self.expect(
            "IDENTIFIER"
        ).value

        self.expect(
            "KEYWORD",
            "in"
        )

        iterable = self.parse_expression()

        self.expect(
            "DELIMITER",
            ":"
        )

        body = self.parse_block()

        return ForNode(
            variable,
            iterable,
            body,
            token.line
        )

    def parse_function(self):
        token = self.expect(
            "KEYWORD",
            "function"
        )

        name = self.expect(
            "IDENTIFIER"
        ).value

        self.expect(
            "DELIMITER",
            "("
        )

        parameters = []

        if not self.match(
            "DELIMITER",
            ")"
        ):
            while True:
                parameters.append(
                    self.expect(
                        "IDENTIFIER"
                    ).value
                )

                if self.match(
                    "DELIMITER",
                    ")"
                ):
                    break

                self.expect(
                    "DELIMITER",
                    ","
                )

        self.expect(
            "DELIMITER",
            ":"
        )

        body = self.parse_block()

        return FunctionDefNode(
            name,
            parameters,
            body,
            token.line
        )

    def parse_return(self):
        token = self.expect(
            "KEYWORD",
            "return"
        )

        if self.current().type in {
            "NEWLINE",
            "DEDENT",
            "EOF"
        }:
            return ReturnNode(
                None,
                token.line
            )

        expression = self.parse_expression()

        return ReturnNode(
            expression,
            token.line
        )

    def parse_block(self):
        self.skip_newlines()

        if self.current().type == "INDENT":
            self.advance()
        else:
            raise ParserError(
                "Expected indented block",
                self.current().line
            )

        statements = []

        self.skip_newlines()

        while self.current().type not in {
            "DEDENT",
            "EOF"
        }:
            statements.append(
                self.parse_statement()
            )

            self.skip_newlines()

        if self.current().type == "DEDENT":
            self.advance()

        return statements

    def parse_expression(self):
        return self.parse_comparison()

    def parse_comparison(self):
        node = self.parse_term()

        while (
            self.current().type == "OPERATOR"
            and self.current().value in {
                "==",
                "!=",
                "<",
                ">",
                "<=",
                ">="
            }
        ):
            operator = self.advance()
            right = self.parse_term()

            node = BinaryOpNode(
                node,
                operator.value,
                right,
                operator.line
            )

        return node

    def parse_term(self):
        node = self.parse_factor()

        while (
            self.current().type == "OPERATOR"
            and self.current().value in {
                "+",
                "-"
            }
        ):
            operator = self.advance()
            right = self.parse_factor()

            node = BinaryOpNode(
                node,
                operator.value,
                right,
                operator.line
            )

        return node

    def parse_factor(self):
        node = self.parse_unary()

        while (
            self.current().type == "OPERATOR"
            and self.current().value in {
                "*",
                "/",
                "%"
            }
        ):
            operator = self.advance()
            right = self.parse_unary()

            node = BinaryOpNode(
                node,
                operator.value,
                right,
                operator.line
            )

        return node

    def parse_unary(self):
        if (
            self.current().type == "OPERATOR"
            and self.current().value == "-"
        ):
            token = self.advance()

            right = self.parse_unary()

            return BinaryOpNode(
                NumberNode(0, token.line),
                "-",
                right,
                token.line
            )

        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()

        while True:
            if self.match(
                "DELIMITER",
                "["
            ):
                index = self.parse_expression()

                self.expect(
                    "DELIMITER",
                    "]"
                )

                node = IndexNode(
                    node,
                    index,
                    getattr(node, "line", None)
                )

                continue

            if self.match(
                "DELIMITER",
                "."
            ):
                name = self.expect(
                    "IDENTIFIER"
                )

                node = IndexNode(
                    node,
                    StringNode(
                        name.value,
                        name.line
                    ),
                    name.line
                )

                continue

            if self.match(
                "DELIMITER",
                "("
            ):
                arguments = []

                if not self.match(
                    "DELIMITER",
                    ")"
                ):
                    while True:
                        arguments.append(
                            self.parse_expression()
                        )

                        if self.match(
                            "DELIMITER",
                            ")"
                        ):
                            break

                        self.expect(
                            "DELIMITER",
                            ","
                        )

                if isinstance(
                    node,
                    IdentifierNode
                ):
                    node = CallNode(
                        node.name,
                        arguments,
                        node.line
                    )
                else:
                    node = CallNode(
                        getattr(node, "name", ""),
                        arguments,
                        getattr(node, "line", None)
                    )

                continue

            break

        return node

    def parse_primary(self):
        token = self.current()

        if token.type == "NUMBER":
            self.advance()

            try:
                if "." in str(token.value):
                    value = float(token.value)
                else:
                    value = int(token.value)
            except ValueError:
                raise ParserError(
                    f"Invalid number: {token.value}",
                    token.line
                )

            return NumberNode(
                value,
                token.line
            )

        if token.type == "STRING":
            self.advance()

            return StringNode(
                token.value,
                token.line
            )

        if token.type == "IDENTIFIER":
            self.advance()

            return IdentifierNode(
                token.value,
                token.line
            )

        if token.type == "KEYWORD":
            if token.value == "true":
                self.advance()
                return BooleanNode(
                    True,
                    token.line
                )

            if token.value == "false":
                self.advance()
                return BooleanNode(
                    False,
                    token.line
                )

            if token.value == "none":
                self.advance()
                return NoneNode(
                    token.line
                )

        if (
            token.type == "DELIMITER"
            and token.value == "("
        ):
            self.advance()

            expression = self.parse_expression()

            self.expect(
                "DELIMITER",
                ")"
            )

            return expression

        if (
            token.type == "DELIMITER"
            and token.value == "["
        ):
            return self.parse_list()

        if (
            token.type == "DELIMITER"
            and token.value == "{"
        ):
            return self.parse_dictionary()

        raise ParserError(
            "Invalid expression",
            token.line
        )

    def parse_list(self):
        token = self.expect(
            "DELIMITER",
            "["
        )

        elements = []

        self.skip_newlines()

        if not (
            self.current().type == "DELIMITER"
            and self.current().value == "]"
        ):
            while True:
                self.skip_newlines()

                elements.append(
                    self.parse_expression()
                )

                self.skip_newlines()

                if self.match(
                    "DELIMITER",
                    "]"
                ):
                    break

                self.expect(
                    "DELIMITER",
                    ","
                )

                self.skip_newlines()

        else:
            self.advance()

        return ListNode(
            elements,
            token.line
        )

    def parse_dictionary(self):
        token = self.expect(
            "DELIMITER",
            "{"
        )

        pairs = []

        self.skip_dictionary_layout()

        if (
            self.current().type == "DELIMITER"
            and self.current().value == "}"
        ):
            self.advance()

            return DictionaryNode(
                pairs,
                token.line
            )

        while True:
            self.skip_dictionary_layout()

            key = self.parse_expression()

            self.skip_dictionary_layout()

            self.expect(
                "DELIMITER",
                ":"
            )

            self.skip_dictionary_layout()

            value = self.parse_expression()

            pairs.append(
                (key, value)
            )

            self.skip_dictionary_layout()

            if self.match(
                "DELIMITER",
                ","
            ):
                self.skip_dictionary_layout()

                if (
                    self.current().type == "DELIMITER"
                    and self.current().value == "}"
                ):
                    self.advance()
                    break

                continue

            self.skip_dictionary_layout()

            self.expect(
                "DELIMITER",
                "}"
            )

            break

        return DictionaryNode(
            pairs,
            token.line
        )



def parse(tokens):
    parser = Parser(tokens)
    return parser.parse()
