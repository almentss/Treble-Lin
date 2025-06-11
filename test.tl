fun GCD(x, y) {
    if(x%y==0){
        return y;
    }
    return GCD(y,x%y);
}

fun multiply(a, b) {
    return a * b;
}

fun greet(name) {
    print("Greetings, %s!", name);
}

let ans = GCD(18, 12);
print("Sum: %d", ans); // Expected: Sum: 10