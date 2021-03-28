import unittest

from z80 import Z80

class DoubleByte:
    BYTE = 256

    def __init__(self, value):
        self.value = value
        self.low = value % self.BYTE
        self.high = value // self.BYTE


class Z80TestHandler:
    def __init__(self, registers, flags, memory, instruction_text):
        self.z80 = Z80()
        self.test_registers = registers
        self.test_flags = flags
        self.test_memory = memory
        self.instruction_text = instruction_text
        self.set_registers()
        self.set_flags()
        self.set_memory()

    def run_test(self):
        instruction = self.z80.instructions_by_text[self.instruction_text]
        self.z80.execute_instruction(instruction)
        self.run_assertions()

    def run_assertions(self):
        self.assert_registers()
        self.assert_flags()
        self.assert_memory()

    def set_registers(self):
        for r in self.test_registers:
            initial_value = self.test_registers[r][0]
            self.z80.registers_by_name[r].set_contents(initial_value)

    def set_flags(self):
        for f in self.test_flags:
            if self.test_flags[f][0]:
                self.z80.flag_register.set_flag(f)
            else:
                self.z80.flag_register.reset_flag(f)

    def set_memory(self):
        for m in self.test_memory:
            value = self.test_memory[m][0]
            self.z80.memory.set_contents_value(m, value)

    def assert_registers(self):
        for r in self.test_registers:
            expected_value = self.test_registers[r][1]
            actual_value =  self.z80.registers_by_name[r].get_contents()
            assert expected_value == actual_value, f"Instruction: {self.instruction_text}, Register: {r}, expected value: {expected_value}, actual value: {actual_value}"

    def assert_flags(self):
        for f in self.test_flags:
            expected_value = self.test_flags[f][1]
            actual_value =  self.z80.flag_register.get_flag(f)
            assert expected_value == actual_value, f"Instruction: {self.instruction_text}, Flag: {f}, expected value: {expected_value}, actual value: {actual_value}"

    def assert_memory(self):
        for m in self.test_memory:
            expected_value = self.test_memory[m][1]
            actual_value =  self.z80.memory.get_contents_value(m)
            assert expected_value == actual_value, f"Instruction: {self.instruction_text}, Memory: {m}, expected value: {expected_value}, actual value: {actual_value}"
