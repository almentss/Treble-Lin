// test_script.tl
//45-48
// --- Section 1: Basic Declarations and Arithmetic ---
let a = 10;
let b = 5;
let c = a + b * 2; // 10 + 10 = 20
print("Section 1:");
print(a); // Expected: 10
print(b); // Expected: 5
print(c); // Expected: 20
print(c / 2); // Expected: 10

let str1 = "Hello, ";
let str2 = "Treble Lin!";
print(str1 + str2); // Expected: Hello, Treble Lin!
print(true and false); // Expected: false
print(true or false);  // Expected: true
print(not true);       // Expected: false

// --- Section 2: Conditional Statements (if/else) ---
print("\nSection 2:");
let temp = 25;
if (temp > 20) {
    print("It's warm!"); // Expected: It's warm!
} else {
    print("It's cool!");
}

if (temp < 15) {
    print("It's cold!");
} else if (temp >= 20 and temp < 30) {
    print("It's pleasant."); // Expected: It's pleasant.
} else {
    print("Extreme weather!");
}

// --- Section 3: Loops (while, for, break, continue) ---
print("\nSection 3:");
let i = 0;
while (i < 3) {
    print("While loop count: " + i); // Expected: 0, 1, 2
    i = i + 1;
}

// For loop desugared to while loop internally
//for (let j = 0; j < 3; j = j + 1) {
//    print("For loop count: " + j); // Expected: 0, 1, 2
//}

let k = 0;
print("Break/Continue Test:");
while (k < 10) {
    k = k + 1;
    if (k == 3) continue; // Skip 3
    if (k == 5) break;    // Exit at 5
    print("k: " + k); // Expected: k: 1, k: 2, k: 4
}


// --- Section 4: Functions ---
print("\nSection 4:");

fun add(x, y) {
    return x + y;
}

fun multiply(a, b) {
    return a * b;
}

fun greet(name) {
    print("Greetings, " + name + "!");
}

let sum_result = add(7, 3);
print("Sum: " + sum_result); // Expected: Sum: 10

let prod_result = multiply(4, 5);
print("Product: " + prod_result); // Expected: Product: 20

greet("Alice"); // Expected: Greetings, Alice!

// Function without explicit return (should return nil)
fun do_nothing() {
    print("Doing nothing...");
}
let nothing_val = do_nothing(); // Expected: Doing nothing...
print("Result of do_nothing: " + nothing_val); // Expected: Result of do_nothing: nil

// Recursion (Factorial)
fun factorial(n) {
    if (n == 0) return 1;
    if (n == 1) return 1; // Base case for n=1
    return n * factorial(n - 1);
}
print("Factorial of 5: " + factorial(5)); // Expected: Factorial of 5: 120

// Nested scopes with functions and variables
print("\nSection 4.1: Nested Scopes & Closures (conceptual)");
let outerVar = "I'm outside";
fun outerFunc() {
    let innerVar = "I'm inside outerFunc";
    fun innerFunc() {
        print("From innerFunc: " + outerVar); // Should capture outerVar
        print("From innerFunc: " + innerVar);
    }
    innerFunc();
}
outerFunc();
// print(innerVar); // This would be a runtime error (undefined)

// --- Section 5: Error Handling (Try/Catch) ---
print("\nSection 5: Error Handling");

// Test: Division by Zero
try {
    print("Attempting division by zero...");
    let zero_divisor = 0;
    let result = 10 / zero_divisor; // This will throw an error
    print("This line should not be reached: " + result);
} catch (err_msg) {
    print("Caught error 1: " + err_msg); // Expected: Caught error 1: Division by zero.
}

// Test: Undefined Variable
try {
    print("Attempting to access undefined variable...");
    print(undefined_variable); // This will throw an error
} catch (err_msg) {
    print("Caught error 2: " + err_msg); // Expected: Caught error 2: Undefined variable 'undefined_variable'.
}

// Test: Type Mismatch
try {
    print("Attempting type mismatch operation...");
    print("hello" - 123); // This will throw an error
} catch (err_msg) {
    print("Caught error 3: " + err_msg); // Expected: Caught error 3: Operands must be numbers.
}

// Test: Function call with wrong arity
try {
    print("Attempting function call with wrong arguments...");
    add(1); // add expects 2 arguments
} catch (err_msg) {
    print("Caught error 4: " + err_msg); // Expected: Caught error 4: Expected 2 arguments but got 1.
}

// Test: Nested try/catch (simple)
try {
    print("Outer try block.");
    try {
        print("Inner try block.");
        let x = 1 / 0;
    } catch (inner_err) {
        print("Caught inner error: " + inner_err);
    }
    print("After inner try/catch.");
} catch (outer_err) {
    print("Caught outer error: " + outer_err); // This should not be reached
}

// --- Section 6: Comments ---
print("\nSection 6: Comments");
// This is a single-line comment
/* This is a
   multi-line comment
   It should be ignored by the lexer */
let commented_var = 123; // Inline comment
print("Commented variable: " + commented_var); // Expected: Commented variable: 123

print("\n--- All tests completed ---");