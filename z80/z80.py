from base import (
    Component, Memory, DoubleComponent, SIGN_FLAG, ZERO_FLAG, HALF_CARRY_FLAG, PARITY_OVERFLOW_FLAG, ADD_SUBTRACT_FLAG, CARRY_FLAG,
)
from instructions import (
    instructions_by_opcode, instructions_by_text, NO_OPERATION, SPECIAL_ARGS, LOAD,
    EXCHANGE, EXCHANGE_MULTI, ADD, INSTRUCTION_FLAG_POSITIONS
)


class Z80():

    MEMORY_SIZE = 256 * 256

    def __init__(self):
        self.memory = Memory(self.MEMORY_SIZE)
        self._define_registers()
        self.instructions_by_opcode = instructions_by_opcode
        self.instructions_by_text = instructions_by_text

    def _define_registers(self):
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

        self.program_counter_low = Component("PCL")
        self.program_counter_high = Component("PCH")
        self.program_counter = DoubleComponent("PC", self.program_counter_low, self.program_counter_high)

        self.stack_pointer_low = Component("SPL")
        self.stack_pointer_high = Component("SPH")
        self.stack_pointer = DoubleComponent("SP", self.stack_pointer_low, self.stack_pointer_high)

        self.flag_register = self.F

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
        substituted_left_arg = self.substitute_arg(instruction.left_arg, instruction.right_arg)
        substituted_right_arg = self.substitute_right_arg(instruction.right_arg, instruction.left_arg)
        self.execute_instruction_base(instruction, substituted_left_arg, substituted_right_arg)

    def execute_instruction_base(self, instruction, substituted_left_arg, substituted_right_arg):
        if instruction.instruction_base == LOAD:
            self.load_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == EXCHANGE_MULTI:
            self.exchange_execute(self.registers_by_name["BC"], self.registers_by_name["BC'"])
            self.exchange_execute(self.registers_by_name["DE"], self.registers_by_name["DE'"])
            self.exchange_execute(self.registers_by_name["HL"], self.registers_by_name["HL'"])
        elif instruction.instruction_base == EXCHANGE:
            substituted_right_arg = self.substitute_arg(instruction.right_arg, instruction.left_arg)
            self.exchange_execute(substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == ADD:
            self.add_execute(instruction, substituted_left_arg, substituted_right_arg)

    def load_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        if not isinstance(substituted_left_arg, tuple):
            substituted_left_arg.set_contents(substituted_right_arg)
        elif len(substituted_left_arg) == 2:
            low, high = self.convert_value_to_low_and_high_bytes(substituted_right_arg)
            substituted_left_arg[0].set_contents(low)
            substituted_left_arg[1].set_contents(high)
        else:
            raise Exception("Left arg subsititution has too many components")

    def exchange_execute(self, substituted_left_arg, substituted_right_arg):
        if not isinstance(substituted_left_arg, tuple):
            temp_substituted_left_arg_contents = substituted_left_arg.get_contents()
            substituted_left_arg.set_contents(substituted_right_arg.get_contents())
        elif len(substituted_left_arg) == 2:
            low = substituted_left_arg[0].get_contents()
            high = substituted_left_arg[1].get_contents()
            temp_substituted_left_arg_contents = self.convert_low_and_high_bytes_to_value(low, high)
            low, high = self.convert_value_to_low_and_high_bytes(substituted_right_arg.get_contents())
            substituted_left_arg[0].set_contents(low)
            substituted_left_arg[1].set_contents(high)
        else:
            raise Exception("Left arg subsititution has too many components")
        substituted_right_arg.set_contents(temp_substituted_left_arg_contents)

    def load_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        result, carry_flag, half_carry_flag = substituted_left_arg.addition_with_flags(
            substituted_left_arg.get_contents(),
            substituted_right_arg
        )

    def add_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        substituted_left_arg.addition_with_flags(substituted_right_arg)
        substituted_left_arg.test_set_potential_flags()
        self.set_flags_if_required(instruction, substituted_left_arg.potential_flags)

    def substitute_arg(self, arg, opposite_arg):
        if not arg or arg in SPECIAL_ARGS:
            return arg
        if arg.upper() in self.registers_by_name:
            return self.registers_by_name[arg.upper()]
        if "(" in arg:
            arg = arg[1:-1]
            if arg == "c":   # in/out (c) specifies port
                return self.registers_by_name["C"].get_contents()
            if arg.upper() in self.registers_by_name:
                address = self.registers_by_name[arg.upper()].get_contents()
                if not opposite_arg or opposite_arg == "*" or self.registers_by_name[opposite_arg.upper()].SIZE == 1:
                    return self.memory.get_contents(address)
                return (self.memory.get_contents(address), self.memory.get_contents(address + 1))
            else:
                if arg == "ix+*":
                    ix_value = self.registers_by_name["IX"].get_contents()
                    displacement, _ = self.read_memory_and_increment_pc()
                    return self.memory.get_contents(ix_value + displacement)
            if "**" in arg:
                low_byte, end_of_memory_reached = self.read_memory_and_increment_pc()
                if end_of_memory_reached:
                    raise Exception("Out of memory!!!")
                high_byte, _ = self.read_memory_and_increment_pc()
                address = self.convert_low_and_high_bytes_to_value(low_byte, high_byte)
                if not opposite_arg or self.registers_by_name[opposite_arg.upper()].SIZE == 1:
                    return self.memory.get_contents(address)
                return (self.memory.get_contents(address), self.memory.get_contents(address + 1))

            raise Exception("Invalid arg {}".format(arg))

        if arg == "*":
            value, _ = self.read_memory_and_increment_pc()
            return value
        elif arg == "**":
            low_byte, end_of_memory_reached = self.read_memory_and_increment_pc()
            if end_of_memory_reached:
                raise Exception("Out of memory!!!")
            high_byte, _ = self.read_memory_and_increment_pc()
            return self.convert_low_and_high_bytes_to_value(low_byte, high_byte)
        raise Exception("Invalid arg {}".format(arg))

    def convert_low_and_high_bytes_to_value(self, low_byte, high_byte):
        return high_byte * 256 + low_byte

    def convert_value_to_low_and_high_bytes(self, value):
        high = value // 256
        low = value % 256
        return low, high

    def substitute_right_arg(self, arg, opposite_arg=None):
        if not arg or arg in SPECIAL_ARGS:
            return arg
        substituted_arg = self.substitute_arg(arg, opposite_arg)
        if not isinstance(substituted_arg, int):
            if not isinstance(substituted_arg, tuple):
                substituted_arg = substituted_arg.get_contents()
            elif len(substituted_arg) == 2:
                substituted_arg = self.convert_low_and_high_bytes_to_value(
                    substituted_arg[0].get_contents(),
                    substituted_arg[1].get_contents(),
                )
            else:
                raise Exception("Right arg subsititution has too many components")
        return substituted_arg

    def set_flags_if_required(self, instruction, potential_flags):
        for i, action in enumerate(instruction.flags):
            if action in ["-", " "]:
                continue
            flag = INSTRUCTION_FLAG_POSITIONS[i]
            if action in ["+", "V", "P", "*"]:
                set_flag = potential_flags[flag]
                if set_flag:
                    self.flag_register.set_flag(flag)
                else:
                    self.flag_register.reset_flag(flag)
            elif action == "0":
                self.flag_register.reset_flag(flag)
            elif action == "1":
                self.flag_register.set_flag(flag)
        potential_flags = {}

'''

*-P*++
-1  * 
-10+++
-1-1--
00P0++
10-0--
-0*0++
+0-0--
-0 1+ 
00P1++
-000--
+0P0++
-0*0--
-0P0++
++-+--
-+V+++
++V+++
-1*+++
------
-1  1 
*0-*--

var flags = ['C', 'N', 'P/V', 'H', 'Z', 'S'];

          for (i = 0; i < 6; i++) {
            desc += '<br><b>' + flags[i] + ':</b> ';

            switch (val[0].charAt(i)) {
              case '-':
                desc += 'unaffected';
                break;
              case '+':
                desc += 'affected as defined';
                break;
              case 'P':
                desc += 'detects parity';
                break;
              case 'V':
                desc += 'detects overflow';
                break;
              case '1':
                desc += 'set';
                break;
              case '0':
                desc += 'reset';
                break;
              case '*':
                desc += 'exceptional';
                break;
              default:
                desc += 'unknown';
            }
          }
'''