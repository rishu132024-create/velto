class ASTInterpreterError(Exception):
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

        if isinstance(node, BinaryOpNode):
            return self.evaluate_binary(node)

        raise ASTInterpreterError(
            f"Unknown expression node: {type(node).__name__}"
        )

    def evaluate_binary(self, node):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)
        operator = node.operator

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

        if isinstance(node, SayNode):
            value = self.evaluate(node.value)
            print(value)
            return

        if isinstance(node, ExpressionStatementNode):
            self.evaluate(node.expression)
            return

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
    BinaryOpNode,
    AssignmentNode,
    SayNode,
    ExpressionStatementNode
)


def run_ast(tree):
    interpreter = ASTInterpreter()
    interpreter.execute(tree)
