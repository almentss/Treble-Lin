# environment.py
class Environment:
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent

    def define(self, name, value):
        self.values[name] = value

    def assign(self, name_token, value):
        if name_token.lexeme in self.values:
            self.values[name_token.lexeme] = value
            return
        if self.parent:
            self.parent.assign(name_token, value)
            return
        raise RuntimeError(f"Undefined variable '{name_token.lexeme}'.", name_token)


    def get(self, name_token):
        if name_token.lexeme in self.values:
            return self.values[name_token.lexeme]
        if self.parent:
            return self.parent.get(name_token)
        raise RuntimeError(f"Undefined variable '{name_token.lexeme}'.", name_token)


    def ancestor(self, distance):
        environment = self
        for _ in range(distance):
            environment = environment.parent
        return environment

    def assign_at(self, distance, name_token, value):
        self.ancestor(distance).values[name_token.lexeme] = value

    def get_at(self, distance, name_token):
        return self.ancestor(distance).values[name_token.lexeme]
