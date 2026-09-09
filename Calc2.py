class SimpleParser:
    def __init__(self, text):
        self.text = text.replace(" ", "")
        self.pos = 0

    def parse(self):
        result = self.plus_minus()
        if self.pos < len(self.text):
            raise ValueError
        return result

    def plus_minus(self):
        value = self.multiple_divide()
        while self.pos < len(self.text) and self.text[self.pos] in ('+', '-'):
            operation = self.text[self.pos]
            self.pos += 1
            if operation == '+':
                value += self.multiple_divide()
            else:
                value -= self.multiple_divide()
        return value

    def multiple_divide(self):
        value = self.factor()
        while self.pos < len(self.text) and self.text[self.pos] in ('*', '/'):
            operation = self.text[self.pos]
            self.pos += 1
            if operation == '*':
                value *= self.factor()
            else:
                denom = self.factor()
                if denom == 0:
                    raise ZeroDivisionError
                value /= denom
        return value

    def factor(self):
        if self.pos >= len(self.text):
            raise ValueError

        if self.text[self.pos] == '-':
            self.pos += 1
            return -self.factor()

        if self.text[self.pos] == '(':
            self.pos += 1
            value = self.plus_minus()
            if self.pos >= len(self.text) or self.text[self.pos] != ')':
                raise ValueError
            self.pos += 1
            return value

        start = self.pos
        while self.pos < len(self.text) and (self.text[self.pos].isdigit() or self.text[self.pos] == '.'):
            self.pos += 1

        num_str = self.text[start:self.pos]
        if not num_str or num_str.count('.') > 1:
            raise ValueError

        return float(num_str) if '.' in num_str else int(num_str)


def main():
    user_input = input("Enter expression: ").strip()
    
    try:
        parser = SimpleParser(user_input)
        result = parser.parse()
            
        print(result)
    except Exception:
        print("Error")


if __name__ == "__main__":
    main()