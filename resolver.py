# resolver.py
import sys
from ast_tl import *
from lexer import Token # For error reporting

class ResolveError(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message
        super().__init__(f"Resolution Error at line {token.line}, '{token.lexeme}': {message}")

class Resolver:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.scopes = [] # Stack of maps: each map represents a scope (local variables)
        self.had_error = False

    def resolve(self, statements):
        for statement in statements:
            self._resolve_statement(statement)

    def _resolve_statement(self, stmt):
        # Visitor pattern could be used here, but direct dispatch for simplicity
        if isinstance(stmt, Block):
            self._begin_scope()
            self.resolve(stmt.statements)
            self._end_scope()
        elif isinstance(stmt, VarDeclaration):
            self._declare(stmt.name_token)
            if stmt.initializer:
                self._resolve_expression(stmt.initializer)
            self._define(stmt.name_token)
        elif isinstance(stmt, FunctionDeclaration):
            self._declare(stmt.name_token)
            self._define(stmt.name_token) # Define function before resolving body for recursion
            self._resolve_function(stmt)
        elif isinstance(stmt, ExpressionStatement):
            self._resolve_expression(stmt.expression)
        elif isinstance(stmt, IfStatement):
            self._resolve_expression(stmt.condition)
            self._resolve_statement(stmt.then_branch)
            if stmt.else_branch:
                self._resolve_statement(stmt.else_branch)
        elif isinstance(stmt, ReturnStatement):
            if stmt.value:
                self._resolve_expression(stmt.value)
        elif isinstance(stmt, WhileStatement):
            self._resolve_expression(stmt.condition)
            self._resolve_statement(stmt.body)
        elif isinstance(stmt, BreakStatement) or isinstance(stmt, ContinueStatement):
            # No specific resolution needed for break/continue, just ensure they are within loops
            pass # We could add loop tracking here for error reporting
        elif isinstance(stmt, TryCatchStatement):
            self._begin_scope() # try block has its own scope
            self.resolve(stmt.try_block.statements)
            self._end_scope()

            self._begin_scope() # catch block has its own scope
            self._declare(stmt.error_name_token)
            self._define(stmt.error_name_token)
            self.resolve(stmt.catch_block.statements)
            self._end_scope()

    def _resolve_expression(self, expr):
        if isinstance(expr, Variable):
            if len(self.scopes) > 0 and expr.name_token.lexeme in self.scopes[-1] and self.scopes[-1][expr.name_token.lexeme] == False:
                self._error(expr.name_token, "Cannot read local variable in its own initializer.")
            self._resolve_local(expr, expr.name_token)
        elif isinstance(expr, Assignment):
            self._resolve_expression(expr.value)
            self._resolve_local(expr, expr.name_token)
        elif isinstance(expr, BinaryExpression):
            self._resolve_expression(expr.left)
            self._resolve_expression(expr.right)
        elif isinstance(expr, CallExpression):
            self._resolve_expression(expr.callee)
            for arg in expr.arguments:
                self._resolve_expression(arg)
        elif isinstance(expr, UnaryExpression):
            self._resolve_expression(expr.right)
        elif isinstance(expr, (NumberLiteral, StringLiteral, BooleanLiteral, NilLiteral)):
            pass # Literals don't need resolution

    def _resolve_function(self, function_decl):
        self._begin_scope()
        for param in function_decl.parameters:
            self._declare(param)
            self._define(param)
        self.resolve(function_decl.body.statements)
        self._end_scope()

    def _begin_scope(self):
        self.scopes.append({})

    def _end_scope(self):
        self.scopes.pop()

    def _declare(self, name_token):
        if not self.scopes: return
        scope = self.scopes[-1]
        if name_token.lexeme in scope:
            self._error(name_token, "Already a variable with this name in this scope.")
        scope[name_token.lexeme] = False # False means declared but not defined

    def _define(self, name_token):
        if not self.scopes: return
        self.scopes[-1][name_token.lexeme] = True # True means defined

    def _resolve_local(self, expr, name_token):
        for i in reversed(range(len(self.scopes))):
            if name_token.lexeme in self.scopes[i]:
                self.interpreter.locals[expr] = len(self.scopes) - 1 - i # Store distance
                return
        # Not found. Assume it's a global variable. Interpreter will try to get it from globals.
        # This means undefined variable errors are now caught at runtime if not resolved here.
        # For stricter static analysis, we could raise an error here.
        # But for this simple interpreter, it's fine for globals to be 'implicitly' defined.
        # However, for user-defined globals, it is still better to explicitly define them.
        pass


    def _error(self, token, message):
        print(f"Resolution Error at line {token.line}, '{token.lexeme}': {message}", file=sys.stderr)
        self.had_error = True