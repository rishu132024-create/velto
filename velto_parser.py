class Program:
    def __init__(self, statements):
        self.statements = statements


class NumberNode:
    def __init__(self, value):
        self.value = value


class StringNode:
    def __init__(self, value):
        self.value = value


class BooleanNode:
    def __init__(self, value):
        self.value = value


class NoneNode:
    pass


class IdentifierNode:
    def __init__(self, name):
        self.name = name


class ListNode:
    def __init__(self, elements):
        self.elements = elements


class IndexNode:
    def __init__(self, value, index):
        self.value = value
        self.index = index


class BinaryOpNode:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class AssignmentNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class IndexAssignmentNode:
    def __init__(self, target, index, value):
        self.target = target
        self.index = index
        self.value = value


class SayNode:
    def __init__(self, value):
        self.value = value


class ExpressionStatementNode:
    def __init__(self, expression):
        self.expression = expression


class IfNode:
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body


class WhileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class ForNode:
    def __init__(self, variable, iterable, body):
        self.variable = variable
        self.iterable = iterable
        self.body = body


class BreakNode:
    pass


class ContinueNode:
    pass


class FunctionDefNode:
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body


class CallNode:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class ReturnNode:
    def __init__(self, value=None):
        self.value = value


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current(self):
        if self.position >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.position]

    def peek(self, offset=1):
        position = self.position + offset

        if position >= len(self.tokens):
            return self.tokens[-1]

        return self.tokens[position]

    def advance(self):
        token = self.current()
        self.position += 1
        return token

    def check(self, token_type, value=None):
        token = self.current()

        if token.token_type != token_type:
            return False

        if value is not None and token.value != value:
            return False

        return True

    def match(self, token_type, value=None):
        if self.check(token_type, value):
            return self.advance()

        return None

    def expect(self, token_type, value=None):
        if not self.check(token_type, value):
            token = self.current()

            expected = token_type

            if value is not None:
                expected += f" {value!r}"

            raise ParserError(
                f"Expected {expected} at line {token.line}"
            )

        return self.advance()

    def skip_newlines(self):
        while self.check("NEWLINE"):
            self.advance()

    def parse(self):
        statements = []

        self.skip_newlines()

        while not self.check("EOF"):
            statements.append(self.parse_statement())
            self.skip_newlines()

        return Program(statements)

    def parse_statement(self):
        if self.check("KEYWORD", "say"):
            return self.parse_say()

        if self.check("KEYWORD", "if"):
            return self.parse_if()

        if self.check("KEYWORD", "while"):
            return self.parse_while()

        if self.check("KEYWORD", "for"):
            return self.parse_for()

        if self.check("KEYWORD", "function"):
            return self.parse_function()

        if self.check("KEYWORD", "return"):
            return self.parse_return()

        if self.check("KEYWORD", "break"):
            self.advance()
            return BreakNode()

        if self.check("KEYWORD", "continue"):
            self.advance()
            return ContinueNode()

        if self.check("IDENTIFIER"):
            if self.peek().token_type == "OPERATOR":
                if self.peek().value == "=":
                    return self.parse_assignment()

            if self.peek().token_type == "DELIMITER":
                if self.peek().value == "[":
                    if self.is_index_assignment():
                        return self.parse_possible_index_assignment()

        return self.parse_expression_statement()

    def is_index_assignment(self):
        position = self.position

        while position < len(self.tokens):
            token = self.tokens[position]

            if token.token_type == "DELIMITER" and token.value == "]":
                if position + 1 < len(self.tokens):
                    next_token = self.tokens[position + 1]

                    return (
                        next_token.token_type == "OPERATOR"
                        and next_token.value == "="
                    )

                return False

            if token.token_type == "NEWLINE":
                return False

            position += 1

        return False

    def parse_say(self):
        self.expect("KEYWORD", "say")

        value = self.parse_expression()

        return SayNode(value)

    def parse_assignment(self):
        name = self.expect("IDENTIFIER").value

        self.expect("OPERATOR", "=")

        value = self.parse_expression()

        return AssignmentNode(name, value)

    def parse_possible_index_assignment(self):
        target = self.parse_postfix()

        if not isinstance(target, IndexNode):
            raise ParserError(
                f"Invalid assignment target at line {self.current().line}"
            )

        self.expect("OPERATOR", "=")

        value = self.parse_expression()

        return IndexAssignmentNode(
            target.value,
            target.index,
            value
        )

    def parse_if(self):
        self.expect("KEYWORD", "if")

        condition = self.parse_expression()

        self.expect("DELIMITER", ":")
        self.expect("NEWLINE")
        self.expect("INDENT")

        body = self.parse_block()

        else_body = None

        if self.check("KEYWORD", "else"):
            self.advance()

            self.expect("DELIMITER", ":")
            self.expect("NEWLINE")
            self.expect("INDENT")

            else_body = self.parse_block()

        return IfNode(
            condition,
            body,
            else_body
        )

    def parse_while(self):
        self.expect("KEYWORD", "while")

        condition = self.parse_expression()

        self.expect("DELIMITER", ":")
        self.expect("NEWLINE")
        self.expect("INDENT")

        body = self.parse_block()

        return WhileNode(
            condition,
            body
        )

    def parse_for(self):
        self.expect("KEYWORD", "for")

        variable = self.expect("IDENTIFIER").value

        self.expect("KEYWORD", "in")

        iterable = self.parse_expression()

        self.expect("DELIMITER", ":")
        self.expect("NEWLINE")
        self.expect("INDENT")

        body = self.parse_block()

        return ForNode(
            variable,
            iterable,
            body
        )

    def parse_function(self):
        self.expect("KEYWORD", "function")

        name = self.expect("IDENTIFIER").value

        self.expect("DELIMITER", "(")

        parameters = []

        if not self.check("DELIMITER", ")"):
            parameters.append(
                self.expect("IDENTIFIER").value
            )

            while self.match("DELIMITER", ","):
                parameters.append(
                    self.expect("IDENTIFIER").value
                )

        self.expect("DELIMITER", ")")

        self.expect("DELIMITER", ":")
        self.expect("NEWLINE")
        self.expect("INDENT")

        body = self.parse_block()

        return FunctionDefNode(
            name,
            parameters,
            body
        )

    def parse_return(self):
        self.expect("KEYWORD", "return")

        if (
            self.check("NEWLINE")
            or self.check("DEDENT")
            or self.check("EOF")
        ):
            return ReturnNode()

        value = self.parse_expression()

        return ReturnNode(value)

    def parse_block(self):
        statements = []

        self.skip_newlines()

        while (
            not self.check("DEDENT")
            and not self.check("EOF")
        ):
            statements.append(
                self.parse_statement()
            )

            self.skip_newlines()

        if self.check("DEDENT"):
            self.advance()

        return statements

    def parse_expression_statement(self):
        expression = self.parse_expression()

        return ExpressionStatementNode(expression)

    def parse_expression(self):
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_term()

        while (
            self.check("OPERATOR")
            and self.current().value in {
                "==",
                "!=",
                "<",
                ">",
                "<=",
                ">="
            }
        ):
            operator = self.advance().value
            right = self.parse_term()

            left = BinaryOpNode(
                left,
                operator,
                right
            )

        return left

    def parse_term(self):
        left = self.parse_factor()

        while (
            self.check("OPERATOR")
            and self.current().value in {
                "+",
                "-"
            }
        ):
            operator = self.advance().value
            right = self.parse_factor()

            left = BinaryOpNode(
                left,
                operator,
                right
            )

        return left

    def parse_factor(self):
        left = self.parse_unary()

        while (
            self.check("OPERATOR")
            and self.current().value in {
                "*",
                "/",
                "%"
            }
        ):
            operator = self.advance().value
            right = self.parse_unary()

            left = BinaryOpNode(
                left,
                operator,
                right
            )

        return left

    def parse_unary(self):
        if self.match("OPERATOR", "-"):
            value = self.parse_unary()

            return BinaryOpNode(
                NumberNode(0),
                "-",
                value
            )

        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()

        while True:
            if self.match("DELIMITER", "["):
                index = self.parse_expression()

                self.expect("DELIMITER", "]")

                node = IndexNode(
                    node,
                    index
                )

                continue

            if self.match("DELIMITER", "("):
                if not isinstance(node, IdentifierNode):
                    raise ParserError(
                        f"Invalid function call at line {self.current().line}"
                    )

                arguments = []

                if not self.check("DELIMITER", ")"):
                    arguments.append(
                        self.parse_expression()
                    )

                    while self.match("DELIMITER", ","):
                        arguments.append(
                            self.parse_expression()
                        )

                self.expect("DELIMITER", ")")

                node = CallNode(
                    node.name,
                    arguments
                )

                continue

            break

        return node

    def parse_primary(self):
        token = self.current()

        if token.token_type == "NUMBER":
            self.advance()

            if "." in token.value:
                return NumberNode(
                    float(token.value)
                )

            return NumberNode(
                int(token.value)
            )

        if token.token_type == "STRING":
            self.advance()

            return StringNode(
                token.value
            )

        if token.token_type == "IDENTIFIER":
            self.advance()

            return IdentifierNode(
                token.value
            )

        if token.token_type == "KEYWORD":
            if token.value == "true":
                self.advance()
                return BooleanNode(True)

            if token.value == "false":
                self.advance()
                return BooleanNode(False)

            if token.value == "none":
                self.advance()
                return NoneNode()

        if self.match("DELIMITER", "("):
            expression = self.parse_expression()

            self.expect("DELIMITER", ")")

            return expression

        if self.match("DELIMITER", "["):
            elements = []

            if not self.check("DELIMITER", "]"):
                elements.append(
                    self.parse_expression()
                )

                while self.match("DELIMITER", ","):
                    elements.append(
                        self.parse_expression()
                    )

            self.expect("DELIMITER", "]")

            return ListNode(elements)

        raise ParserError(
            f"Unexpected token {token.value!r} at line {token.line}"
        )


def parse(tokens):
    parser = Parser(tokens)

    return parser.parse()
