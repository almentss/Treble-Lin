# main.py
import sys
from lexer import Lexer
from parser import Parser, ParseError # Import ParseError
from interpreter import Interpreter, RuntimeError # Import RuntimeError

def run(source_code):
    # 1. Lexical Analysis
    lexer = Lexer(source_code)
    tokens = lexer.scan_tokens()
    if lexer.had_error:
        sys.exit(65) # Lexical error

    # print("Tokens:")
    # for token in tokens:
    #     print(token)

    # 2. Parsing
    parser = Parser(tokens)
    statements = []
    try:
        statements = parser.parse()
        if parser.had_error:
            sys.exit(65) # Parsing error
        # print("\nAST:")
        # for stmt in statements:
        #     print(stmt)
    except ParseError as e:
        print(e, file=sys.stderr)
        sys.exit(65) # Parsing error

    # 3. Interpretation
    interpreter = Interpreter()
    interpreter.interpret(statements)

def run_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source_code = f.read()
        run(source_code)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        sys.exit(74)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

def run_prompt():
    print("Treble Lin Interpreter (Ctrl+C or 'exit()' to quit)")
    while True:
        try:
            line = input("> ")
            if line.strip() == "exit()":
                break
            run(line)
        except EOFError: # Ctrl+D
            break
        except KeyboardInterrupt: # Ctrl+C
            print("\nExiting interpreter.")
            break
        except Exception as e:
            # Errors already printed by lexer/parser/interpreter
            pass

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Usage: python main.py [script]", file=sys.stderr)
        sys.exit(64)
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()


    print("\n--- Running built-in test cases ---")

    print("\n--- Test 1: Basic Arithmetic and Variable ---")
    code1 = """
    let x = 10;
    let y = x + 5 * 2;
    print(y); // Expected: 20
    """
    run(code1)

    print("\n--- Test 2: If-Else Statement ---")
    code2 = """
    let temp = 25;
    if (temp > 20) {
        print("It's warm!");
    } else {
        print("It's cool!");
    }
    """
    run(code2)

    print("\n--- Test 3: While Loop ---")
    code3 = """
    let i = 3;
    while (i > 0) {
        print(i);
        i = i - 1;
    }
    // Expected: 3, 2, 1
    """
    run(code3)

    print("\n--- Test 4: Function Declaration and Call ---")
    code4 = """
    fun greet(name) {
        print("Hello, " + name + "!");
        return "Greeting done.";
    }
    let message = greet("Treble Lin"); // Expected: Hello, Treble Lin!
    print(message); // Expected: Greeting done.
    """
    run(code4)

    print("\n--- Test 5: Logical Operators (Short-circuiting) ---")
    code5 = """
    print(true and false);    // Expected: false
    print(true or false);     // Expected: true
    print(not true);          // Expected: false
    print(not false);         // Expected: true
    print(1 and 0);           // Expected: 0 (truthy/falsy behavior from sheet)
    print(0 or "fallback");   // Expected: fallback
    """
    run(code5)

    print("\n--- Test 6: Error Handling (Division by Zero) ---")
    code6 = """
    try {
        let result = 10 / 0;
        print(result);
    } catch (e) {
        print("Caught error: " + e); // Expected: Caught error: Division by zero.
    }
    """
    run(code6)

    print("\n--- Test 7: Error Handling (Undefined Variable) ---")
    code7 = """
    try {
        print(undefinedVar); // This will cause a Resolution Error, then if bypassed, a Runtime Error
    } catch (err) {
        print("Caught error: " + err); // Expected: Caught error: Undefined variable 'undefinedVar'.
    }
    """
    run(code7)

    print("\n--- Test 8: Error Handling (Type Error) ---")
    code8 = """
    try {
        print("hello" - 1);
    } catch (err) {
        print("Caught error: " + err); // Expected: Caught error: Operands must be numbers.
    }
    """
    run(code8)

    print("\n--- Test 9: For Loop (desugared) ---")
    code9 = """
    for (let i = 0; i < 3; i = i + 1) {
        print(i);
    }
    // Expected: 0, 1, 2
    """
    run(code9)

    print("\n--- Test 10: Break and Continue ---")
    code10 = """
    let i = 0;
    while (i < 10) {
      i = i + 1;
      if (i == 3) continue;
      if (i == 5) break;
      print(i);
    }
    // Expected Output: 1, 2, 4 (from worksheet)
    """
    run(code10)

    print("\n--- Test 11: Nested Scopes ---")
    code11 = """
    {
      let x = 10;
      {
        let x = 5;
        print(x); // Should print 5
      }
      print(x); // Should print 10
    }
    """
    run(code11)

    print("\n--- Test 12: Multi-line comment ---")
    code12 = """
    /* This is a
    multi-line
    comment */
    let a = 1;
    print(a); // Expected: 1
    """
    run(code12)

    print("\n--- Test 13: Function with no return ---")
    code13 = """
    fun doNothing() {
      // This function doesn't return anything
    }
    let result = doNothing();
    print(result); // Expected: nil
    """
    run(code13)

    print("\n--- Test 14: Function with parameters but no arguments (error) ---")
    code14 = """
    fun sum(a, b) {
      return a + b;
    }
    try {
      print(sum(1));
    } catch (e) {
      print("Caught error: " + e); // Expected: Caught error: Expected 2 arguments but got 1.
    }
    """
    run(code14)

    print("\n--- Test 15: Invalid syntax (unmatched paren) ---")
    code15 = """
    let x = (10 + 5;
    """
    run(code15)

    print("\n--- Test 16: Invalid token ---")
    code16 = """
    let x = @10;
    """
    run(code16)

    print("\n--- Test 17: Complex Try/Catch ---")
    code17 = """
    let globalVar = "original";
    fun riskyFunc(val) {
        if (val == 0) {
            globalVar = "changed by riskyFunc";
            let localErr = "zero error";
            print("Before throw: " + localErr);
            throw "Division by zero in riskyFunc"; // Simulating a throw
        }
        return 10 / val;
    }

    try {
        print("Before try block. Global: " + globalVar);
        riskyFunc(0);
        print("After riskyFunc call (should not reach here)");
    } catch (e) {
        print("In catch block. Error: " + e);
        print("Global in catch: " + globalVar); // Should be "changed by riskyFunc"
        let catchVar = "handled";
        print("Catch var: " + catchVar);
    }
    print("After try/catch. Global: " + globalVar); // Should still be "changed by riskyFunc"
    // print(catchVar); // This should be an undefined variable error if uncommented
    """
    run(code17)