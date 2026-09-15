class ASTInterpreterError(Exception):
    pass


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class ASTInterpreter:
    def __init__(self):
        self.variables = {}

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
                raise ASTInterpreterError(
                    f"Variable not found: {node.name}"
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

            if not isinstance(index, int):
                raise ASTInterpreterError(
                    "List or string index must be an integer"
                )

            try:
                return value[index]
            except (IndexError, TypeError):
                raise ASTInterpreterError(
                    f"Index out of range: {index}"
                )

        if isinstance(node, BinaryOpNode):
            return self.evaluate_binary(node)

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

        except Exception as error:
            raise ASTInterpreterError(str(error))

        raise ASTInterpreterError(
            f"Unknown operator: {operator}"
        )

    def execute_block(self, statements):
        for statement in statements:
            self.execute(statement)

    def execute(self, node):
        if isinstance(node, Program):
            self.execute_block(node.statements)
            return

        if isinstance(node, AssignmentNode):
            value = self.evaluate(node.value)
            self.variables[node.name] = value
            return

        if isinstance(node, IndexAssignmentNode):
            target = self.evaluate(node.target)
            index = self.evaluate(node.index)
            value = self.evaluate(node.value)

            if not isinstance(index, int):
                raise ASTInterpreterError(
                    "List or string index must be an integer"
                )

            if not isinstance(target, list):
                raise ASTInterpreterError(
                    "Only lists can be modified by index"
                )

            try:
                target[index] = value
            except IndexError:
                raise ASTInterpreterError(
                    f"Index out of range: {index}"
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
            loop_count = 0

            while self.evaluate(node.condition):
                loop_count += 1

                if loop_count > 100000:
                    raise ASTInterpreterError(
                        "Possible infinite loop"
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

            if not isinstance(iterable, (list, str)):
                raise ASTInterpreterError(
                    "Object is not iterable"
                )

            for value in iterable:
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

        raise ASTInterpreterError(
            f"Unknown statement node: {type(node).__name__}"
        )


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
    ContinueNode
)


def run_ast(tree):
    interpreter = ASTInterpreter()
    interpreter.execute(tree)
