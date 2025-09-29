# TODO:
# Create a function called calculate that takes three arguments:
# - A number
# - An operator ("+", "-", "*", or "/")
# - Another number
# The function should return the result of the calculation

# Insert your function code here
def calculate(number, operator, number2):
    if operator == "+":
        return number + number2
    elif operator == "-":
        return number - number2
    elif operator == "*":
        return number * number2
    elif operator == "/":
        return number / number2

    
# Test the function with different operations
print(calculate(10, "+", 10))  # should return 20
print(calculate(10, "-", 10))  # should return 0
print(calculate(10, "*", 10))  # should return 100
print(calculate(10, "/", 10))  # should return 1.0