SIGN_FLAG = "S"
ZERO_FLAG = "Z"
HALF_CARRY_FLAG = "H"
PARITY_OVERFLOW_FLAG = "P/V"
ADD_SUBTRACT_FLAG = "N"
CARRY_FLAG = "C"


class Component:

    SIZE = 1
    MAX_VALUE = 256
    MAX_NIBBLE_VALUE = 16

    FLAG_POSITIONS = {
        SIGN_FLAG: 7,
        ZERO_FLAG: 6,
        HALF_CARRY_FLAG: 4,
        PARITY_OVERFLOW_FLAG: 2,
        ADD_SUBTRACT_FLAG: 1,
        CARRY_FLAG: 0,
    }

    def __init__(self, name):
        self.name = name
        self.contents = 0
        self.potential_flags = {}

    def get_name(self):
        return self.name

    def get_contents(self):
        return self.contents

    def set_contents(self, value):
        self.contents = value

    def add_to_contents(self, value):
        self.contents += value
        self.contents = self.contents % self.MAX_VALUE

    def set_potential_flags(self):
        if self.get_contents() >= 128:
            self.potential_flags[SIGN_FLAG] = True
        else:
            self.potential_flags[SIGN_FLAG] = False

        if self.get_contents() == 0:
            self.potential_flags[ZERO_FLAG] = True
        else:
            self.potential_flags[ZERO_FLAG] = False

    def addition_with_flags(self, value):
        result = self.get_contents() + value
        overflow_result = result % self.MAX_VALUE

        left_nibble = self.get_contents() % self.MAX_NIBBLE_VALUE
        value_nibble = value % self.MAX_NIBBLE_VALUE
        result_nibble = (left_nibble + value_nibble) % self.MAX_NIBBLE_VALUE

        self.set_contents(overflow_result)
 
        self.potential_flags[ADD_SUBTRACT_FLAG] = False
        self.potential_flags[CARRY_FLAG] = overflow_result != result
        self.potential_flags[HALF_CARRY_FLAG] = left_nibble > result_nibble
        if (self.get_contents() // 128 == value // 128) and (self.get_contents() // 128 != overflow_result // 128):
            self.potential_flags[PARITY_OVERFLOW_FLAG] = True
        else:
            self.potential_flags[PARITY_OVERFLOW_FLAG] = False
        
    def subtraction_with_flags(self, value, set_flags=True):
        result = self.get_contents() - value
        if result < 0:
            overflow_result = self.MAX_VALUE + result
        else:
            overflow_result = result

        left_nibble = self.get_contents() % self.MAX_NIBBLE_VALUE
        right_nibble = value % self.MAX_NIBBLE_VALUE
        nibble_result = left_nibble - right_nibble
        if nibble_result < 0:
            nibble_overflow = True
        else:
            nibble_overflow = False

        self.potential_flags[ADD_SUBTRACT_FLAG] = True
        self.potential_flags[CARRY_FLAG] = overflow_result != result
        self.potential_flags[HALF_CARRY_FLAG] = nibble_overflow

        if self.get_contents() // 128 != value // 128:
            self.potential_flags[PARITY_OVERFLOW_FLAG] = True
        else:
            self.potential_flags[PARITY_OVERFLOW_FLAG] = False

        self.set_contents(overflow_result)

    def convert_contents_to_bit_list(self):
        bit_list = [int(x) for x in '{:08b}'.format(self.contents)]
        bit_list.reverse()
        return bit_list

    def convert_bit_list_to_contents(self, bit_list):
        self.contents = 0
        bit_list.reverse()
        for i, bit in enumerate(bit_list):
            self.contents = (self.contents << 1) | bit

    def get_flag(self, flag):
        flag_position = self.FLAG_POSITIONS[flag]
        bit_list = self.convert_contents_to_bit_list()
        return bit_list[flag_position]
        
    def set_flag(self, flag):
        flag_position = self.FLAG_POSITIONS[flag]
        bit_list = self.convert_contents_to_bit_list()
        bit_list[flag_position] = 1
        self.convert_bit_list_to_contents(bit_list)

    def reset_flag(self, flag):
        flag_position = self.FLAG_POSITIONS[flag]
        bit_list = self.convert_contents_to_bit_list()
        bit_list[flag_position] = 0
        self.convert_bit_list_to_contents(bit_list)


class DoubleComponent(Component):

    SIZE = 2
    MAX_VALUE = 65536
    MAX_NIBBLE_VALUE = 4096


    def __init__(self, name, low_component, high_component):
        self.name = name
        self.low = low_component
        self.high = high_component
        self.potential_flags = {}

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
        result = self.get_contents() + value
        self.set_contents_value(result % self.MAX_VALUE)


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
