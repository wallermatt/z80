from types import DynamicClassAttribute
from base import (
    Component, Memory, DoubleComponent, SIGN_FLAG, ZERO_FLAG, HALF_CARRY_FLAG, PARITY_OVERFLOW_FLAG, ADD_SUBTRACT_FLAG, CARRY_FLAG, PARITY
)
from instructions import (
    CONVERT_CARRY_FLAG, instructions_by_opcode, instructions_by_text, NO_OPERATION, SPECIAL_ARGS, LOAD,
    EXCHANGE, EXCHANGE_MULTI, ADD, INSTRUCTION_FLAG_POSITIONS, SUB, ADC, SBC, INC, DEC,
    PUSH, POP, JUMP, JUMP_RELATIVE, JUMP_INSTRUCTIONS, DEC_JUMP_RELATIVE, CALL, COMPARE,
    COMPARE_INC, COMPARE_INC_REPEAT, COMPARE_DEC, COMPARE_DEC_REPEAT, COMPLEMENT, NEGATION,
    LOAD_INC, LOAD_DEC, LOAD_INC_REPEAT, LOAD_DEC_REPEAT, AND, OR, XOR, DAA, RETURN, BIT, IN,
    OUT, OUT_INC, OUT_INC_REPEAT, OUT_DEC, OUT_DEC_REPEAT, IN_INC, IN_INC_REPEAT, IN_DEC, 
    IN_DEC_REPEAT, ROT_LEFT, ROT_LEFT_ACC, ROT_LEFT_C, ROT_LEFT_C_ACC, ROT_LEFT_DEC, ROT_RIGHT,
    ROT_RIGHT_ACC, ROT_RIGHT_C, ROT_RIGHT_C_ACC, ROT_RIGHT_DEC, SHIFT_LEFT_A, SHIFT_LEFT_L, 
    SHIFT_RIGHT_A, SHIFT_RIGHT_L, CONVERT_CARRY_FLAG, SET_CARRY_FLAG, RESTART, RESET, SET, DDCB
)


class Z80():

    MEMORY_SIZE = 256 * 256

    def __init__(self, memory_size=MEMORY_SIZE):
        self.memory = Memory(memory_size)
        self.ports = Memory(256)
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

    def run(self, code_end=-1):
        end_of_memory_reached = False
        while not end_of_memory_reached:
            opcode, end_of_memory_reached = self.read_memory_and_increment_pc()
            if opcode == 203:
                opcode2, end_of_memory_reached = self.read_memory_and_increment_pc()
                opcode = "CB" + str(opcode2)
            elif opcode == 221:
                opcode2, end_of_memory_reached = self.read_memory_and_increment_pc()
                if opcode2 == 203:
                    opcode = "DDCB" 
                elif "DD" + str(opcode2) not in self.instructions_by_opcode:
                    opcode = opcode2
                else:
                    opcode = "DD" + str(opcode2)
            if str(opcode) not in self.instructions_by_opcode:
                raise Exception("Opcode {} not recognised!!!".format(opcode))
            instruction = self.instructions_by_opcode[str(opcode)]
            self.execute_instruction(instruction)
            if code_end > -1:
                if self.program_counter.get_contents() >= code_end:
                    return
        
    def execute_instruction(self, instruction):
        if instruction.instruction_base == NO_OPERATION:
            pass
        if instruction.instruction_base == DDCB:
            extra_opcode = self.memory.get_contents_value(self.program_counter.get_contents() + 1)
            instruction = self.instructions_by_opcode[DDCB + str(extra_opcode)]
            substituted_left_arg = self.substitute_arg(instruction.left_arg, instruction.right_arg)
            substituted_right_arg = self.substitute_right_arg(instruction.right_arg, instruction.left_arg, DDCB)
        elif instruction.instruction_base in JUMP_INSTRUCTIONS:
            left_arg = instruction.left_arg
            right_arg = instruction.right_arg
            left_arg = left_arg.replace("(", "")
            left_arg = left_arg.replace(")", "")
            if  left_arg == "c":
                 left_arg = "cf"
            if right_arg:
                right_arg = right_arg.replace("(", "")
                right_arg = right_arg.replace(")", "")
            else:
                right_arg = left_arg
                left_arg = None
            substituted_left_arg = self.substitute_arg(left_arg, right_arg)
            substituted_right_arg = self.substitute_right_arg(right_arg, left_arg)
        elif instruction.instruction_base == RESTART:
            substituted_left_arg = int(instruction.left_arg.replace("h", ""), 16)
            substituted_right_arg = None
        else:
            if instruction.instruction_base in [ROT_RIGHT_C_ACC, ROT_LEFT_ACC, ROT_LEFT_C_ACC, ROT_RIGHT_ACC, ROT_RIGHT_DEC]:
                substituted_left_arg = self.A
                substituted_right_arg = None
            else:
                substituted_left_arg = self.substitute_arg(instruction.left_arg, instruction.right_arg)
                substituted_right_arg = self.substitute_right_arg(instruction.right_arg, instruction.left_arg)
        self.execute_instruction_base(instruction, substituted_left_arg, substituted_right_arg)
        self.undocumented_behaviour(instruction, substituted_left_arg, substituted_right_arg)

    def execute_instruction_base(self, instruction, substituted_left_arg, substituted_right_arg):
        if instruction.instruction_base == NO_OPERATION:
            return
        elif instruction.instruction_base == LOAD:
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
        elif instruction.instruction_base == SUB:
            self.sub_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == ADC:
            substituted_right_arg += self.flag_register.get_flag(CARRY_FLAG)
            self.add_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == SBC:
            substituted_right_arg += self.flag_register.get_flag(CARRY_FLAG)
            self.sub_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == INC:
            self.add_execute(instruction, substituted_left_arg, 1)
        elif instruction.instruction_base == DEC:
            self.sub_execute(instruction, substituted_left_arg, 1)
        elif instruction.instruction_base == PUSH:
            self.push_execute(instruction, substituted_left_arg)
        elif instruction.instruction_base == POP:
            self.pop_execute(instruction, substituted_left_arg)
        elif instruction.instruction_base == JUMP:
            self.jump_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == JUMP_RELATIVE:
            self.jump_relative_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == DEC_JUMP_RELATIVE:
            self.dec_jump_relative_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == CALL:
            self.call_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == RETURN:
            self.return_execute(instruction, substituted_left_arg)
        elif instruction.instruction_base == COMPARE:
            self.compare_execute(instruction, substituted_left_arg)
        elif instruction.instruction_base == COMPARE_INC:
            self.compare_inc_execute(instruction)
        elif instruction.instruction_base == COMPARE_INC_REPEAT:
            self.compare_inc_repeat_execute(instruction)
        elif instruction.instruction_base == COMPARE_DEC:
            self.compare_dec_execute(instruction)
        elif instruction.instruction_base == COMPARE_DEC_REPEAT:
            self.compare_dec_repeat_execute(instruction)
        elif instruction.instruction_base == COMPLEMENT:
            self.complement_execute(instruction)
        elif instruction.instruction_base == NEGATION:
            self.negation_execute(instruction)
        elif instruction.instruction_base == LOAD_INC:
            self.load_inc_execute(instruction)
        elif instruction.instruction_base == LOAD_DEC:
            self.load_dec_execute(instruction)
        elif instruction.instruction_base == LOAD_INC_REPEAT:
            self.load_inc_repeat_execute(instruction)
        elif instruction.instruction_base == LOAD_DEC_REPEAT:
            self.load_dec_repeat_execute(instruction)
        elif instruction.instruction_base == AND:
            self.and_execute(instruction, substituted_left_arg)
        elif instruction.instruction_base == OR:
            self.or_execute(instruction, substituted_left_arg)
        elif instruction.instruction_base == XOR:
            self.xor_execute(instruction, substituted_left_arg)
        elif instruction.instruction_base == DAA:
            self.daa_execute(instruction)
        elif instruction.instruction_base == BIT:
            self.bit_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == IN:
            self.in_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == IN_INC:
            self.in_inc_execute(instruction)
        elif instruction.instruction_base == IN_INC_REPEAT:
            self.in_inc_repeat_execute(instruction)
        elif instruction.instruction_base == IN_DEC:
            self.in_dec_execute(instruction)
        elif instruction.instruction_base == IN_DEC_REPEAT:
            self.in_dec_repeat_execute(instruction)
        elif instruction.instruction_base == OUT:
            self.out_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == OUT_INC:
            self.out_inc_execute(instruction)
        elif instruction.instruction_base == OUT_INC_REPEAT:
            self.out_inc_repeat_execute(instruction)
        elif instruction.instruction_base == OUT_DEC:
            self.out_dec_execute(instruction)
        elif instruction.instruction_base == OUT_DEC_REPEAT:
            self.out_dec_repeat_execute(instruction)
        elif instruction.instruction_base == ROT_LEFT:
            self.rot_left_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == ROT_LEFT_ACC:
            self.rot_left_execute(instruction, self.A)
        elif instruction.instruction_base == ROT_LEFT_C:
            self.rot_left_c_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == ROT_LEFT_C_ACC:
            self.rot_left_c_execute(instruction, self.A)
        elif instruction.instruction_base == ROT_LEFT_DEC:
            self.rot_left_dec_execute(instruction)
        elif instruction.instruction_base == ROT_RIGHT:
            self.rot_right_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == ROT_RIGHT_ACC:
            self.rot_right_execute(instruction, self.A)
        elif instruction.instruction_base == ROT_RIGHT_C:
            self.rot_right_c_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == ROT_RIGHT_C_ACC:
            self.rot_right_c_execute(instruction, substituted_left_arg)
        elif instruction.instruction_base == ROT_RIGHT_DEC:
            self.rot_right_dec_execute(instruction)
        elif instruction.instruction_base == SHIFT_LEFT_A:
            self.shift_left_a_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == SHIFT_LEFT_L:
            self.shift_left_l_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == SHIFT_RIGHT_A:
            self.shift_right_a_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == SHIFT_RIGHT_L:
            self.shift_right_l_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == CONVERT_CARRY_FLAG:
            self.convert_carry_flag_execute(instruction)
        elif instruction.instruction_base == SET_CARRY_FLAG:
            self.set_carry_flag_execute(instruction)
        elif instruction.instruction_base == RESTART:
            self.restart_execute(instruction, substituted_left_arg)
        elif instruction.instruction_base == RESET:
            self.reset_execute(instruction, substituted_left_arg, substituted_right_arg)
        elif instruction.instruction_base == SET:
            self.set_execute(instruction, substituted_left_arg, substituted_right_arg)

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

    def add_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        substituted_left_arg.addition_with_flags(substituted_right_arg)
        substituted_left_arg.set_potential_flags()
        self.set_flags_if_required(instruction, substituted_left_arg.potential_flags)

    def sub_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        substituted_left_arg.subtraction_with_flags(substituted_right_arg)
        substituted_left_arg.set_potential_flags(instruction=instruction)
        self.set_flags_if_required(instruction, substituted_left_arg.potential_flags)

    def push_execute(self, instruction, substituted_left_arg):
        self.stack_pointer.subtraction_with_flags(1)
        self.memory.set_contents_value(
            self.stack_pointer.get_contents(),
            substituted_left_arg.high.get_contents()
        )
        self.stack_pointer.subtraction_with_flags(1)
        self.memory.set_contents_value(
            self.stack_pointer.get_contents(),
            substituted_left_arg.low.get_contents()
        )

    def pop_execute(self, instruction, substituted_left_arg):
        low_value = self.memory.get_contents_value(self.stack_pointer.get_contents())
        substituted_left_arg.low.set_contents(low_value)
        self.stack_pointer.addition_with_flags(1)
        high_value = self.memory.get_contents_value(self.stack_pointer.get_contents())
        substituted_left_arg.high.set_contents(high_value)
        self.stack_pointer.addition_with_flags(1)

    def check_flag_arg(self, flag_arg):
        if flag_arg == "z":
            if not self.flag_register.get_flag(ZERO_FLAG):
                return False
        elif flag_arg == "nz":
            if self.flag_register.get_flag(ZERO_FLAG):
                return False
        elif flag_arg == "cf":
            if not self.flag_register.get_flag(CARRY_FLAG):
                return False
        elif flag_arg == "nc":
            if self.flag_register.get_flag(CARRY_FLAG):
                return False
        elif flag_arg == "po":
            if not self.flag_register.get_flag(PARITY_OVERFLOW_FLAG):
                return False
        elif flag_arg == "pe":
            if self.flag_register.get_flag(PARITY_OVERFLOW_FLAG):
                return False
        elif flag_arg == "p":
            if self.flag_register.get_flag(SIGN_FLAG):
                return False
        elif flag_arg == "m":
            if not self.flag_register.get_flag(SIGN_FLAG):
                return False
        return True

    def jump_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        if substituted_left_arg and not self.check_flag_arg(substituted_left_arg):
            return
        self.program_counter.set_contents_value(substituted_right_arg)

    def jump_relative_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        if substituted_left_arg and not self.check_flag_arg(substituted_left_arg):
            return
        displacement = self.twos_complement(substituted_right_arg)
        if displacement > 0:
            self.program_counter.add_to_contents(displacement)
        else:
            self.program_counter.subtract_from_contents(displacement * -1)
            
    def dec_jump_relative_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        self.registers_by_name["B"].subtraction_with_flags(1)
        if self.registers_by_name["B"].get_contents() == 0:
            return
        displacement = self.twos_complement(substituted_right_arg)
        if displacement > 0:
            self.program_counter.add_to_contents(displacement)
        else:
            self.program_counter.subtract_from_contents(displacement * -1)

    def call_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        if substituted_left_arg and not self.check_flag_arg(substituted_left_arg):
            return
        self.push_execute(instruction, self.program_counter)
        self.program_counter.set_contents_value(substituted_right_arg)

    def return_execute(self, instruction, substituted_left_arg):
        if substituted_left_arg and not self.check_flag_arg(substituted_left_arg):
            return
        self.pop_execute(instruction, self.program_counter)

    def compare_execute(self, instruction, substituted_left_arg):
        a = self.registers_by_name["A"]
        a_original_contents = a.get_contents()
        a.subtraction_with_flags(substituted_left_arg.get_contents())
        a.set_potential_flags()
        self.set_flags_if_required(instruction, a.potential_flags)
        a.set_contents(a_original_contents)

    def compare_inc_execute(self, instruction):
        hl = self.registers_by_name["HL"]
        memory_loc = self.memory.get_contents(hl.get_contents())
        self.compare_execute(instruction, memory_loc)
        hl.add_to_contents(1)
        self.registers_by_name["BC"].subtract_from_contents(1)

    def compare_inc_repeat_execute(self, instruction):
        bc = self.registers_by_name["BC"]
        self.compare_inc_execute(instruction)
        while not self.flag_register.get_flag(ZERO_FLAG) and bc.get_contents() != 0:
            self.compare_inc_execute(instruction)

    def compare_dec_execute(self, instruction):
        hl = self.registers_by_name["HL"]
        memory_loc = self.memory.get_contents(hl.get_contents())
        self.compare_execute(instruction, memory_loc)
        hl.subtract_from_contents(1)
        self.registers_by_name["BC"].subtract_from_contents(1)

    def compare_dec_repeat_execute(self, instruction):
        bc = self.registers_by_name["BC"]
        self.compare_dec_execute(instruction)
        while not self.flag_register.get_flag(ZERO_FLAG) and bc.get_contents() != 0:
            self.compare_dec_execute(instruction)

    def complement_execute(self, instruction):
        a = self.registers_by_name["A"]
        a.set_contents(a.MAX_VALUE - 1 - a.get_contents())
        self.set_flags_if_required(instruction, {})

    def negation_execute(self, instruction):
        a = self.registers_by_name["A"]
        a_value = a.get_contents()
        a.set_contents(0)
        a.subtraction_with_flags(a_value)
        a.set_potential_flags()
        self.set_flags_if_required(instruction, a.potential_flags)

    def load_inc_execute(self, instruction):
        memory_value = self.memory.get_contents_value(self.HL.get_contents())
        self.memory.set_contents_value(self.DE.get_contents(), memory_value)
        self.HL.add_to_contents(1)
        self.DE.add_to_contents(1)
        self.BC.subtract_from_contents(1)
        self.set_flags_if_required(instruction, {})

    def load_dec_execute(self, instruction):
        memory_value = self.memory.get_contents_value(self.HL.get_contents())
        self.memory.set_contents_value(self.DE.get_contents(), memory_value)
        self.HL.subtract_from_contents(1)
        self.DE.subtract_from_contents(1)
        self.BC.subtract_from_contents(1)
        self.set_flags_if_required(instruction, {})

    def load_inc_repeat_execute(self, instruction):
        while self.BC.get_contents() != 0:
            self.load_inc_execute(instruction)

    def load_dec_repeat_execute(self, instruction):
        while self.BC.get_contents() != 0:
            self.load_dec_execute(instruction)

    def and_execute(self, instruction, substituted_left_arg):
        if type(substituted_left_arg) is not int:
            substituted_left_arg = substituted_left_arg.get_contents()
        self.A.set_contents(self.A.get_contents() & substituted_left_arg)
        self.A.set_potential_flags()
        self.set_flags_if_required(instruction, self.A.potential_flags)

    def or_execute(self, instruction, substituted_left_arg):
        if type(substituted_left_arg) is not int:
            substituted_left_arg = substituted_left_arg.get_contents()
        self.A.set_contents(self.A.get_contents() | substituted_left_arg)
        self.A.set_potential_flags()
        self.set_flags_if_required(instruction, self.A.potential_flags)

    def xor_execute(self, instruction, substituted_left_arg):
        if type(substituted_left_arg) is not int:
            substituted_left_arg = substituted_left_arg.get_contents()
        self.A.set_contents(self.A.get_contents() ^ substituted_left_arg)
        self.A.set_potential_flags()
        self.set_flags_if_required(instruction, self.A.potential_flags)

    def daa_execute(self, instruction):
        if not self.F.get_flag(ADD_SUBTRACT_FLAG):
            if self.F.get_flag(HALF_CARRY_FLAG) or (self.A.get_contents() & 15) > 9:
                self.A.addition_with_flags(6)
            if self.F.get_flag(CARRY_FLAG) or self.A.get_contents() > 99:
                self.A.addition_with_flags(96)
                self.F.set_flag(CARRY_FLAG)
            else:
                self.F.reset_flag(CARRY_FLAG)
        else:
            if self.F.get_flag(HALF_CARRY_FLAG) or (self.A.get_contents() & 15) > 9:
                self.A.subtraction_with_flags(6)
            if self.F.get_flag(CARRY_FLAG) or self.A.get_contents() > 99:
                self.A.subtraction_with_flags(96)
                self.F.set_flag(CARRY_FLAG)
            else:
                self.F.reset_flag(CARRY_FLAG)
        if self.F.get_flag(ADD_SUBTRACT_FLAG) and not self.F.get_flag(HALF_CARRY_FLAG):
            self.F.potential_flags[HALF_CARRY_FLAG] = False
        elif self.F.get_flag(ADD_SUBTRACT_FLAG) and self.F.get_flag(HALF_CARRY_FLAG):
            if self.A.get_contents() & 15 < 6:
                self.F.potential_flags[HALF_CARRY_FLAG] = True
            else:
                self.F.potential_flags[HALF_CARRY_FLAG] = False
        else:
            if self.A.get_contents() & 15 >= 10:
                self.F.potential_flags[HALF_CARRY_FLAG] = True
            else:
                self.F.potential_flags[HALF_CARRY_FLAG] = False
        self.A.set_potential_flags()
        self.set_flags_if_required(instruction, self.A.potential_flags)

    def bit_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        potential_flags = {}
        if (2 ** substituted_left_arg) & substituted_right_arg.get_contents():
            potential_flags[ZERO_FLAG] = 0
        else:
            potential_flags[ZERO_FLAG] = 1
        self.set_flags_if_required(instruction, potential_flags)

    def in_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        if type(substituted_left_arg) is not int:
            value = self.ports.get_contents_value(substituted_right_arg)
        else:
            value = self.ports.get_contents_value(substituted_left_arg)
            substituted_left_arg = Component("temp")
        substituted_left_arg.set_contents(value)
        substituted_left_arg.set_potential_flags()
        self.set_flags_if_required(instruction, substituted_left_arg.potential_flags)

    def in_inc_execute(self, instruction):
        in_value = self.ports.get_contents_value(self.C.get_contents())
        self.B.subtraction_with_flags(1, False)
        self.memory.set_contents_value(self.HL.get_contents(), in_value)
        self.HL.add_to_contents(1)
        self.set_flags_if_required(instruction, None)

    def in_inc_repeat_execute(self, instruction):
        while self.B.get_contents() != 0:
            self.in_inc_execute(instruction) 

    def in_dec_execute(self, instruction):
        in_value = self.ports.get_contents_value(self.C.get_contents())
        self.B.subtraction_with_flags(1, False)
        self.memory.set_contents_value(self.HL.get_contents(), in_value)
        self.HL.subtraction_with_flags(1, False)
        self.set_flags_if_required(instruction, None)

    def in_dec_repeat_execute(self, instruction):
        while self.B.get_contents() != 0:
            self.in_dec_execute(instruction) 

    def out_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        self.ports.set_contents_value(substituted_left_arg, substituted_right_arg)

    def out_inc_execute(self, instruction):
        out_value = self.memory.get_contents_value(self.HL.get_contents())
        self.B.subtraction_with_flags(1, False)
        self.ports.set_contents_value(self.C.get_contents(), out_value)
        self.HL.add_to_contents(1)
        self.set_flags_if_required(instruction, None)

    def out_inc_repeat_execute(self, instruction):
        while self.B.get_contents() != 0:
            self.out_inc_execute(instruction) 

    def out_dec_execute(self, instruction):
        out_value = self.memory.get_contents_value(self.HL.get_contents())
        self.B.subtraction_with_flags(1, False)
        self.ports.set_contents_value(self.C.get_contents(), out_value)
        self.HL.subtraction_with_flags(1, False)
        self.set_flags_if_required(instruction, None)

    def out_dec_repeat_execute(self, instruction):
        while self.B.get_contents() != 0:
            self.out_dec_execute(instruction) 

    def rot_left_execute(self, instruction, substituted_left_arg, substituted_right_arg=None):
        bl = substituted_left_arg.convert_contents_to_bit_list()
        c_flag = self.flag_register.get_flag(CARRY_FLAG)
        c_value = bl[0]
        rot_bl = bl[1:] + [c_flag]
        substituted_left_arg.convert_bit_list_to_contents(rot_bl)
        substituted_left_arg.set_potential_flags()
        substituted_left_arg.potential_flags[CARRY_FLAG] = c_value
        self.set_flags_if_required(instruction, substituted_left_arg.potential_flags)
        if substituted_right_arg:
            substituted_right_arg.set_contents(substituted_left_arg.get_contents())

    def rot_left_c_execute(self, instruction, substituted_left_arg, substituted_right_arg=None):
        bl = substituted_left_arg.convert_contents_to_bit_list()
        c_value = bl[0]
        rot_bl = bl[1:] + [bl[0]]
        substituted_left_arg.convert_bit_list_to_contents(rot_bl)
        substituted_left_arg.set_potential_flags()
        substituted_left_arg.potential_flags[CARRY_FLAG] = c_value
        self.set_flags_if_required(instruction, substituted_left_arg.potential_flags)
        if substituted_right_arg:
            substituted_right_arg.set_contents(substituted_left_arg.get_contents())

    def rot_left_dec_execute(self, instruction):
        mem_loc = self.memory.get_contents(self.HL.get_contents())
        mem_bl = mem_loc.convert_contents_to_bit_list()
        a_bl = self.A.convert_contents_to_bit_list()
        mem_bl_hi = list(mem_bl[:4])
        mem_bl = mem_bl[4:] + a_bl[4:]
        a_bl = a_bl[:4] + mem_bl_hi
        mem_loc.convert_bit_list_to_contents(mem_bl)
        self.A.convert_bit_list_to_contents(a_bl)
        self.A.set_potential_flags()
        self.set_flags_if_required(instruction, self.A.potential_flags)

    def rot_right_execute(self, instruction, substituted_left_arg, substituted_right_arg=None):
        bl = substituted_left_arg.convert_contents_to_bit_list()
        c_flag = self.flag_register.get_flag(CARRY_FLAG)
        c_value = bl[7]
        rot_bl = [c_flag] + bl[:7]
        substituted_left_arg.convert_bit_list_to_contents(rot_bl)
        substituted_left_arg.set_potential_flags()
        substituted_left_arg.potential_flags[CARRY_FLAG] = c_value
        self.set_flags_if_required(instruction, substituted_left_arg.potential_flags)
        if substituted_right_arg:
            substituted_right_arg.set_contents(substituted_left_arg.get_contents())

    def rot_right_c_execute(self, instruction, substituted_left_arg, substituted_right_arg=None):
        bl = substituted_left_arg.convert_contents_to_bit_list()
        c_value = bl[7]
        rot_bl = [c_value] + bl[:7]
        substituted_left_arg.convert_bit_list_to_contents(rot_bl)
        substituted_left_arg.set_potential_flags()
        substituted_left_arg.potential_flags[CARRY_FLAG] = c_value
        self.set_flags_if_required(instruction, substituted_left_arg.potential_flags)
        if substituted_right_arg:
            substituted_right_arg.set_contents(substituted_left_arg.get_contents())

    def rot_right_dec_execute(self, instruction):
        mem_loc = self.memory.get_contents(self.HL.get_contents())
        mem_bl = mem_loc.convert_contents_to_bit_list()
        a_bl = self.A.convert_contents_to_bit_list()
        mem_bl_low = list(mem_bl[4:])
        mem_bl = a_bl[4:] + mem_bl[:4]
        a_bl = a_bl[:4] + mem_bl_low
        mem_loc.convert_bit_list_to_contents(mem_bl)
        self.A.convert_bit_list_to_contents(a_bl)
        self.A.set_potential_flags()
        self.set_flags_if_required(instruction, self.A.potential_flags)

    def shift_left_a_execute(self, instruction, substituted_left_arg, substituted_right_arg=None):
        new_c, bl  = substituted_left_arg.split_bit_list_at_bit_pos(6)
        substituted_left_arg.convert_bit_list_to_contents(bl + [0])
        substituted_left_arg.set_potential_flags()
        substituted_left_arg.potential_flags[CARRY_FLAG] = new_c[0]
        if substituted_left_arg.parity():
            substituted_left_arg.potential_flags[PARITY_OVERFLOW_FLAG] = True
        else:
             substituted_left_arg.potential_flags[PARITY_OVERFLOW_FLAG] = False
        self.set_flags_if_required(instruction, substituted_left_arg.potential_flags)
        if substituted_right_arg:
            substituted_right_arg.set_contents(substituted_left_arg.get_contents())

    def shift_left_l_execute(self, instruction, substituted_left_arg, substituted_right_arg=None):
        new_c, bl  = substituted_left_arg.split_bit_list_at_bit_pos(6)
        substituted_left_arg.convert_bit_list_to_contents(bl + [1])
        substituted_left_arg.set_potential_flags()
        substituted_left_arg.potential_flags[CARRY_FLAG] = new_c[0]
        if substituted_left_arg.parity():
            substituted_left_arg.potential_flags[PARITY_OVERFLOW_FLAG] = True
        else:
             substituted_left_arg.potential_flags[PARITY_OVERFLOW_FLAG] = False
        self.set_flags_if_required(instruction, substituted_left_arg.potential_flags)
        if substituted_right_arg:
            substituted_right_arg.set_contents(substituted_left_arg.get_contents())

    def shift_right_a_execute(self, instruction, substituted_left_arg, substituted_right_arg=None):
        bl, new_c  = substituted_left_arg.split_bit_list_at_bit_pos(0)
        substituted_left_arg.convert_bit_list_to_contents([bl[0]] + bl)
        substituted_left_arg.set_potential_flags()
        substituted_left_arg.potential_flags[CARRY_FLAG] = new_c[0]
        if substituted_left_arg.parity():
            substituted_left_arg.potential_flags[PARITY_OVERFLOW_FLAG] = True
        else:
             substituted_left_arg.potential_flags[PARITY_OVERFLOW_FLAG] = False
        self.set_flags_if_required(instruction, substituted_left_arg.potential_flags)
        if substituted_right_arg:
            substituted_right_arg.set_contents(substituted_left_arg.get_contents())

    def shift_right_l_execute(self, instruction, substituted_left_arg, substituted_right_arg=None):
        bl, new_c  = substituted_left_arg.split_bit_list_at_bit_pos(0)
        substituted_left_arg.convert_bit_list_to_contents([0] + bl)
        substituted_left_arg.set_potential_flags()
        substituted_left_arg.potential_flags[CARRY_FLAG] = new_c[0]
        if substituted_left_arg.parity():
            substituted_left_arg.potential_flags[PARITY_OVERFLOW_FLAG] = True
        else:
             substituted_left_arg.potential_flags[PARITY_OVERFLOW_FLAG] = False
        self.set_flags_if_required(instruction, substituted_left_arg.potential_flags)
        if substituted_right_arg:
            substituted_right_arg.set_contents(substituted_left_arg.get_contents())

    def convert_carry_flag_execute(self, instruction):
        if self.flag_register.get_flag(CARRY_FLAG):
            potential_flags = {CARRY_FLAG: False}
        else:
            potential_flags = {CARRY_FLAG: True}
        self.set_flags_if_required(instruction, potential_flags)

    def set_carry_flag_execute(self, instruction):
        self.set_flags_if_required(instruction, None)

    def restart_execute(self, instruction, substituted_left_arg):
        self.push_execute(instruction, self.program_counter)
        self.program_counter.set_contents_value(substituted_left_arg)

    def reset_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        bit_list = substituted_right_arg.convert_contents_to_bit_list()
        bit_list[7 - substituted_left_arg] = 0
        substituted_right_arg.convert_bit_list_to_contents(bit_list)
        args = instruction.text.split(",")
        if len(args) == 3:
            third_arg = self.registers_by_name[args[2].capitalize()]
            third_arg.set_contents(substituted_right_arg.get_contents())

    def set_execute(self, instruction, substituted_left_arg, substituted_right_arg):
        bit_list = substituted_right_arg.convert_contents_to_bit_list()
        bit_list[7 - substituted_left_arg] = 1
        substituted_right_arg.convert_bit_list_to_contents(bit_list)

    def substitute_arg(self, arg, opposite_arg, special=False):
        if special == DDCB:
            if not opposite_arg.isdigit():
                _, _ = self.read_memory_and_increment_pc()
        if arg and arg.isdigit():
            return int(arg)
        if not arg or arg in SPECIAL_ARGS:
            return arg
        if arg.upper() in self.registers_by_name:
            return self.registers_by_name[arg.upper()]
        if "(" in arg:
            arg = arg[1:-1]
            if arg == "c":   # in/out (c) specifies port
                return self.registers_by_name["C"].get_contents()
            if arg == "*":   # in/out (*) specifies port
                return self.read_memory_and_increment_pc()[0]
            if arg.upper() in self.registers_by_name:
                address = self.registers_by_name[arg.upper()].get_contents()
                # bit n, (hl) check
                if opposite_arg and isinstance(opposite_arg, str) and opposite_arg.isdigit():
                    return self.memory.get_contents(address)
                if not opposite_arg or opposite_arg == "*" or self.registers_by_name[opposite_arg.upper()].SIZE == 1:
                    return self.memory.get_contents(address)
                return (self.memory.get_contents(address), self.memory.get_contents(address + 1))
            else:
                if arg == "ix+*":
                    ix_value = self.registers_by_name["IX"].get_contents()
                    displacement, _ = self.read_memory_and_increment_pc()
                    displacement = self.twos_complement(displacement)
                    substituted_arg = self.memory.get_contents(ix_value + displacement)
                    if special == DDCB:
                        if opposite_arg.isdigit():
                            _, _ = self.read_memory_and_increment_pc()
                    return substituted_arg
                elif arg == "iy+*":
                    iy_value = self.registers_by_name["IY"].get_contents()
                    displacement, _ = self.read_memory_and_increment_pc()
                    displacement = self.twos_complement(displacement)
                    return self.memory.get_contents(iy_value + displacement)
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

    def substitute_right_arg(self, arg, opposite_arg=None, special=False):
        if not arg or arg in SPECIAL_ARGS:
            if special == DDCB:
                _, _ = self.read_memory_and_increment_pc()
            return arg
        substituted_arg = self.substitute_arg(arg, opposite_arg, special)
        # res 0, r  bit 0, r etc
        if isinstance(opposite_arg, str) and opposite_arg.isdigit():
            return substituted_arg
        if not isinstance(substituted_arg, int):
            if not isinstance(substituted_arg, tuple):
                if special == DDCB:
                    return substituted_arg
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
            flag = INSTRUCTION_FLAG_POSITIONS[i]   # pos 7 at lhs
            if action in ["+", "V"]:
                set_flag = potential_flags[flag]
                if set_flag:
                    self.flag_register.set_flag(flag)
                else:
                    self.flag_register.reset_flag(flag)
            elif action == "P":
                if instruction.instruction_base in [SHIFT_LEFT_A, SHIFT_LEFT_L, SHIFT_RIGHT_A, SHIFT_RIGHT_L]:
                    if potential_flags[PARITY_OVERFLOW_FLAG]:
                        self.flag_register.set_flag(flag)
                    else:
                        self.flag_register.reset_flag(flag)
                    continue
                if potential_flags[PARITY]:
                    self.flag_register.set_flag(flag)
                else:
                    self.flag_register.reset_flag(flag) 
            elif action == "*":
                if instruction.text in [OUT_INC, OUT_DEC, IN_INC, IN_DEC]:
                    if flag == ZERO_FLAG:
                        if self.B.get_contents() - 1 == 0:
                            self.flag_register.set_flag(flag)
                        else:
                            self.flag_register.reset_flag(flag)
                        continue
                if instruction.text in [CONVERT_CARRY_FLAG]:
                    if flag == CARRY_FLAG:
                        if potential_flags[CARRY_FLAG]:
                            self.flag_register.set_flag(CARRY_FLAG)
                        else:
                            self.flag_register.reset_flag(CARRY_FLAG)
                    continue
                if flag == PARITY_OVERFLOW_FLAG:
                    if self.registers_by_name["BC"].get_contents() - 1 == 0:
                        self.flag_register.reset_flag(flag)
                    else:
                        self.flag_register.set_flag(flag)
            elif action == "0":
                self.flag_register.reset_flag(flag)
            elif action == "1":
                self.flag_register.set_flag(flag)
        potential_flags = {}

    def twos_complement(self, value):
        if value < 128:
            return value
        return value - 256

    def undocumented_behaviour(self, instruction, substituted_left_arg, substituted_right_arg):
        if instruction.instruction_base in [INC, DEC, ADD, ADC, SUB, SBC, ROT_RIGHT_C_ACC, DAA, COMPLEMENT, SET_CARRY_FLAG, CONVERT_CARRY_FLAG, AND, OR, XOR, COMPARE, ROT_LEFT_C, ROT_RIGHT_C, ROT_LEFT, ROT_RIGHT_C, ROT_RIGHT, SHIFT_LEFT_A, SHIFT_RIGHT_A, SHIFT_LEFT_L, SHIFT_RIGHT_L, BIT]:
            if instruction.flags == "------":
                return
            if instruction.instruction_base in [DAA, COMPLEMENT, SET_CARRY_FLAG, CONVERT_CARRY_FLAG, SUB, AND, OR, XOR]:
                substituted_left_arg = self.A
            if instruction.instruction_base in [BIT]:
                if substituted_left_arg == 7 and substituted_right_arg.get_contents() >= 128:
                    self.F.set_flag(SIGN_FLAG)
                else:
                    self.F.reset_flag(SIGN_FLAG)
                if self.F.get_flag(ZERO_FLAG):
                    self.F.set_flag(PARITY_OVERFLOW_FLAG)
                else:
                    self.F.reset_flag(PARITY_OVERFLOW_FLAG)
                if instruction.right_arg == "(ix+*)":
                    temp_comp = Component("temp")
                    temp_comp.set_contents(substituted_right_arg.name // 256)
                    substituted_left_arg = temp_comp
                else:
                    substituted_left_arg = substituted_right_arg
            if substituted_left_arg.SIZE == 2:
                substituted_left_arg = substituted_left_arg.high
            self.F.set_bit_position(5, substituted_left_arg.get_bit_position(5))
            self.F.set_bit_position(3, substituted_left_arg.get_bit_position(3))
