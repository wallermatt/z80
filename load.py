



x = open("/home/matthew/games/be.sna", "rb").read()

print(x[5])

memory_list = []
for i in x:
    memory_list.append(int(i))

print(memory_list[16401])