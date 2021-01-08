from base import Component, Memory, DoubleComponent
from instructions import instructions_by_opcode, instructions_by_text, NO_OPERATION


class Z80():

    MEMORY_SIZE = 256 * 256

    def __init__(self):
        self.memory = Memory(self.MEMORY_SIZE)
        self._define_registers()
        self.instructions_by_opcode = instructions_by_opcode
        self.instructions_by_text = instructions_by_text

    def _define_registers(self):
        self.program_counter_low = Component("PCL")
        self.program_counter_high = Component("PCH")
        self.program_counter = DoubleComponent("PC", self.program_counter_low, self.program_counter_high)

        self.stack_pointer_low = Component("SPL")
        self.stack_pointer_high = Component("SPH")
        self.stack_pointer = DoubleComponent("SP", self.stack_pointer_low, self.stack_pointer_high)

        self.A = Component("A")
        self.B = Component("B")
        self.C = Component("C")
        self.D = Component("D")
        self.E = Component("E")
        self.F = Component("F")
        self.H = Component("H")
        self.L = Component("L")
        self.I = Component("I")
        self.R = Component("R")
        self.IXH = Component("IXH")
        self.IXL = Component("IXL")
        self.IYH = Component("IYH")
        self.IYL = Component("IYL")

        self.A_ALT = Component("A'")
        self.B_ALT = Component("B'")
        self.C_ALT = Component("C'")
        self.D_ALT = Component("D'")
        self.E_ALT = Component("E'")
        self.F_ALT = Component("F'")
        self.H_ALT = Component("H'")
        self.L_ALT = Component("L'")

        self.AF = DoubleComponent("AF", self.F, self.A)
        self.BC = DoubleComponent("BC", self.C, self.B)
        self.DE = DoubleComponent("DE", self.E, self.D)
        self.HL = DoubleComponent("HL", self.L, self.H)
        self.IX = DoubleComponent("IX", self.IXL, self.IXH)
        self.IY = DoubleComponent("IY", self.IYL, self.IYH)

        self.AF_ALT = DoubleComponent("AF'", self.F_ALT, self.A_ALT)
        self.BC_ALT = DoubleComponent("BC'", self.C_ALT, self.B_ALT)
        self.DE_ALT = DoubleComponent("DE'", self.E_ALT, self.D_ALT)
        self.HL_ALT = DoubleComponent("HL'", self.L_ALT, self.H_ALT)

        self.registers = [
            self.program_counter,
            self.stack_pointer,
            self.A,
            self.B,
            self.C,
            self.D,
            self.E,
            self.F,
            self.H,
            self.L,
            self.I,
            self.R,
            self.IXH,
            self.IXL,
            self.IYH,
            self.IYL,
            self.AF,
            self.BC,
            self.DE,
            self.HL,
            self.IX,
            self.IY,
            self.A_ALT,
            self.B_ALT,
            self.C_ALT,
            self.D_ALT,
            self.E_ALT,
            self.F_ALT,
            self.AF_ALT,
            self.BC_ALT,
            self.DE_ALT,
            self.HL_ALT,
        ]

        self.registers_by_name = {reg.name: reg for reg in self.registers}

    def read_memory_and_increment_pc(self):
        memory_contents = self.memory.get_contents_value(self.program_counter.get_contents())
        if self.program_counter.get_contents() < self.MEMORY_SIZE - 1:
            self.program_counter.add_to_contents(1)
            end_of_memory_reached = False
        else:
            end_of_memory_reached = True
        return memory_contents, end_of_memory_reached

    def run(self):
        end_of_memory_reached = False
        while not end_of_memory_reached:
            opcode, end_of_memory_reached = self.read_memory_and_increment_pc()
            if str(opcode) not in self.instructions_by_opcode:
                raise Exception("Opcode {} not recognised!!!".format(opcode))
            instruction = self.instructions_by_opcode[str(opcode)]
            self.execute_instruction(instruction)
        
    def execute_instruction(self, instruction):
        if instruction.instruction_base == NO_OPERATION:
            return
        substituted_left_arg = self.substitute_arg(instruction.left_arg)
        substituted_right_arg = self.substitute_right_arg(instruction.right_arg)

    def substitute_arg(self, arg):
        if not arg:
            return None
        if arg.upper() in self.registers_by_name:
            return self.registers_by_name[arg.upper()]
        if "(" in arg:
            arg = arg[1:-1]
            if arg.upper() in self.registers_by_name:
                return self.memory.get_contents(self.registers_by_name[arg.upper()].get_contents())
            if "**" in arg:
                high_byte, end_of_memory_reached = self.read_memory_and_increment_pc()
                if end_of_memory_reached:
                    raise Exception("Out of memory!!!")
                low_byte, _ = self.read_memory_and_increment_pc()
                address = self.convert_high_and_low_bytes_to_address(high_byte, low_byte)
                return self.memory.get_contents(address)
            raise Exception("Invalid arg {}".format(arg))
        if arg == "*":
            value, _ = self.read_memory_and_increment_pc()
            return value
        elif arg == "**":
            high_byte, end_of_memory_reached = self.read_memory_and_increment_pc()
            if end_of_memory_reached:
                raise Exception("Out of memory!!!")
            low_byte, _ = self.read_memory_and_increment_pc()
            return self.convert_high_and_low_bytes_to_address(high_byte, low_byte)
        raise Exception("Invalid arg {}".format(arg))

    def convert_high_and_low_bytes_to_address(self, high_byte, low_byte):
        return high_byte * 256 + low_byte

    def substitute_right_arg(self, arg):
        if arg == None:
            return arg
        substituted_arg = self.substitute_arg(arg)
        if not isinstance(substituted_arg, int):
            substituted_arg = substituted_arg.get_contents()
        return substituted_arg
