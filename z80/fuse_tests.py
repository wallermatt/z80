from helper import Z80TestHandler
from instructions import instructions_by_opcode
from base import FLAG_POSITIONS

in_order = ["name", "registers", "states", "memory", "-1"]

REGISTERS = [
    "AF",
    "BC",
    "DE",
    "HL", 
    "AF'",
    "BC'", 
    "DE'", 
    "HL'",
    "IX",
    "IY",
    "SP",
    "PC"
]


class State:
    def __init__(self, name, registers='', states='', memory=''):
        self.name = name
        self.registers = registers
        self.states = states
        if not memory:
            self.memory = []
        else:
            self.memory = memory
        self.test_registers = {}
        self.test_memory = {}
        self.test_ports = {}
        self.instruction_text = ''

    def __str__(self):
        return 'name: {}\n registers: {}\n states: {}\n memory: {}\n'.format(self.name, self.registers, self.states, self.memory)

    def load_test_registers(self):
        for i, e in enumerate(self.registers.split(' ')):
            high = int(e[:2], 16)
            low = int(e[2:], 16)
            self.test_registers[REGISTERS[i]] = high * 256 + low

    def load_test_memory(self):
        for m in self.memory:
            print(m)
            m = m.split(' ')
            high = int(m[0][:2], 16)
            low = int(m[0][2:], 16)
            start = high * 256 + low
            print(start, m[1:])
            for e in m[1:]:
                if e == '-1':
                    break
                self.test_memory[start] = int(e, 16)
                start += 1

        

before = {}
after = {}

with open('./tests.in', 'r') as f:
    next_row = 0
    for i, l in enumerate(f):
        if l == '\n':
            continue
        l = str(l).replace('\n', '')
        if in_order[next_row] == 'name':
            new_test = State(l)
            next_row += 1
        elif in_order[next_row] == 'registers':
            new_test.registers = l
            next_row += 1
        elif in_order[next_row] == 'states':
            new_test.states = l
            next_row += 1
        elif in_order[next_row] == 'memory':
            if l == '-1':
                before[new_test.name] = new_test
                next_row = 0
                continue
            new_test.memory.append(l)
    print(len(before))

with open('./tests.expected', 'r') as f:
    next_row = 0
    for i, l in enumerate(f):
        if l[0] == ' ':
            continue
        if in_order[next_row] == 'name':
            l = str(l).replace('\n', '')
            new_test = State(l)
            next_row += 1
        elif in_order[next_row] == 'registers':
            l = str(l).replace('\n', '')
            new_test.registers = l
            next_row += 1
        elif in_order[next_row] == 'states':
            l = str(l).replace('\n', '')
            new_test.states = l
            next_row += 1
        elif in_order[next_row] == 'memory':
            if l in ['\n', '-1']:
                after[new_test.name] = new_test
                next_row = 0
                continue
            l = str(l).replace('\n', '')
            new_test.memory.append(l)
    print(len(before))


    def create_z80_registers(before, after):
        registers = {}
        for r in before:
            registers[r] = (before[r], after[r])
        return registers

    def create_z80_memory(before, after):
        memory = {}
        for m in before:
            if m in after:
                v = after[m]
            else:
                v = before[m]
            memory[m] = (before[m], v)

        for m in after:
            if m not in before:
                memory[m] = (0, after[m])
        return memory

    def get_opcode_and_instruction(registers, memory):
        #import pdb; pdb.set_trace()
        #opcode = hex(memory[registers['PC'][0]][0])
        #opcode = str(opcode)[2:]
        opcode = str(memory[registers['PC'][0]][0])
        if opcode == "203":
            opcode = "CB" + str(memory[registers['PC'][0] + 1][0])
        return opcode, (instructions_by_opcode[opcode]).text

    def get_flags(f_value):
        flags = {}
        bit_list = [int(x) for x in '{:08b}'.format(f_value)]
        #print(bit_list)
        for flag in FLAG_POSITIONS:
            flags[flag] = bit_list[7 - FLAG_POSITIONS[flag]]
        return flags


def run_test(before, after, test):
    b = before[test]
    b.load_test_registers()
    b.load_test_memory()

    a = after[test]
    a.load_test_registers()
    a.load_test_memory()

    registers = create_z80_registers(b.test_registers, a.test_registers)
    print(registers)

    memory = create_z80_memory(b.test_memory, a.test_memory)
    print(memory)

    print(get_opcode_and_instruction(registers, memory))

    for v in registers['AF']:
        low = v % 256
        print(get_flags(low))

    print(get_flags(120))

    Z80TestHandler(registers, {}, memory, {}, '', False, True)


TEST = 'cb40'
if TEST:
    run_test(before, after, TEST)
else:
    for test in before:
        if test in ['120']:
            continue
        print('TEST: {}'.format(test))
        run_test(before, after, test)

'''
    b = before[TEST]
    #print(b.registers)
    b.load_test_registers()
    #print(b.test_registers)

    #print(b.memory)
    b.load_test_memory()
    #print(b.test_memory)

    a = after[TEST]
    #print(a.registers)
    a.load_test_registers()
    #print(a.test_registers)

    #print(a.memory)
    a.load_test_memory()
    #print(a.test_memory)

    registers = create_z80_registers(b.test_registers, a.test_registers)
    print(registers)

    memory = create_z80_memory(b.test_memory, a.test_memory)
    print(memory)

    print(get_opcode_and_instruction(registers, memory))

    for v in registers['AF']:
        low = v % 256
        print(get_flags(low))

    print(get_flags(66))

    Z80TestHandler(registers, {}, memory, {}, '', False, True)

    
    b = before['00']
    print(b.registers)
    b.load_test_registers()
    print(b.test_registers)

    print(b.memory)
    b.load_test_memory()
    print(b.test_memory)

    a = after['00']
    print(a.registers)
    a.load_test_registers()
    print(a.test_registers)

    print(a.memory)
    a.load_test_memory()
    print(a.test_memory)
    
    
    for e in after:
        print(e)
        print(after[e])
'''



        

#for l in tests_in.line():
 #   print(l)

# split into tests

# split up individual test

# assign values to my helper.