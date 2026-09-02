
def func(num, count):
    for i in range(count):
        print(num + 1)
        num += 1

def main():
    Inum = int(input("Enter a number: "))
    Icount = int(input("Enter how many times to print: "))
    func(Inum, Icount)

if __name__ == "__main__":
    main()