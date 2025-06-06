# ast.py
class ASTNode:
    pass

class Expression(ASTNode):
    pass

class Statement(ASTNode):
    pass

class NumberLiteral(Expression):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Number({self.value})"

class StringLiteral(Expression):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"String('{self.value}')"

class BooleanLiteral(Expression):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Boolean({self.value})"

class NilLiteral(Expression):
    def __init__(self):
        self.value = None
    def __repr__(self):
        return "Nil()"

class Variable(Expression):
    def __init__(self, name_token):
        self.name_token = name_token 
    def __repr__(self):
        return f"Variable('{self.name_token.lexeme}')"

class Assignment(Expression):
    def __init__(self, name_token, value):
        self.name_token = name_token
        self.value = value
    def __repr__(self):
        return f"Assignment('{self.name_token.lexeme}', {self.value})"

class BinaryExpression(Expression):
    def __init__(self, left, operator_token, right):
        self.left = left
        self.operator_token = operator_token
        self.right = right
    def __repr__(self):
        return f"Binary({self.left}, '{self.operator_token.lexeme}', {self.right})"

class UnaryExpression(Expression):
    def __init__(self, operator_token, right):
        self.operator_token = operator_token
        self.right = right
    def __repr__(self):
        return f"Unary('{self.operator_token.lexeme}', {self.right})"

class VarDeclaration(Statement):
    def __init__(self, name_token, initializer=None):
        self.name_token = name_token
        self.initializer = initializer
    def __repr__(self):
        return f"VarDecl('{self.name_token.lexeme}', {self.initializer})"

class ExpressionStatement(Statement):
    def __init__(self, expression):
        self.expression = expression
    def __repr__(self):
        return f"ExprStmt({self.expression})"

class Block(Statement):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"Block({self.statements})"

class IfStatement(Statement):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    def __repr__(self):
        return f"If({self.condition}, {self.then_branch}, {self.else_branch})"

class WhileStatement(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    def __repr__(self):
        return f"While({self.condition}, {self.body})"

class FunctionDeclaration(Statement):
    def __init__(self, name_token, parameters, body):
        self.name_token = name_token
        self.parameters = parameters 
        self.body = body 
    def __repr__(self):
        return f"FunDecl('{self.name_token.lexeme}', {self.parameters}, {self.body})"

class CallExpression(Expression):
    def __init__(self, callee, paren_token, arguments):
        self.callee = callee 
        self.paren_token = paren_token
        self.arguments = arguments 
    def __repr__(self):
        return f"Call({self.callee}, {self.arguments})"

class ReturnStatement(Statement):
    def __init__(self, keyword_token, value=None):
        self.keyword_token = keyword_token 
        self.value = value
    def __repr__(self):
        return f"Return({self.value})"

class BreakStatement(Statement):
    def __init__(self, keyword_token):
        self.keyword_token = keyword_token
    def __repr__(self):
        return "Break()"

class ContinueStatement(Statement):
    def __init__(self, keyword_token):
        self.keyword_token = keyword_token
    def __repr__(self):
        return "Continue()"

class TryCatchStatement(Statement):
    def __init__(self, try_block, error_name_token, catch_block):
        self.try_block = try_block
        self.error_name_token = error_name_token
        self.catch_block = catch_block
    def __repr__(self):
        return f"TryCatch(try={self.try_block}, error_name='{self.error_name_token.lexeme}', catch={self.catch_block})"
