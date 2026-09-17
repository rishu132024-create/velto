class Program:
    def __init__(self, statements, line=None):
        self.statements = statements
        self.line = line


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
        self.line = line


class IdentifierNode:
    def __init__(self, name, line=None):
        self.name = name
        self.line = line


class ListNode:
    def __init__(self, elements, line=None):
        self.elements = elements
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
    def __init__(self, target, index, value, line=None):
        self.target = target
        self.index = index
        self.value = value
        self.line = line


class SayNode:
    def __init__(self, value, line=None):
        self.value = value
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
    def __init__(self, value=None, line=None):
        self.value = value
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
                f"Expected {expected}",
                token.line
            )

        return self.advance()

    def skip_newlines(self):
        while self.check("NEWLINE"):
            self.advance()

    def parse(self):
        statements = []

        self.skip_newlines()

        first_line = self.current().line

        while not self.check("EOF"):
            statements.append(
                self.parse_statement()
            )

            self.skip_newlines()

        return Program(
            statements,
            first_line
        )

    def parse_statement(self):
        line = self.current().line

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
            return BreakNode(line)

        if self.check("KEYWORD", "continue"):
            self.advance()
            return ContinueNode(line)

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

            if token.token_type == "DELIMITER":
                if token.value == "]":
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
        token = self.expect("KEYWORD", "say")

        value = self.parse_expression()

        return SayNode(
            value,
            token.line
        )

    def parse_assignment(self):
        token = self.expect("IDENTIFIER")

        self.expect("OPERATOR", "=")

        value = self.parse_expression()

        return AssignmentNode(
            token.value,
            value,
            token.line
        )

    def parse_possible_index_assignment(self):
        line = self.current().line

        target = self.parse_postfix()

        if not isinstance(target, IndexNode):
            raise ParserError(
                "Invalid assignment target",
                line
            )

        self.expect("OPERATOR", "=")

        value = self.parse_expression()

        return IndexAssignmentNode(
            target.value,
            target.index,
            value,
            line
        )

    def parse_if(self):
        token = self.expect("KEYWORD", "if")

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
            else_body,
            token.line
        )

    def parse_while(self):
        token = self.expect("KEYWORD", "while")

        condition = self.parse_expression()

        self.expect("DELIMITER", ":")
        self.expect("NEWLINE")
        self.expect("INDENT")

        body = self.parse_block()

        return WhileNode(
            condition,
            body,
            token.line
        )

    def parse_for(self):
        token = self.expect("KEYWORD", "for")

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
            body,
            token.line
        )

    def parse_function(self):
        token = self.expect("KEYWORD", "function")

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
            body,
            token.line
        )

    def parse_return(self):
        token = self.expect("KEYWORD", "return")

        if (
            self.check("NEWLINE")
            or self.check("DEDENT")
            or self.check("EOF")
        ):
            return ReturnNode(
                None,
                token.line
            )

        value = self.parse_expression()

        return ReturnNode(
            value,
            token.line
        )

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
        line = self.current().line

        expression = self.parse_expression()

        return ExpressionStatementNode(
            expression,
            line
        )

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
            token = self.advance()

            right = self.parse_term()

            left = BinaryOpNode(
                left,
                token.value,
                right,
                token.line
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
            token = self.advance()

            right = self.parse_factor()

            left = BinaryOpNode(
                left,
                token.value,
                right,
                token.line
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
            token = self.advance()

            right = self.parse_unary()

            left = BinaryOpNode(
                left,
                token.value,
                right,
                token.line
            )

        return left

    def parse_unary(self):
        if self.match("OPERATOR", "-"):
            token = self.tokens[self.position - 1]

            value = self.parse_unary()

            return BinaryOpNode(
                NumberNode(0, token.line),
                "-",
                value,
                token.line
            )

        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()

        while True:
            if self.match("DELIMITER", "["):
                index = self.parse_expression()

                closing = self.expect(
                    "DELIMITER",
                    "]"
                )

                node = IndexNode(
                    node,
                    index,
                    closing.line
                )

                continue

            if self.match("DELIMITER", "("):
                if not isinstance(node, IdentifierNode):
                    raise ParserError(
                        "Invalid function call",
                        getattr(node, "line", None)
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

                closing = self.expect(
                    "DELIMITER",
                    ")"
                )

                node = CallNode(
                    node.name,
                    arguments,
                    closing.line
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
                    float(token.value),
                    token.line
                )

            return NumberNode(
                int(token.value),
                token.line
            )

        if token.token_type == "STRING":
            self.advance()

            return StringNode(
                token.value,
                token.line
            )

        if token.token_type == "IDENTIFIER":
            self.advance()

            return IdentifierNode(
                token.value,
                token.line
            )

        if token.token_type == "KEYWORD":
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

        if self.match("DELIMITER", "("):
            expression = self.parse_expression()

            self.expect(
                "DELIMITER",
                ")"
            )

            return expression

        if self.match("DELIMITER", "["):
            line = self.tokens[self.position - 1].line

            elements = []

            if not self.check("DELIMITER", "]"):
                elements.append(
                    self.parse_expression()
                )

                while self.match("DELIMITER", ","):
                    elements.append(
                        self.parse_expression()
                    )

            self.expect(
                "DELIMITER",
                "]"
            )

            return ListNode(
                elements,
                line
            )

        raise ParserError(
            f"Unexpected token {token.value!r}",
            token.line
        )


def parse(tokens):
    parser = Parser(tokens)
    return parser.parse()
