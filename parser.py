# parser.py
import sys
from lexer import Token
from ast import * # Import all AST nodes

class ParseError(Exception):
    def __init__(self, token, message):
        self.token = token
        self.message = message
        super().__init__(f"Parsing Error at line {token.line}, '{token.lexeme}': {message}")

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.had_error = False

    def parse(self):
        statements = []
        while not self._is_at_end():
            try:
                statements.append(self._declaration())
            except ParseError as e:
                print(e, file=sys.stderr)
                self.had_error = True
                self._synchronize() # Error recovery
        return statements

    def _declaration(self):
        if self._match("FUN"): return self._function("function")
        if self._match("VAR"): return self._var_declaration()
        return self._statement()

    def _function(self, kind):
        name = self._consume("IDENTIFIER", f"Expect {kind} name.")
        self._consume("LEFT_PAREN", f"Expect '(' after {kind} name.")
        parameters = []
        if not self._check("RIGHT_PAREN"):
            while True:
                if len(parameters) >= 255: # Arbitrary limit
                    self._error(self._peek(), "Cannot have more than 255 parameters.")
                parameters.append(self._consume("IDENTIFIER", "Expect parameter name."))
                if not self._match("COMMA"):
                    break
        self._consume("RIGHT_PAREN", "Expect ')' after parameters.")
        self._consume("LEFT_BRACE", f"Expect '{{' before {kind} body.")
        body = self._block()
        return FunctionDeclaration(name, parameters, Block(body)) # Body is a Block node

    def _var_declaration(self):
        name = self._consume("IDENTIFIER", "Expect variable name.")
        initializer = None
        if self._match("EQUAL"):
            initializer = self._expression()
        self._consume("SEMICOLON", "Expect ';' after variable declaration.")
        return VarDeclaration(name, initializer)

    def _statement(self):
        if self._match("PRINT"): return self._print_statement()
        if self._match("IF"): return self._if_statement()
        if self._match("WHILE"): return self._while_statement()
        if self._match("FOR"): return self._for_statement()
        if self._match("RETURN"): return self._return_statement()
        if self._match("BREAK"): return self._break_statement()
        if self._match("CONTINUE"): return self._continue_statement()
        if self._match("TRY"): return self._try_catch_statement()
        if self._match("LEFT_BRACE"): return Block(self._block())
        return self._expression_statement()

    def _print_statement(self):
        # Now print takes a single expression, but interpreter will handle multiple for flexibility
        expr = self._expression()
        self._consume("SEMICOLON", "Expect ';' after value.")
        return PrintStatement(expr)

    def _return_statement(self):
        keyword = self._previous()
        value = None
        if not self._check("SEMICOLON"):
            value = self._expression()
        self._consume("SEMICOLON", "Expect ';' after return value.")
        return ReturnStatement(keyword, value)

    def _break_statement(self):
        keyword = self._previous()
        self._consume("SEMICOLON", "Expect ';' after 'break'.")
        return BreakStatement(keyword)

    def _continue_statement(self):
        keyword = self._previous()
        self._consume("SEMICOLON", "Expect ';' after 'continue'.")
        return ContinueStatement(keyword)

    def _try_catch_statement(self):
        self._consume("LEFT_BRACE", "Expect '{' after 'try'.")
        try_block_statements = self._block() # This returns a list of statements
        self._consume("CATCH", "Expect 'catch' after try block.")
        self._consume("LEFT_PAREN", "Expect '(' after 'catch'.")
        error_name_token = self._consume("IDENTIFIER", "Expect error variable name in catch block.")
        self._consume("RIGHT_PAREN", "Expect ')' after error variable name.")
        self._consume("LEFT_BRACE", "Expect '{' before catch block body.")
        catch_block_statements = self._block() # This returns a list of statements
        return TryCatchStatement(Block(try_block_statements), error_name_token, Block(catch_block_statements))


    def _if_statement(self):
        self._consume("LEFT_PAREN", "Expect '(' after 'if'.")
        condition = self._expression()
        self._consume("RIGHT_PAREN", "Expect ')' after if condition.")
        then_branch = self._statement()
        else_branch = None
        if self._match("ELSE"):
            else_branch = self._statement()
        return IfStatement(condition, then_branch, else_branch)

    def _while_statement(self):
        self._consume("LEFT_PAREN", "Expect '(' after 'while'.")
        condition = self._expression()
        self._consume("RIGHT_PAREN", "Expect ')' after while condition.")
        body = self._statement()
        return WhileStatement(condition, body)

    # Implement for loop desugaring here
    def _for_statement(self):
        self._consume("LEFT_PAREN", "Expect '(' after 'for'.")

        initializer = None
        if self._match("VAR"):
            initializer = self._var_declaration()
        elif not self._check("SEMICOLON"):
            initializer = self._expression_statement()
        self._consume("SEMICOLON", "Expect ';' after loop initializer.")

        condition = None
        if not self._check("SEMICOLON"):
            condition = self._expression()
        self._consume("SEMICOLON", "Expect ';' after loop condition.")

        increment = None
        if not self._check("RIGHT_PAREN"):
            increment = self._expression()
        self._consume("RIGHT_PAREN", "Expect ')' after for clauses.")

        body = self._statement()

        # Desugar for loop into a while loop
        if increment:
            # Wrap body and increment in a block
            body = Block([body, ExpressionStatement(increment)])
        if not condition:
            condition = BooleanLiteral(True) # Infinite loop if no condition
        body = WhileStatement(condition, body)
        if initializer:
            # Wrap initializer and while loop in a block
            body = Block([initializer, body])
        return body


    def _block(self):
        statements = []
        while not self._check("RIGHT_BRACE") and not self._is_at_end():
            statements.append(self._declaration())
        self._consume("RIGHT_BRACE", "Expect '}' after block.")
        return statements

    def _expression_statement(self):
        expr = self._expression()
        self._consume("SEMICOLON", "Expect ';' after expression.")
        return ExpressionStatement(expr)

    def _expression(self):
        return self._assignment()

    def _assignment(self):
        expr = self._or() # Changed to _or for logical operator hierarchy

        if self._match("EQUAL"):
            equals = self._previous()
            value = self._assignment() # Right-associativity for assignment

            if isinstance(expr, Variable):
                name = expr.name_token
                return Assignment(name, value)
            # Add other assignable targets here if needed (e.g., properties)
            self._error(equals, "Invalid assignment target.")
        return expr

    def _or(self): # New method for logical OR
        expr = self._and()
        while self._match("LOGICAL_OR"):
            operator = self._previous()
            right = self._and()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def _and(self): # New method for logical AND
        expr = self._equality()
        while self._match("LOGICAL_AND"):
            operator = self._previous()
            right = self._equality()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def _equality(self):
        expr = self._comparison()
        while self._match("EQUAL_EQUAL", "BANG_EQUAL"):
            operator = self._previous()
            right = self._comparison()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def _comparison(self):
        expr = self._term()
        while self._match("GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"):
            operator = self._previous()
            right = self._term()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def _term(self):
        expr = self._factor()
        while self._match("MINUS", "PLUS"):
            operator = self._previous()
            right = self._factor()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def _factor(self):
        expr = self._unary()
        while self._match("SLASH", "STAR"):
            operator = self._previous()
            right = self._unary()
            expr = BinaryExpression(expr, operator, right)
        return expr

    def _unary(self):
        if self._match("BANG", "MINUS", "LOGICAL_NOT"):
            operator = self._previous()
            right = self._unary()
            return UnaryExpression(operator, right)
        return self._call()

    def _call(self):
        expr = self._primary()
        while True:
            if self._match("LEFT_PAREN"):
                expr = self._finish_call(expr)
            else:
                break
        return expr

    def _finish_call(self, callee):
        arguments = []
        if not self._check("RIGHT_PAREN"):
            while True:
                if len(arguments) >= 255:
                    self._error(self._peek(), "Cannot have more than 255 arguments.")
                arguments.append(self._expression())
                if not self._match("COMMA"):
                    break
        paren = self._consume("RIGHT_PAREN", "Expect ')' after arguments.")
        return CallExpression(callee, paren, arguments)

    def _primary(self):
        if self._match("FALSE"): return BooleanLiteral(False)
        if self._match("TRUE"): return BooleanLiteral(True)
        if self._match("NIL"): return NilLiteral()
        if self._match("NUMBER"): return NumberLiteral(self._previous().literal)
        if self._match("STRING"): return StringLiteral(self._previous().literal)
        if self._match("IDENTIFIER"): return Variable(self._previous())
        if self._match("LEFT_PAREN"):
            expr = self._expression()
            self._consume("RIGHT_PAREN", "Expect ')' after expression.")
            return expr

        raise self._error(self._peek(), "Expect expression.")

    # Helper methods for parser
    def _match(self, *types):
        for type in types:
            if self._check(type):
                self._advance()
                return True
        return False

    def _consume(self, type, message):
        if self._check(type):
            return self._advance()
        raise self._error(self._peek(), message)

    def _check(self, type):
        if self._is_at_end():
            return False
        return self._peek().type == type

    def _advance(self):
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self):
        return self._peek().type == "EOF"

    def _peek(self):
        return self.tokens[self.current]

    def _previous(self):
        return self.tokens[self.current - 1]

    def _error(self, token, message):
        self.had_error = True
        return ParseError(token, message)

    def _synchronize(self):
        self.current += 1
        while not self._is_at_end():
            if self._previous().type == "SEMICOLON": return
            if self._peek().type in ["CLASS", "FUN", "VAR", "FOR", "IF", "WHILE", "PRINT", "RETURN", "TRY", "CATCH", "BREAK", "CONTINUE"]: return
            self.current += 1