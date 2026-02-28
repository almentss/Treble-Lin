// test_script.tl
//45-48
// --- Section 1: Basic Declarations and Arithmetic ---
let a = 10;
let b = 5;
let c = a + b * 2; // 10 + 10 = 20
print("%s", "Section 1:\n");
print("%d\n", a); // Expected: 10
print("%d\n", b); // Expected: 5
print("%d\n", c); // Expected: 20
print("%d\n", c / 2); // Expected: 10

let str1 = "Hello, ";
let str2 = "Treble Lin!";
print("%s", str1 + str2); // Expected: Hello, Treble Lin!
print("%s", true and false); // Expected: false
print("%s", true or false);  // Expected: true
print("%s", not true);       // Expected: false

// --- Section 2: Conditional Statements (if/else) ---
print("%s", "\nSection 2:");
let temp = 25;
if (temp > 20) {
    print("%s", "It's warm!"); // Expected: It's warm!
} else {
    print("%s", "It's cool!");
}

if (temp < 15) {
    print("%s", "It's cold!");
} else if (temp >= 20 and temp < 30) {
    print("%s", "It's pleasant."); // Expected: It's pleasant.
} else {
    print("%s", "Extreme weather!");
}

// --- Section 3: Loops (while, for, break, continue) ---
print("%s", "\nSection 3:");
let i = 0;
while (i < 3) {
    print("While loop count: %d\n", i); // Expected: 0, 1, 2
    i = i + 1;
}

for (let j = 0; j < 3; j = j + 1) {
    print("For loop count: %d\n", j); // Expected: 0, 1, 2
}

let k = 0;
print("%s", "Break/Continue Test:\n");
while (k < 10) {
    k = k + 1;
    if (k == 3) continue; // Skip 3
    if (k == 5) break;    // Exit at 5
    print("k: %d\n", k); // Expected: k: 1, k: 2, k: 4
}

// --- Section 4: Functions ---
print("%s", "\nSection 4:\n");

fun add(x, y) {
    return x + y;
}

fun multiply(a, b) {
    return a * b;
}

fun greet(name) {
    print("Greetings, %s!\n", name);
}

let sum_result = add(7, 3);
print("Sum: %d\n", sum_result); // Expected: Sum: 10

let prod_result = multiply(4, 5);
print("Product: %d\n", prod_result); // Expected: Product: 20

greet("Alice"); // Expected: Greetings, Alice!

fun do_nothing() {
    print("%s", "Doing nothing...");
}
let nothing_val = do_nothing(); // Expected: Doing nothing...

fun factorial(n) {
    if (n == 0) return 1;
    if (n == 1) return 1;
    return n * factorial(n - 1);
}
print("Factorial of 5: %d\n", factorial(5)); // Expected: Factorial of 5: 120

// Nested scopes with functions and variables
print("%s", "\nSection 4.1: Nested Scopes & Closures (conceptual)\n");
let outerVar = "I'm outside";
fun outerFunc() {
    let innerVar = "I'm inside outerFunc";
    fun innerFunc() {
        print("From innerFunc: %s\n", outerVar);
        print("From innerFunc: %s\n", innerVar);
    }
    innerFunc();
}
outerFunc();
// print(innerVar); // This would be a runtime error (undefined)

// --- Section 5: Error Handling (Try/Catch) ---
print("%s", "\nSection 5: Error Handling\n");

try {
    print("%s", "Attempting division by zero...\n");
    let zero_divisor = 0;
    let result = 10 / zero_divisor;
    print("This line should not be reached: %d\n", result);
} catch (err_msg) {
    print("Caught error 1: %s\n", err_msg);
}

/*
try {
    print("%s", "Attempting to access undefined variable...\n");
    print("%s", undefined_variable);
} catch (err_msg) {
    print("Caught error 2: %s\n", err_msg);
}
*/

try {
    print("%s", "Attempting type mismatch operation...\n");
    print("%s", "hello" - 123);
} catch (err_msg) {
    print("Caught error 3: %s\n", err_msg);
}

try {
    print("%s", "Attempting function call with wrong arguments...\n");
    add(1);
} catch (err_msg) {
    print("Caught error 4: %s\n", err_msg);
}

try {
    print("%s", "Outer try block.\n");
    try {
        print("%s", "Inner try block.\n");
        let x = 1 / 0;
    } catch (inner_err) {
        print("Caught inner error: %s\n", inner_err);
    }
    print("%s", "After inner try/catch.\n");
} catch (outer_err) {
    print("Caught outer error: %s\n", outer_err);
}

// --- Section 6: Comments ---
print("%s", "\nSection 6: Comments\n");
// This is a single-line comment
/* This is a
   multi-line comment
   It should be ignored by the lexer */
let commented_var = 123; // Inline comment
print("Commented variable: %d\n", commented_var); // Expected: Commented variable: 123

print("%s", "\n--- All tests completed ---\n");
