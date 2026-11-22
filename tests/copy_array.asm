mem[512] = 12
mem[513] = 42
mem[514] = 9
mem[700] = 512

mem[701] = 600
mem[702] = mem[mem[700] + 0]
mem[mem[701]] = mem[702]

mem[701] = 601
mem[702] = mem[mem[700] + 1]
mem[mem[701]] = mem[702]

mem[701] = 602
mem[702] = mem[mem[700] + 2]
mem[mem[701]] = mem[702]
