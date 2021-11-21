# load test.in

in_order = ["name", "registers", "states", "memory", "-1"]
class FuseTest:
    def __init__(self, name, registers='', states='', memory=''):
        self.name = name
        self.registers = registers
        self.states = states
        if not memory:
            self.memory = []
        else:
            self.memory = memory

    def __str__(self):
        return 'name: {}\n registers: {}\n states: {}\n memory: {}\n'.format(self.name, self.registers, self.states, self.memory)

tests = {}

with open('./tests.in', 'r') as f:
    #tests_in = f.read()
    next_row = 0
    for i, l in enumerate(f):
        if l == '\n':
            continue
        l = str(l).replace('\n', '')
        if in_order[next_row] == 'name':
            new_test = FuseTest(l)
            next_row += 1
        elif in_order[next_row] == 'registers':
            new_test.registers = l
            next_row += 1
        elif in_order[next_row] == 'states':
            new_test.states = l
            next_row += 1
        elif in_order[next_row] == 'memory':
            if l == '-1':
                tests[new_test.name] = new_test
                next_row = 0
                print(new_test.name)
                continue
            new_test.memory.append(l)
    print(len(tests))
    print(tests['00'])




        

#for l in tests_in.line():
 #   print(l)

# split into tests

# split up individual test

# assign values to my helper.