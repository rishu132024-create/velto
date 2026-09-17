from velto_parser import (
    Program,
    NumberNode,
    StringNode,
    BooleanNode,
    NoneNode,
    IdentifierNode,
    ListNode,
    IndexNode,
    BinaryOpNode,
    AssignmentNode,
    IndexAssignmentNode,
    SayNode,
    ExpressionStatementNode,
    IfNode,
    WhileNode,
    ForNode,
    BreakNode,
    ContinueNode,
    FunctionDefNode,
    CallNode,
    ReturnNode
)

from velto_stdlib import BUILTINS, StdLibError


class ASTInterpreterError(Exception):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        super().__init__(message)


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class Function:
    def __init__(self, name, parameters, body, closure):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.closure = closure


class ASTInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.loop_limit = 10000

    def error(self, message, node=None):
        line = None

        if node is not None:
            line = getattr(node, "line", None)

        raise ASTInterpreterError(message, line)

    def evaluate(self, node):
        if isinstance(node, NumberNode):
            return node.value

        if isinstance(node, StringNode):
            return node.value

        if isinstance(node, BooleanNode):
            return node.value

        if isinstance(node, NoneNode):
            return None

        if isinstance(node, IdentifierNode):
            if node.name not in self.variables:
                self.error(
                    f"Variable not found: {node.name}",
                    node
                )

            return self.variables[node.name]

        if isinstance(node, ListNode):
            return [
                self.evaluate(element)
                for element in node.elements
            ]

        if isinstance(node, IndexNode):
            value = self.evaluate(node.value)
            index = self.evaluate(node.index)

            try:
                return value[index]
            except (IndexError, TypeError, KeyError):
                self.error(
                    f"Invalid index: {index}",
                    node
                )

        if isinstance(node, BinaryOpNode):
            return self.evaluate_binary(node)

        if isinstance(node, CallNode):
            return self.call_function(node)

        self.error(
            f"Unknown expression node: {type(node).__name__}",
            node
        )

    def evaluate_binary(self, node):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        operator = node.operator

        try:
            if operator == "+":
                return left + right

            if operator == "-":
                return left - right

            if operator == "*":
                return left * right

            if operator == "/":
                return left / right

            if operator == "%":
                return left % right

            if operator == "==":
                return left == right

            if operator == "!=":
                return left != right

            if operator == "<":
                return left < right

            if operator == ">":
                return left > right

            if operator == "<=":
                return left <= right

            if operator == ">=":
                return left >= right

        except (TypeError, ZeroDivisionError) as error:
            self.error(
                str(error),
                node
            )

        self.error(
            f"Unknown operator: {operator}",
            node
        )

    def execute(self, node):
        if isinstance(node, Program):
            for statement in node.statements:
                self.execute(statement)

            return

        if isinstance(node, AssignmentNode):
            value = self.evaluate(node.value)
            self.variables[node.name] = value
            return

        if isinstance(node, IndexAssignmentNode):
            target = self.evaluate(node.target)
            index = self.evaluate(node.index)
            value = self.evaluate(node.value)

            if not isinstance(target, list):
                self.error(
                    "Index assignment requires a list",
                    node
                )

            try:
                target[index] = value
            except (IndexError, TypeError):
                self.error(
                    f"Invalid index: {index}",
                    node
                )

            return

        if isinstance(node, SayNode):
            value = self.evaluate(node.value)
            print(value)
            return

        if isinstance(node, ExpressionStatementNode):
            self.evaluate(node.expression)
            return

        if isinstance(node, IfNode):
            condition = self.evaluate(node.condition)

            if condition:
                self.execute_block(node.body)
            elif node.else_body is not None:
                self.execute_block(node.else_body)

            return

        if isinstance(node, WhileNode):
            count = 0

            while self.evaluate(node.condition):
                count += 1

                if count > self.loop_limit:
                    self.error(
                        "Possible infinite loop",
                        node
                    )

                try:
                    self.execute_block(node.body)

                except ContinueSignal:
                    continue

                except BreakSignal:
                    break

            return

        if isinstance(node, ForNode):
            iterable = self.evaluate(node.iterable)

            try:
                values = list(iterable)
            except TypeError:
                self.error(
                    "Object is not iterable",
                    node
                )

            for value in values:
                self.variables[node.variable] = value

                try:
                    self.execute_block(node.body)

                except ContinueSignal:
                    continue

                except BreakSignal:
                    break

            return

        if isinstance(node, BreakNode):
            raise BreakSignal()

        if isinstance(node, ContinueNode):
            raise ContinueSignal()

        if isinstance(node, FunctionDefNode):
            self.functions[node.name] = Function(
                node.name,
                node.parameters,
                node.body,
                dict(self.variables)
            )
            return

        if isinstance(node, ReturnNode):
            if node.value is None:
                raise ReturnSignal(None)

            value = self.evaluate(node.value)

            raise ReturnSignal(value)

        self.error(
            f"Unknown statement node: {type(node).__name__}",
            node
        )

    def execute_block(self, statements):
        for statement in statements:
            self.execute(statement)

    def call_function(self, node):
        arguments = [
            self.evaluate(argument)
            for argument in node.arguments
        ]

        if node.name in BUILTINS:
            try:
                return BUILTINS[node.name](arguments)

            except StdLibError as error:
                self.error(
                    str(error),
                    node
                )

        if node.name not in self.functions:
            self.error(
                f"Function not found: {node.name}",
                node
            )

        function = self.functions[node.name]

        if len(arguments) != len(function.parameters):
            self.error(
                f"Function {node.name} expects "
                f"{len(function.parameters)} arguments, "
                f"got {len(arguments)}",
                node
            )

        old_variables = self.variables

        local_variables = dict(function.closure)

        for parameter, argument in zip(
            function.parameters,
            arguments
        ):
            local_variables[parameter] = argument

        self.variables = local_variables

        try:
            self.execute_block(function.body)

        except ReturnSignal as signal:
            self.variables = old_variables
            return signal.value

        finally:
            self.variables = old_variables

        return None


def run_ast(tree):
    interpreter = ASTInterpreter()
    interpreter.execute(tree)
