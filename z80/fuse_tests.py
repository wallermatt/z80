from helper import Z80TestHandler
from instructions import instructions_by_opcode
from base import FLAG_POSITIONS

in_order = ["name", "registers", "states", "memory", "-1"]

REGISTERS_16_BIT = [
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

REGISTERS_8_BIT = [
    "I",
    "R"
]


class State:
    def __init__(self, name, registers='', states='', memory='', ports=''):
        self.name = name
        self.registers = registers
        self.states = states
        if not memory:
            self.memory = []
        else:
            self.memory = memory
        if not ports:
            self.ports = {}
        else:
            self.ports = ports
        self.test_registers = {}
        self.test_memory = {}
        self.test_ports = {}
        self.instruction_text = ''

    def __str__(self):
        return 'name: {}\n registers: {}\n states: {}\n memory: {}\n ports: {}\n'.format(self.name, self.registers, self.states, self.memory, self.ports)

    def load_test_registers(self):
        self.registers = ' '.join(self.registers.split())
        for i, e in enumerate(self.registers.split(' ')):
            if i < len(REGISTERS_16_BIT):
                high = int(e[:2], 16)
                low = int(e[2:], 16)
                self.test_registers[REGISTERS_16_BIT[i]] = high * 256 + low
            else:
                self.test_registers[REGISTERS_8_BIT[i - len(REGISTERS_16_BIT)]] = int(e, 16)

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
            new_test.registers = new_test.registers + ' ' + l[:5]
            new_test.IFF1 = int(l[6])
            new_test.IFF2 = int(l[8])
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
            if 'PR ' in l:
                pr = l.split('PR ')[1][:4]
                if 'PR' not in new_test.ports:
                    new_test.ports['PR'] = [pr]
                else:
                    new_test.ports['PR'] = new_test.ports['PR'] + [pr]
            elif 'PW ' in l:
                pw = l.split('PW ')[1][:4]
                if 'PW' not in new_test.ports:
                    new_test.ports['PW'] = [pw]
                else:
                    new_test.ports['PW'] = new_test.ports['PW'] + [pw]           
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
            new_test.registers = new_test.registers + ' ' + l[:5]
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

    def create_z80_ports(before, after):
        ports = {}
        for pr in before:
            v, p = int(pr[:2], 16), int(pr[2:], 16)
            ports[p] = [v, v]
        for pw in after:
            v, p = int(pw[:2], 16), int(pw[2:], 16)
            if p in ports:
                ports[p][1] = v
            else:
                ports[p] = [0, v]
        return ports


    def get_opcode_and_instruction(registers, memory):
        #import pdb; pdb.set_trace()
        #opcode = hex(memory[registers['PC'][0]][0])
        #opcode = str(opcode)[2:]
        opcode = str(memory[registers['PC'][0]][0])
        if opcode == "203":
            opcode = "CB" + str(memory[registers['PC'][0] + 1][0])
        elif opcode == "221":
            opcode = "DD" + str(memory[registers['PC'][0] + 1][0])
        if opcode in instructions_by_opcode:
            opcode, (instructions_by_opcode[opcode]).text
        return opcode, "not found"

    def get_flags(f_value):
        flags = {}
        bit_list = [int(x) for x in '{:08b}'.format(f_value)]
        #print(bit_list)
        for flag in FLAG_POSITIONS:
            flags[flag] = bit_list[7 - FLAG_POSITIONS[flag]]
        return flags


def run_test(before, after, test, ignore_flags=False):
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

    if 'PR' in a.ports:
        bp = a.ports['PR']
    else:
        bp = []

    if 'PW' in a.ports:
        ap = a.ports['PW']
    else:
        ap = []

    ports = create_z80_ports(bp, ap)
    print(ports)

    for v in registers['AF']:
        low = v % 256
        print(get_flags(low))

    print(get_flags(205))

    Z80TestHandler(registers, {}, memory, ports, '', False, True, b.IFF1, b.IFF2, ignore_flags)


#TEST = 'ddcb80'
TEST = ''

START = 'edbb'
start_reached = False
if TEST:
    run_test(before, after, TEST)
else:
    for test in before:
        if test == START:
            start_reached = True
        if not start_reached:
            continue
        if test in [
            '27', 'db_1', 'db_2', 'db_3', 'db', 'eda2', 'eda2_01', 'eda2_02', 'eda2_03',
            'eda3', 'eda3_01', 'eda3_02', 'eda3_03', 'eda3_04', 'eda3_05', 'eda3_06', 'eda3_07', 'eda3_08', 'eda3_09', 'eda3_10', 'eda3_11',
            'edaa', 'edaa_01', 'edaa_02', 'edaa_03', 'edab',
            'edab_01', 'edab_02', 'edb0', 'edb1', 'edb2', 'edb3', 'edb8', 'edb9', 'edba'
        ]:
            continue
        if test in ['edbb']:
            ignore_flags = True
        else:
            ignore_flags = False
        print('TEST: {}'.format(test))
        run_test(before, after, test, ignore_flags)

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