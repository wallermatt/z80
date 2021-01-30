SIGN_FLAG = "S"
ZERO_FLAG = "Z"
HALF_CARRY_FLAG = "H"
PARITY_OVERFLOW_FLAG = "P/V"
ADD_SUBTRACT_FLAG = "N"
CARRY_FLAG = "C"

FLAG_POSITIONS = {
    SIGN_FLAG: 7,
    ZERO_FLAG: 6,
    HALF_CARRY_FLAG: 4,
    PARITY_OVERFLOW_FLAG: 2,
    ADD_SUBTRACT_FLAG: 1,
    CARRY_FLAG: 0,
}



class Component:

    SIZE = 1
    MAX_VALUE = 256

    def __init__(self, name):
        self.name = name
        self.contents = 0

    def get_name(self):
        return self.name

    def get_contents(self):
        return self.contents

    def set_contents(self, value):
        self.contents = value

    def add_to_contents(self, value):
        carry_flag = 0
        result = self.contents + value
        if result >= self.MAX_VALUE:
            result = result % self.MAX_VALUE
            carry_flag = 1
        self.contents = result
        return carry_flag

    def subtract_from_contents(self, value):
        carry_flag = 0
        if self.contents >= value:
            self.contents -= value
        else:
            self.contents = self.contents - value + self.MAX_VALUE
            carry_flag = 1
        return carry_flag

    def convert_contents_to_bit_list(self):
        return [int(x) for x in '{:08b}'.format(input)]

    def convert_bit_list_to_contents(self, bit_list):
        self.contents = 0
        for bit in bit_list:
            self.contents = (self.contents << 1) | bit



class DoubleComponent(Component):

    SIZE = 2

    def __init__(self, name, low_component, high_component):
        self.name = name
        self.low = low_component
        self.high = high_component

    def get_contents(self):
        return self.high.get_contents() * self.MAX_VALUE + self.low.get_contents()

    def set_contents_value(self, value):
        low_value = value % self.MAX_VALUE
        high_value = value // self.MAX_VALUE
        self.low.set_contents(low_value)
        self.high.set_contents(high_value)

    def set_contents(self, low_value, high_value=0):
        self.low.set_contents(low_value)
        self.high.set_contents(high_value) 

    def add_to_contents(self, value):
        low_value = value % self.MAX_VALUE
        high_value = value // self.MAX_VALUE
        carry_flag = self.low.add_to_contents(low_value)
        if carry_flag == 1:
            high_value += 1
        carry_flag = self.high.add_to_contents(high_value)
        return carry_flag

    def subtract_from_contents(self, value):
        low_value = value % self.MAX_VALUE
        high_value = value // self.MAX_VALUE
        carry_flag = self.low.subtract_from_contents(low_value)
        if carry_flag == 1:
            high_value += 1
        carry_flag = self.high.subtract_from_contents(high_value)
        return carry_flag


class Memory:

    def __init__(self, size):
        self.contents = [Component("address: {}".format(e)) for e in range(size)]

    def get_contents(self, address):
        if address >= len(self.contents):
             raise Exception("Memory address out of range!!! address: {}, memory size: {}".format(address, self.contents))
        return self.contents[address]

    def get_contents_value(self, address):
        return self.contents[address].get_contents()

    def set_contents_value(self, address, value):
        self.contents[address].set_contents(value)

    def dump(self):
        return [e.get_contents() for e in self.contents]

    def load(self, data):
        for address,value in enumerate(data):
            self.contents[address].set_contents(value)



class InstructionBase:

    def __init__(self, name, opcode, memory, program_counter=None, components=None, stack_pointer=None):
        self.name = name
        self.opcode = opcode
        self.memory = memory
        self.program_counter = program_counter
        self.components = components
        self.stack_pointer = stack_pointer

    def get_memory_location_contents_and_inc_pc(self):
        pc_value = self.program_counter.get_contents()
        contents = self.memory.get_contents_value(pc_value)
        self.program_counter.set_contents(pc_value + 1)
        return contents

    def run(self):
        pass
