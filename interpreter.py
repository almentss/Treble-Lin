# interpreter.py
import sys
import math
from ast_tl import *
from lexer import Token 
from environment import Environment
from resolver import Resolver 

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
        self.closure = closure 
        self.is_initializer = is_initializer

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)

        for i, param_token in enumerate(self.declaration.parameters):
            environment.define(param_token.lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body.statements, environment)
        except ReturnException as e:
            if self.is_initializer:
                return self.closure.get_at(0, Token("this", "this", None, -1))
            return e.value

        if self.is_initializer:
            return self.closure.get_at(0, Token("this", "this", None, -1))
        return None 

    def arity(self):
        return len(self.declaration.parameters)

    def bind(self, instance):
        environment = Environment(self.closure)
        environment.define("this", instance)
        return TrebleLinFunction(self.declaration, environment, self.is_initializer)


    def __repr__(self):
        return f"<fun {self.declaration.name_token.lexeme}>"


class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {} 

        self.globals.define("print", self._print_builtin())

    def _print_builtin(self):
        class PrintBuiltin(TrebleLinCallable):
            def arity(self): 

                return -1 
            
            def call(self, interpreter, arguments):
                if not arguments:
                    print()
                    return None

                first_arg = arguments[0]
            
                if isinstance(first_arg, str) and '%' in first_arg and len(arguments) > 1:
                    try:
                        format_args = tuple(arguments[1:])
                        output = first_arg % format_args
                        print(output, end='') 
                        sys.stdout.flush()
                    except (TypeError, ValueError) as e:
                        raise RuntimeError(f"Invalid arguments for format string '{first_arg}'. Details: {e}")
                
                else:
                    output = " ".join([interpreter._stringify(arg) for arg in arguments])
                    print(output,end="")
                
                return None

            def __repr__(self): return "<native fun print>"
        return PrintBuiltin()


    def interpret(self, statements):
        resolver = Resolver(self)
        resolver.resolve(statements)
        if resolver.had_error:
            sys.exit(65)

        try:
            for statement in statements:
                self._execute(statement)
        except RuntimeError as e:
            if e.token:
                print(f"Runtime Error at line {e.token.line}: {e.message}", file=sys.stderr)
            else:
                print(f"Runtime Error: {e.message}", file=sys.stderr)
            sys.exit(70) 

    def _execute(self, stmt):
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

    def _execute_TryCatchStatement(self, stmt):
        previous_environment = self.environment
        try:
            self.environment = Environment(self.environment)
            self.execute_block(stmt.try_block.statements, self.environment)
        except RuntimeError as err:
            catch_env = Environment(previous_environment)
            catch_env.define(stmt.error_name_token.lexeme, str(err.message)) 
            self.environment = catch_env
            self.execute_block(stmt.catch_block.statements, self.environment)
        finally:
            self.environment = previous_environment 

    def execute_block(self, statements, environment):
        previous_environment = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self._execute(statement)
        finally:
            self.environment = previous_environment 

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
        elif operator_type == "MODULO": 
            self._check_number_operands(expr.operator_token, left, right)
            if right == 0:
                raise RuntimeError("Modulo by zero.", expr.operator_token)
            if isinstance(left, int) and isinstance(right, int):
                return left % right
            return left % right 
        elif operator_type == "PLUS":
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            elif isinstance(left, str) and isinstance(right, (int, float)):
                return left + str(right) 
            elif isinstance(left, (int, float)) and isinstance(right, str):
                return str(left) + right 
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
        if expr in self.locals: 
            distance = self.locals[expr]
            self.environment.assign_at(distance, expr.name_token, value)
        else: 
            self.globals.assign(expr.name_token, value)
        return value

    def _evaluate_ArrayLiteral(self, expr):
        return [self._evaluate(element) for element in expr.elements]

    def _evaluate_IndexExpression(self, expr):
        array = self._evaluate(expr.array)
        index = self._evaluate(expr.index)

        if not isinstance(array, list):
            raise RuntimeError("Can only index arrays (lists).", expr.array)
        if not isinstance(index, int):
            raise RuntimeError("Array index must be an integer.", expr.index)

        try:
            return array[index]
        except IndexError:
            raise RuntimeError(f"Array index {index} out of bounds.", expr.index)


    def _evaluate_CallExpression(self, expr):
        callee = self._evaluate(expr.callee)
        arguments = [self._evaluate(arg) for arg in expr.arguments]

        if not isinstance(callee, TrebleLinCallable):
            raise RuntimeError("Can only call functions and classes.", expr.paren_token)

        if callee.arity() != -1 and len(arguments) != callee.arity():
            raise RuntimeError(f"Expected {callee.arity()} arguments but got {len(arguments)}.", expr.paren_token)

        return callee.call(self, arguments)

    def _lookup_variable(self, name_token, expr):
        if expr in self.locals:
            distance = self.locals[expr]
            return self.environment.get_at(distance, name_token)
        else: # Global variable
            return self.globals.get(name_token)

    def _is_truthy(self, value):
        if value is None: return False
        if isinstance(value, bool): return value
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
        if isinstance(value, list):
            items = [self._stringify(item) for item in value]
            return "[" + ", ".join(items) + "]"
        return str(value)
    
    def _evaluate_ArrayLiteral(self, expr):
        elements = []
        for element_expr in expr.elements:
            elements.append(self._evaluate(element_expr))
        return elements

    def _evaluate_Subscript(self, expr):
        callee = self._evaluate(expr.callee)
        if not isinstance(callee, list):
            raise RuntimeError("Can only subscript on arrays.", expr.bracket_token)

        index = self._evaluate(expr.index)
        if not isinstance(index, int):
            raise RuntimeError("Array index must be an integer.", expr.bracket_token)

        try:
            return callee[index]
        except IndexError:
            raise RuntimeError("Array index out of bounds.", expr.bracket_token)

    def _evaluate_Set(self, expr):
        callee_obj = self._evaluate(expr.callee)
        if not isinstance(callee_obj, list):
            raise RuntimeError("Can only assign to elements of arrays.", expr.bracket_token)

        index = self._evaluate(expr.index)
        if not isinstance(index, int):
            raise RuntimeError("Array index must be an integer.", expr.bracket_token)
        
        value = self._evaluate(expr.value)

        if index < -len(callee_obj) or index >= len(callee_obj):
             raise RuntimeError("Array index out of bounds for assignment.", expr.bracket_token)
        
        callee_obj[index] = value
        return value
