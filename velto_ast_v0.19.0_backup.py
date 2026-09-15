from velto_parser import (
    Program,
    NumberNode,
    StringNode,
    IdentifierNode,
    BooleanNode,
    NoneNode,
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


class ASTInterpreterError(Exception):
    pass


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class Function:
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body


class ASTInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.loop_limit = 10000

    def evaluate(self, node):
        if isinstance(node, NumberNode):
            return node.value

        if isinstance(node, StringNode):
            return node.value

        if isinstance(node, BooleanNode):
            return node.value

        if isinstance(node, NoneNode):
            return None

        if isinstance(node, ListNode):
            return [
                self.evaluate(element)
                for element in node.elements
            ]

        if isinstance(node, IdentifierNode):
            if node.name not in self.variables:
                raise ASTInterpreterError(
                    f"Variable not found: {node.name}"
                )

            return self.variables[node.name]

        if isinstance(node, IndexNode):
            value = self.evaluate(node.value)
            index = self.evaluate(node.index)

            try:
                return value[index]
            except (IndexError, TypeError, KeyError):
                raise ASTInterpreterError(
                    f"Invalid index: {index}"
                )

        if isinstance(node, BinaryOpNode):
            return self.evaluate_binary(node)

        if isinstance(node, CallNode):
            return self.call_function(node)

        raise ASTInterpreterError(
            f"Unknown expression node: {type(node).__name__}"
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
            raise ASTInterpreterError(
                str(error)
            )

        raise ASTInterpreterError(
            f"Unknown operator: {operator}"
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
                raise ASTInterpreterError(
                    "Index assignment requires a list"
                )

            try:
                target[index] = value
            except (IndexError, TypeError):
                raise ASTInterpreterError(
                    f"Invalid index: {index}"
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
            condition = self.evaluate(
                node.condition
            )

            if condition:
                self.execute_block(
                    node.body
                )
            elif node.else_body is not None:
                self.execute_block(
                    node.else_body
                )

            return

        if isinstance(node, WhileNode):
            count = 0

            while self.evaluate(node.condition):
                count += 1

                if count > self.loop_limit:
                    raise ASTInterpreterError(
                        "Possible infinite loop"
                    )

                try:
                    self.execute_block(
                        node.body
                    )
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break

            return

        if isinstance(node, ForNode):
            iterable = self.evaluate(
                node.iterable
            )

            try:
                values = list(iterable)
            except TypeError:
                raise ASTInterpreterError(
                    "Object is not iterable"
                )

            for value in values:
                self.variables[
                    node.variable
                ] = value

                try:
                    self.execute_block(
                        node.body
                    )
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
                node.body
            )

            return

        if isinstance(node, ReturnNode):
            if node.value is None:
                raise ReturnSignal(None)

            value = self.evaluate(
                node.value
            )

            raise ReturnSignal(value)

        raise ASTInterpreterError(
            f"Unknown statement node: {type(node).__name__}"
        )

    def execute_block(self, statements):
        for statement in statements:
            self.execute(statement)

    def call_function(self, node):
        if node.name not in self.functions:
            raise ASTInterpreterError(
                f"Function not found: {node.name}"
            )

        function = self.functions[node.name]

        if len(node.arguments) != len(
            function.parameters
        ):
            raise ASTInterpreterError(
                f"Function {node.name} expects "
                f"{len(function.parameters)} arguments, "
                f"got {len(node.arguments)}"
            )

        arguments = [
            self.evaluate(argument)
            for argument in node.arguments
        ]

        old_variables = self.variables

        self.variables = dict(
            zip(
                function.parameters,
                arguments
            )
        )

        try:
            self.execute_block(
                function.body
            )

        except ReturnSignal as signal:
            self.variables = old_variables

            return signal.value

        self.variables = old_variables

        return None


def run_ast(tree):
    interpreter = ASTInterpreter()

    interpreter.execute(tree)
