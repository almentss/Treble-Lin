# interpreter.py
import sys
import math
from ast_tl import *
from lexer import Token # For error reporting
from environment import Environment
from resolver import Resolver # Import Resolver

# Custom exceptions for control flow and runtime errors
class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class BreakLoop(Exception):
    pass

class ContinueLoop(Exception):
    pass

class RuntimeError(Exception):
    def __init__(self, message, token=None):
        super().__init__(message)
        self.token = token
        self.message = message

class TrebleLinCallable:
    def arity(self):
        raise NotImplementedError

    def call(self, interpreter, arguments):
        raise NotImplementedError

class TrebleLinFunction(TrebleLinCallable):
    def __init__(self, declaration, closure, is_initializer=False):
        self.declaration = declaration
        self.closure = closure # Environment where function was declared
        self.is_initializer = is_initializer

    def call(self, interpreter, arguments):
        # Create a new environment for the function's execution, parented by the closure
        environment = Environment(self.closure)

        # Bind parameters to arguments
        for i, param_token in enumerate(self.declaration.parameters):
            environment.define(param_token.lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body.statements, environment)
        except ReturnException as e:
            if self.is_initializer: # Initializers implicitly return 'this'
                return self.closure.get_at(0, Token("this", "this", None, -1))
            return e.value

        if self.is_initializer: # Initializers implicitly return 'this' even without explicit return
            return self.closure.get_at(0, Token("this", "this", None, -1))
        return None # Implicit nil return if no return statement

    def arity(self):
        return len(self.declaration.parameters)

    def bind(self, instance):
        # Used for methods (not implemented in this basic example, but good to keep in mind)
        # This creates a new environment for the method call, binding 'this'
        environment = Environment(self.closure)
        environment.define("this", instance)
        return TrebleLinFunction(self.declaration, environment, self.is_initializer)


    def __repr__(self):
        return f"<fun {self.declaration.name_token.lexeme}>"

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {} # Stores distances (Expression AST node -> int distance)

        # Define built-in print function
        self.globals.define("print", self._print_builtin())

    def _print_builtin(self):
        class PrintBuiltin(TrebleLinCallable):
            def arity(self): return -1 # -1 means variable arity for simplicity (can take any number of args)
            def call(self, interpreter, arguments):
                output = " ".join([interpreter._stringify(arg) for arg in arguments])
                print(output)
                return None
            def __repr__(self): return "<native fun print>"
        return PrintBuiltin()


    def interpret(self, statements):
        # First, resolve variables
        resolver = Resolver(self)
        resolver.resolve(statements)
        if resolver.had_error:
            # If resolution failed, stop interpretation.
            sys.exit(65) # Exit code for data format error

        try:
            for statement in statements:
                self._execute(statement)
        except RuntimeError as e:
            # Report the runtime error
            if e.token:
                print(f"Runtime Error at line {e.token.line}: {e.message}", file=sys.stderr)
            else:
                print(f"Runtime Error: {e.message}", file=sys.stderr)
            sys.exit(70) # Exit code for runtime error

    def _execute(self, stmt):
        # Using ASDL like dispatch (similar to how visitors work)
        method_name = f'_execute_{type(stmt).__name__}'
        if hasattr(self, method_name):
            getattr(self, method_name)(stmt)
        else:
            raise RuntimeError(f"Unknown statement type during execution: {type(stmt)}")


    def _execute_ExpressionStatement(self, stmt):
        self._evaluate(stmt.expression)

    def _execute_VarDeclaration(self, stmt):
        value = None
        if stmt.initializer:
            value = self._evaluate(stmt.initializer)
        self.environment.define(stmt.name_token.lexeme, value)

    def _execute_Block(self, stmt):
        self.execute_block(stmt.statements, Environment(self.environment))

    def _execute_IfStatement(self, stmt):
        if self._is_truthy(self._evaluate(stmt.condition)):
            self._execute(stmt.then_branch)
        elif stmt.else_branch:
            self._execute(stmt.else_branch)

    def _execute_WhileStatement(self, stmt):
        while self._is_truthy(self._evaluate(stmt.condition)):
            try:
                self._execute(stmt.body)
            except BreakLoop:
                break
            except ContinueLoop:
                continue

    def _execute_FunctionDeclaration(self, stmt):
        function = TrebleLinFunction(stmt, self.environment, False)
        self.environment.define(stmt.name_token.lexeme, function)

    def _execute_ReturnStatement(self, stmt):
        value = None
        if stmt.value:
            value = self._evaluate(stmt.value)
        raise ReturnException(value)

    def _execute_BreakStatement(self, stmt):
        raise BreakLoop()

    def _execute_ContinueStatement(self, stmt):
        raise ContinueLoop()

    def _execute_PrintStatement(self, stmt):
        # For simplicity, print is now a built-in function that gets evaluated
        # This assumes _print_builtin can handle what's passed to it.
        # If print was just a keyword, we would directly print self._stringify(self._evaluate(stmt.expression))
        # But given the design, treating 'print' as a call to a built-in is more flexible.
        # For now, it simply evaluates the expression and prints it.
        # If we wanted to allow print(a, b, c), the parser would need to treat 'print' as a call and
        # _print_builtin would handle multiple arguments.
        # The current parser treats 'print' as a statement followed by a single expression.
        # Let's adjust it to take multiple args in the _print_builtin call.
        # If the parser allows `print(expr1, expr2, ...);`, then the PrintStatement AST node
        # would need to hold a list of expressions. For now, it holds one.
        # A simple compromise: `print` keyword takes one expression, but the built-in can take multiple.
        # For the provided AST `PrintStatement(expression)`, we'll just print that one.
        sys.stdout.write(str(self._stringify(self._evaluate(stmt.expression))))


    def _execute_TryCatchStatement(self, stmt):
        previous_environment = self.environment
        try:
            self.environment = Environment(self.environment) # Enter a new scope for the try block
            self.execute_block(stmt.try_block.statements, self.environment)
        except RuntimeError as err:
            # Catch the runtime error and execute the catch block
            # The catch block's environment is parented by the environment *before* the try block,
            # so variables declared outside try are accessible.
            catch_env = Environment(previous_environment)
            catch_env.define(stmt.error_name_token.lexeme, str(err.message)) # Store error message
            self.environment = catch_env
            self.execute_block(stmt.catch_block.statements, self.environment)
        finally:
            self.environment = previous_environment # Restore environment

    def execute_block(self, statements, environment):
        previous_environment = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self.environment = previous_environment # Restore environment

    def _evaluate(self, expr):
        method_name = f'_evaluate_{type(expr).__name__}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(expr)
        else:
            raise RuntimeError(f"Unknown expression type during evaluation: {type(expr)}")

    def _evaluate_NumberLiteral(self, expr): return expr.value
    def _evaluate_StringLiteral(self, expr): return expr.value
    def _evaluate_BooleanLiteral(self, expr): return expr.value
    def _evaluate_NilLiteral(self, expr): return None

    def _evaluate_UnaryExpression(self, expr):
        right = self._evaluate(expr.right)
        if expr.operator_token.type == "MINUS":
            self._check_number_operand(expr.operator_token, right)
            return -right
        elif expr.operator_token.type == "BANG" or expr.operator_token.type == "LOGICAL_NOT":
            return not self._is_truthy(right)
        return None

    def _evaluate_BinaryExpression(self, expr):
        left = self._evaluate(expr.left)
        operator_type = expr.operator_token.type

        # Short-circuiting for logical AND/OR
        if operator_type == "LOGICAL_OR":
            if self._is_truthy(left): return left
            right = self._evaluate(expr.right)
            return right
        if operator_type == "LOGICAL_AND":
            if not self._is_truthy(left): return left
            right = self._evaluate(expr.right)
            return right

        right = self._evaluate(expr.right)

        if operator_type == "MINUS":
            self._check_number_operands(expr.operator_token, left, right)
            return left - right
        elif operator_type == "SLASH":
            self._check_number_operands(expr.operator_token, left, right)
            if right == 0:
                raise RuntimeError("Division by zero.", expr.operator_token)
            return left / right
        elif operator_type == "STAR":
            self._check_number_operands(expr.operator_token, left, right)
            return left * right
        elif operator_type == "PLUS":
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            elif isinstance(left, str) and isinstance(right, (int, float)):
                return left + str(right) # 將數字轉換為字符串
            elif isinstance(left, (int, float)) and isinstance(right, str):
                return str(left) + right # 將數字轉換為字符串
            raise RuntimeError("Operands must be two numbers or two strings for '+'.", expr.operator_token)
        elif operator_type == "GREATER":
            self._check_number_operands(expr.operator_token, left, right)
            return left > right
        elif operator_type == "GREATER_EQUAL":
            self._check_number_operands(expr.operator_token, left, right)
            return left >= right
        elif operator_type == "LESS":
            self._check_number_operands(expr.operator_token, left, right)
            return left < right
        elif operator_type == "LESS_EQUAL":
            self._check_number_operands(expr.operator_token, left, right)
            return left <= right
        elif operator_type == "BANG_EQUAL":
            return not self._is_equal(left, right)
        elif operator_type == "EQUAL_EQUAL":
            return self._is_equal(left, right)

        return None

    def _evaluate_Variable(self, expr):
        return self._lookup_variable(expr.name_token, expr)

    def _evaluate_Assignment(self, expr):
        value = self._evaluate(expr.value)
        if expr in self.locals: # Check if resolved
            distance = self.locals[expr]
            self.environment.assign_at(distance, expr.name_token, value)
        else: # Global variable assignment
            self.globals.assign(expr.name_token, value)
        return value

    def _evaluate_CallExpression(self, expr):
        callee = self._evaluate(expr.callee)
        arguments = [self._evaluate(arg) for arg in expr.arguments]

        if not isinstance(callee, TrebleLinCallable):
            raise RuntimeError("Can only call functions and classes.", expr.paren_token)

        # Allow variable arity for built-ins, but enforce for user functions
        if callee.arity() != -1 and len(arguments) != callee.arity():
            raise RuntimeError(f"Expected {callee.arity()} arguments but got {len(arguments)}.", expr.paren_token)

        return callee.call(self, arguments)

    # Helper for looking up variables, using resolution results if available
    def _lookup_variable(self, name_token, expr):
        if expr in self.locals:
            distance = self.locals[expr]
            return self.environment.get_at(distance, name_token)
        else: # Global variable
            return self.globals.get(name_token)

    def _is_truthy(self, value):
        if value is None: return False
        if isinstance(value, bool): return value
        # Numbers, strings, etc. are truthy by default (as per sheet)
        # For numbers, 0 could be considered falsy in some languages, but here all numbers are truthy.
        # This is a design choice.
        return True

    def _is_equal(self, a, b):
        if a is None and b is None: return True
        if a is None: return False
        return a == b

    def _check_number_operand(self, operator, operand):
        if not isinstance(operand, (int, float)):
            raise RuntimeError("Operand must be a number.", operator)

    def _check_number_operands(self, operator, left, right):
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise RuntimeError("Operands must be numbers.", operator)

    def _stringify(self, value):
        if value is None: return "nil"
        if isinstance(value, float) and value == int(value): return str(int(value))
        if isinstance(value, bool): return "true" if value else "false"
        return str(value)