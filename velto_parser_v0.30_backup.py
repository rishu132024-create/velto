from velto_lexer import tokenize


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
    def __init__(
        self,
        condition,
        body,
        else_body=None,
        line=None
    ):
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
    def __init__(
        self,
        variable,
        iterable,
        body,
        line=None
    ):
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
    def __init__(
        self,
        name,
        parameters,
        body,
        line=None
    ):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.line = line


class CallNode:
    def __init__(
        self,
        name,
        arguments,
        line=None
    ):
        self.name = name
        self.arguments = arguments
        self.line = line


class ReturnNode:
    def __init__(self, value=None, line=None):
        self.value = value
        self.line = line


class ImportNode:
    def __init__(self, name, line=None):
        self.name = name
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

        if self.position < len(self.tokens) - 1:
            self.position += 1

        return token

    def match(self, token_type, value=None):
        token = self.current()

        if token.type != token_type:
            return False

        if value is not None and token.value != value:
            return False

        self.position += 1
        return True

    def expect(self, token_type, value=None):
        token = self.current()

        if token.type != token_type:
            raise ParserError(
                f"Expected {token_type}, got {token.type}",
                getattr(token, "line", None)
            )

        if value is not None and token.value != value:
            raise ParserError(
                f"Expected '{value}', got '{token.value}'",
                getattr(token, "line", None)
            )

        self.position += 1
        return token

    def skip_newlines(self):
        while self.current().type == "NEWLINE":
            self.advance()

    def parse(self):
        statements = []

        self.skip_newlines()

        while self.current().type != "EOF":
            statements.append(
                self.parse_statement()
            )

            self.skip_newlines()

        line = (
            statements[0].line
            if statements
            else None
        )

        return Program(
            statements,
            line
        )

    def parse_statement(self):
        token = self.current()
        value = token.value
        line = getattr(token, "line", None)

        if token.type == "KEYWORD":
            if value == "say":
                return self.parse_say()

            if value == "if":
                return self.parse_if()

            if value == "while":
                return self.parse_while()

            if value == "for":
                return self.parse_for()

            if value == "break":
                self.advance()
                return BreakNode(line)

            if value == "continue":
                self.advance()
                return ContinueNode(line)

            if value == "function":
                return self.parse_function()

            if value == "return":
                return self.parse_return()

            if value == "import":
                return self.parse_import()

        if token.type == "IDENTIFIER":
            if (
                self.peek().type == "OPERATOR"
                and self.peek().value == "="
            ):
                return self.parse_assignment()

            if (
                self.peek().type == "DELIMITER"
                and self.peek().value == "["
            ):
                return self.parse_possible_index_assignment()

            expression = self.parse_expression()

            return ExpressionStatementNode(
                expression,
                expression.line
            )

        raise ParserError(
            f"Invalid statement: {value}",
            line
        )

    def parse_import(self):
        token = self.expect(
            "KEYWORD",
            "import"
        )

        module = self.expect(
            "IDENTIFIER"
        )

        return ImportNode(
            module.value,
            token.line
        )

    def parse_say(self):
        token = self.expect(
            "KEYWORD",
            "say"
        )

        value = self.parse_expression()

        return SayNode(
            value,
            token.line
        )

    def parse_assignment(self):
        name_token = self.expect(
            "IDENTIFIER"
        )

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

    def parse_possible_index_assignment(self):
        target = self.parse_postfix()

        if not isinstance(
            target,
            IndexNode
        ):
            raise ParserError(
                "Invalid assignment target",
                getattr(target, "line", None)
            )

        self.expect(
            "OPERATOR",
            "="
        )

        value = self.parse_expression()

        return IndexAssignmentNode(
            target.value,
            target.index,
            value,
            target.line
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
        )

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
            variable.value,
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
        )

        self.expect(
            "DELIMITER",
            "("
        )

        parameters = []

        if not (
            self.current().type == "DELIMITER"
            and self.current().value == ")"
        ):
            while True:
                parameter = self.expect(
                    "IDENTIFIER"
                )

                parameters.append(
                    parameter.value
                )

                if not self.match(
                    "DELIMITER",
                    ","
                ):
                    break

        self.expect(
            "DELIMITER",
            ")"
        )

        self.expect(
            "DELIMITER",
            ":"
        )

        body = self.parse_block()

        return FunctionDefNode(
            name.value,
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

        value = self.parse_expression()

        return ReturnNode(
            value,
            token.line
        )

    def parse_block(self):
        self.skip_newlines()

        self.expect(
            "INDENT"
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

        self.expect(
            "DEDENT"
        )

        return statements

    def parse_expression(self):
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_term()

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

            left = BinaryOpNode(
                left,
                operator.value,
                right,
                operator.line
            )

        return left

    def parse_term(self):
        left = self.parse_factor()

        while (
            self.current().type == "OPERATOR"
            and self.current().value in {
                "+",
                "-"
            }
        ):
            operator = self.advance()

            right = self.parse_factor()

            left = BinaryOpNode(
                left,
                operator.value,
                right,
                operator.line
            )

        return left

    def parse_factor(self):
        left = self.parse_unary()

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

            left = BinaryOpNode(
                left,
                operator.value,
                right,
                operator.line
            )

        return left

    def parse_unary(self):
        if (
            self.current().type == "OPERATOR"
            and self.current().value == "-"
        ):
            token = self.advance()

            value = self.parse_unary()

            return BinaryOpNode(
                NumberNode(
                    0,
                    token.line
                ),
                "-",
                value,
                token.line
            )

        return self.parse_postfix()

    def parse_postfix(self):
        expression = self.parse_primary()

        while True:
            if (
                self.current().type == "DELIMITER"
                and self.current().value == "["
            ):
                token = self.advance()

                index = self.parse_expression()

                self.expect(
                    "DELIMITER",
                    "]"
                )

                expression = IndexNode(
                    expression,
                    index,
                    token.line
                )

                continue

            if (
                self.current().type == "DELIMITER"
                and self.current().value == "("
            ):
                token = self.advance()

                arguments = []

                if not (
                    self.current().type == "DELIMITER"
                    and self.current().value == ")"
                ):
                    while True:
                        arguments.append(
                            self.parse_expression()
                        )

                        if not self.match(
                            "DELIMITER",
                            ","
                        ):
                            break

                self.expect(
                    "DELIMITER",
                    ")"
                )

                if not isinstance(
                    expression,
                    IdentifierNode
                ):
                    raise ParserError(
                        "Only named functions can be called",
                        token.line
                    )

                expression = CallNode(
                    expression.name,
                    arguments,
                    token.line
                )

                continue

            if (
                self.current().type == "DELIMITER"
                and self.current().value == "."
            ):
                token = self.advance()

                member = self.expect(
                    "IDENTIFIER"
                )

                if not isinstance(
                    expression,
                    IdentifierNode
                ):
                    raise ParserError(
                        "Invalid module reference",
                        token.line
                    )

                expression = IdentifierNode(
                    f"{expression.name}.{member.value}",
                    token.line
                )

                continue

            break

        return expression

    def parse_primary(self):
        token = self.current()
        line = getattr(
            token,
            "line",
            None
        )

        if token.type == "NUMBER":
            self.advance()

            return NumberNode(
                token.value,
                line
            )

        if token.type == "STRING":
            self.advance()

            return StringNode(
                token.value,
                line
            )

        if token.type == "IDENTIFIER":
            self.advance()

            return IdentifierNode(
                token.value,
                line
            )

        if token.type == "KEYWORD":
            if token.value == "true":
                self.advance()

                return BooleanNode(
                    True,
                    line
                )

            if token.value == "false":
                self.advance()

                return BooleanNode(
                    False,
                    line
                )

            if token.value == "none":
                self.advance()

                return NoneNode(
                    line
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
            f"Invalid expression: {token.value}",
            line
        )

    def parse_list(self):
        token = self.expect(
            "DELIMITER",
            "["
        )

        elements = []

        if not (
            self.current().type == "DELIMITER"
            and self.current().value == "]"
        ):
            while True:
                elements.append(
                    self.parse_expression()
                )

                if not self.match(
                    "DELIMITER",
                    ","
                ):
                    break

        self.expect(
            "DELIMITER",
            "]"
        )

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

        if not (
            self.current().type == "DELIMITER"
            and self.current().value == "}"
        ):
            while True:
                key = self.parse_expression()

                self.expect(
                    "DELIMITER",
                    ":"
                )

                value = self.parse_expression()

                pairs.append(
                    (key, value)
                )

                if not self.match(
                    "DELIMITER",
                    ","
                ):
                    break

        self.expect(
            "DELIMITER",
            "}"
        )

        return DictionaryNode(
            pairs,
            token.line
        )


def parse(tokens):
    parser = Parser(tokens)
    return parser.parse()
