def encode_load(a,b,c,d=0):
    if a == 30:
        f = a | (b | (c | d << 24) << 24) << 5
    else:
        f = a | (b | c << 24) << 5
    size = 0
    if '5' in str(a):
        size = 7
    elif a == 6:
        size = 6
    elif a == 30:
        size = 9
    data = f.to_bytes(size,"little")
    return data
if __name__ == "__main__":
    print(encode_load(6, 545, 215).hex(' '))
    print(encode_load(5, 276, 37).hex(' '))
    print(encode_load(15, 263, 283).hex(' '))
    print(encode_load(30, 711, 690, 26).hex(' '))
