from pathlib import Path

from velto_parser import (
    Program,
    NumberNode,
    StringNode,
    BooleanNode,
    NoneNode,
    IdentifierNode,
    ListNode,
    DictionaryNode,
    TupleNode,
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
    ReturnNode,
    ImportNode,
    ParserError,
    parse
)

from velto_lexer import tokenize
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
    def __init__(
        self,
        name,
        parameters,
        body,
        closure
    ):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.closure = closure


class Module:
    def __init__(self, name):
        self.name = name
        self.variables = {}
        self.functions = {}


class ASTInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.modules = {}
        self.loop_limit = 10000

    def error(self, message, node=None):
        line = None

        if node is not None:
            line = getattr(
                node,
                "line",
                None
            )

        raise ASTInterpreterError(
            message,
            line
        )

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
            if "." in node.name:
                parts = node.name.split(".")

                module_name = parts[0]
                member_name = ".".join(
                    parts[1:]
                )

                if module_name in self.modules:
                    module = self.modules[
                        module_name
                    ]

                    if member_name in module.variables:
                        return module.variables[
                            member_name
                        ]

                    self.error(
                        f"Module member not found: {node.name}",
                        node
                    )

            if node.name not in self.variables:
                self.error(
                    f"Variable not found: {node.name}",
                    node
                )

            return self.variables[
                node.name
            ]

        if isinstance(node, ListNode):
            return [
                self.evaluate(element)
                for element in node.elements
            ]

        if isinstance(node, TupleNode):
            return tuple(
                self.evaluate(element)
                for element in node.elements
            )

        if isinstance(node, DictionaryNode):
            result = {}

            for key_node, value_node in node.pairs:
                key = self.evaluate(
                    key_node
                )

                value = self.evaluate(
                    value_node
                )

                try:
                    result[key] = value

                except TypeError:
                    self.error(
                        "Dictionary key must be hashable",
                        key_node
                    )

            return result

        if isinstance(node, IndexNode):
            value = self.evaluate(
                node.value
            )

            index = self.evaluate(
                node.index
            )

            try:
                return value[index]

            except KeyError:
                self.error(
                    f"Key not found: {index}",
                    node
                )

            except (
                IndexError,
                TypeError
            ):
                self.error(
                    f"Invalid index: {index}",
                    node
                )

        if isinstance(node, BinaryOpNode):
            return self.evaluate_binary(
                node
            )

        if isinstance(node, CallNode):
            return self.call_function(
                node
            )

        self.error(
            f"Unknown expression node: "
            f"{type(node).__name__}",
            node
        )

    def evaluate_binary(self, node):
        left = self.evaluate(
            node.left
        )

        right = self.evaluate(
            node.right
        )

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

        except (
            TypeError,
            ZeroDivisionError
        ) as error:
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

        if isinstance(node, ImportNode):
            self.import_module(
                node
            )

            return

        if isinstance(node, AssignmentNode):
            value = self.evaluate(
                node.value
            )

            self.variables[
                node.name
            ] = value

            return

        if isinstance(node, IndexAssignmentNode):
            target = self.evaluate(
                node.target
            )

            index = self.evaluate(
                node.index
            )

            value = self.evaluate(
                node.value
            )

            if not isinstance(
                target,
                (list, dict)
            ):
                self.error(
                    "Index assignment requires a list or dictionary",
                    node
                )

            try:
                target[index] = value

            except (
                IndexError,
                KeyError,
                TypeError
            ):
                self.error(
                    f"Invalid index: {index}",
                    node
                )

            return

        if isinstance(node, SayNode):
            value = self.evaluate(
                node.value
            )

            print(value)

            return

        if isinstance(
            node,
            ExpressionStatementNode
        ):
            self.evaluate(
                node.expression
            )

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

            while self.evaluate(
                node.condition
            ):
                count += 1

                if count > self.loop_limit:
                    self.error(
                        "Possible infinite loop",
                        node
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
                self.error(
                    "Object is not iterable",
                    node
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
            self.functions[
                node.name
            ] = Function(
                node.name,
                node.parameters,
                node.body,
                dict(self.variables)
            )

            return

        if isinstance(node, ReturnNode):
            if node.value is None:
                raise ReturnSignal(None)

            value = self.evaluate(
                node.value
            )

            raise ReturnSignal(value)

        self.error(
            f"Unknown statement node: "
            f"{type(node).__name__}",
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
                return BUILTINS[
                    node.name
                ](arguments)

            except StdLibError as error:
                self.error(
                    str(error),
                    node
                )

        if "." in node.name:
            parts = node.name.split(".")

            module_name = parts[0]

            function_name = ".".join(
                parts[1:]
            )

            if module_name not in self.modules:
                self.error(
                    f"Module not found: {module_name}",
                    node
                )

            return self.call_module_function(
                self.modules[module_name],
                function_name,
                node,
                arguments
            )

        if node.name not in self.functions:
            self.error(
                f"Function not found: {node.name}",
                node
            )

        function = self.functions[
            node.name
        ]

        return self.execute_function(
            function,
            node,
            arguments
        )

    def execute_function(
        self,
        function,
        node,
        arguments
    ):
        if len(arguments) != len(
            function.parameters
        ):
            self.error(
                f"Function {function.name} expects "
                f"{len(function.parameters)} "
                f"arguments, got "
                f"{len(arguments)}",
                node
            )

        old_variables = self.variables
        old_functions = self.functions

        self.variables = dict(
            function.closure
        )

        self.functions = dict(
            self.functions
        )

        for parameter, argument in zip(
            function.parameters,
            arguments
        ):
            self.variables[
                parameter
            ] = argument

        try:
            self.execute_block(
                function.body
            )

        except ReturnSignal as signal:
            return signal.value

        finally:
            self.variables = old_variables
            self.functions = old_functions

        return None

    def call_module_function(
        self,
        module,
        function_name,
        node,
        arguments
    ):
        if function_name not in module.functions:
            self.error(
                f"Module function not found: "
                f"{module.name}.{function_name}",
                node
            )

        function = module.functions[
            function_name
        ]

        if len(arguments) != len(
            function.parameters
        ):
            self.error(
                f"Function "
                f"{module.name}.{function_name} "
                f"expects "
                f"{len(function.parameters)} "
                f"arguments, got "
                f"{len(arguments)}",
                node
            )

        old_variables = self.variables
        old_functions = self.functions

        self.variables = dict(
            module.variables
        )

        self.functions = dict(
            module.functions
        )

        for parameter, argument in zip(
            function.parameters,
            arguments
        ):
            self.variables[
                parameter
            ] = argument

        try:
            self.execute_block(
                function.body
            )

        except ReturnSignal as signal:
            return signal.value

        finally:
            self.variables = old_variables
            self.functions = old_functions

        return None

    def import_module(self, node):
        module_name = node.name

        if module_name in self.modules:
            return

        module_path = (
            Path("examples")
            / f"{module_name}.vlt"
        )

        if not module_path.exists():
            self.error(
                f"Module not found: {module_name}",
                node
            )

        try:
            source = module_path.read_text(
                encoding="utf-8"
            )

            tokens = tokenize(
                source
            )

            tree = parse(
                tokens
            )

        except ParserError as error:
            self.error(
                f"Module '{module_name}' "
                f"parse error: {error.message}",
                node
            )

        except Exception as error:
            self.error(
                f"Module '{module_name}' "
                f"lexer error: {error}",
                node
            )

        module_interpreter = ASTInterpreter()

        try:
            module_interpreter.execute(
                tree
            )

        except ASTInterpreterError as error:
            self.error(
                f"Module '{module_name}' "
                f"error: {error.message}",
                node
            )

        module = Module(
            module_name
        )

        module.variables = dict(
            module_interpreter.variables
        )

        module.functions = dict(
            module_interpreter.functions
        )

        self.modules[
            module_name
        ] = module


def run_ast(tree):
    interpreter = ASTInterpreter()
    interpreter.execute(tree)
