
def main():
    fnum = int(input("Enter first number: "))
    snum = int(input("Enter second number: "))
    operation = input("Enter operation +, -, * or /: ")

    match operation:
        case "+":
            print(fnum + snum)
        case "-":
            print(fnum - snum)
        case "*":
            print(fnum * snum)
        case "/":
            if snum != 0:
                print(fnum / snum)
            else:
                print("Error: Division by zero")
        case _:
            print("Error: Invalid operation")


if __name__ == "__main__":
    main()
