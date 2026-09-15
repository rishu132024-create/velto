
class ParserError(Exception):
    pass


class ASTNode:
    pass


class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements!r})"


class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Number({self.value!r})"


class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"String({self.value!r})"


class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name!r})"


class BooleanNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Boolean({self.value!r})"


class NoneNode(ASTNode):
    def __repr__(self):
        return "NoneValue()"


class ListNode(ASTNode):
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return f"List({self.elements!r})"


class IndexNode(ASTNode):
    def __init__(self, value, index):
        self.value = value
        self.index = index

    def __repr__(self):
        return f"Index({self.value!r}, {self.index!r})"


class BinaryOpNode(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left!r}, {self.operator!r}, {self.right!r})"


class AssignmentNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"Assignment({self.name!r}, {self.value!r})"


class IndexAssignmentNode(ASTNode):
    def __init__(self, target, index, value):
        self.target = target
        self.index = index
        self.value = value

    def __repr__(self):
        return f"IndexAssignment({self.target!r}, {self.index!r}, {self.value!r})"


class SayNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Say({self.value!r})"


class ExpressionStatementNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"ExpressionStatement({self.expression!r})"


class IfNode(ASTNode):
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body

    def __repr__(self):
        return f"If({self.condition!r}, {self.body!r}, {self.else_body!r})"


class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"While({self.condition!r}, {self.body!r})"


class ForNode(ASTNode):
    def __init__(self, variable, iterable, body):
        self.variable = variable
        self.iterable = iterable
        self.body = body

    def __repr__(self):
        return f"For({self.variable!r}, {self.iterable!r}, {self.body!r})"


class BreakNode(ASTNode):
    def __repr__(self):
        return "Break()"


class ContinueNode(ASTNode):
    def __repr__(self):
        return "Continue()"


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
        token = self.current()

        if not self.check(token_type, value):
            expected = token_type

            if value is not None:
                expected += f" {value!r}"

            raise ParserError(
                f"Expected {expected} at line {token.line}, "
                f"got {token.token_type} {token.value!r}"
            )

        return self.advance()

    def skip_newlines(self):
        while self.match("NEWLINE") is not None:
            pass

    def parse(self):
        statements = []

        self.skip_newlines()

        while not self.check("EOF"):
            if self.check("DEDENT"):
                self.advance()
                continue

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
                    return self.parse_possible_index_assignment()

        return self.parse_expression_statement()

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
        target = self.parse_primary()

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

        return IfNode(condition, body, else_body)

    def parse_while(self):
        self.expect("KEYWORD", "while")

        condition = self.parse_expression()

        self.expect("DELIMITER", ":")
        self.expect("NEWLINE")
        self.expect("INDENT")

        body = self.parse_block()

        return WhileNode(condition, body)

    def parse_for(self):
        self.expect("KEYWORD", "for")

        variable = self.expect("IDENTIFIER").value

        self.expect("KEYWORD", "in")

        iterable = self.parse_expression()

        self.expect("DELIMITER", ":")
        self.expect("NEWLINE")
        self.expect("INDENT")

        body = self.parse_block()

        return ForNode(variable, iterable, body)

    def parse_block(self):
        statements = []

        self.skip_newlines()

        while not self.check("DEDENT") and not self.check("EOF"):
            statements.append(self.parse_statement())
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

        while self.check("OPERATOR") and self.current().value in {
            "==",
            "!=",
            "<",
            ">",
            "<=",
            ">="
        }:
            operator = self.advance().value
            right = self.parse_term()
            left = BinaryOpNode(left, operator, right)

        return left

    def parse_term(self):
        left = self.parse_factor()

        while self.check("OPERATOR") and self.current().value in {
            "+",
            "-"
        }:
            operator = self.advance().value
            right = self.parse_factor()
            left = BinaryOpNode(left, operator, right)

        return left

    def parse_factor(self):
        left = self.parse_unary()

        while self.check("OPERATOR") and self.current().value in {
            "*",
            "/",
            "%"
        }:
            operator = self.advance().value
            right = self.parse_unary()
            left = BinaryOpNode(left, operator, right)

        return left

    def parse_unary(self):
        if self.check("OPERATOR", "-"):
            operator = self.advance().value
            value = self.parse_unary()

            return BinaryOpNode(
                NumberNode(0),
                operator,
                value
            )

        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()

        while self.match("DELIMITER", "[") is not None:
            index = self.parse_expression()
            self.expect("DELIMITER", "]")
            node = IndexNode(node, index)

        return node

    def parse_primary(self):
        token = self.current()

        if token.token_type == "NUMBER":
            self.advance()

            if "." in token.value:
                return NumberNode(float(token.value))

            return NumberNode(int(token.value))

        if token.token_type == "STRING":
            self.advance()
            return StringNode(token.value)

        if token.token_type == "IDENTIFIER":
            self.advance()
            return IdentifierNode(token.value)

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

        if self.match("DELIMITER", "["):
            elements = []

            if not self.check("DELIMITER", "]"):
                while True:
                    elements.append(self.parse_expression())

                    if self.match("DELIMITER", ",") is None:
                        break

            self.expect("DELIMITER", "]")

            return ListNode(elements)

        if self.match("DELIMITER", "("):
            expression = self.parse_expression()
            self.expect("DELIMITER", ")")
            return expression

        raise ParserError(
            f"Unexpected token {token.token_type} "
            f"{token.value!r} at line {token.line}"
        )


def parse(tokens):
    parser = Parser(tokens)
    return parser.parse()
