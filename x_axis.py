for i in range(256):
    column = i // 8
    remainder = i % 8
    power = 7 - remainder
    value = 2 ** power
    print(i, column, value)