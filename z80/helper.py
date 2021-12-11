import unittest

from z80 import Z80
from base import (
    SIGN_FLAG, ZERO_FLAG, HALF_CARRY_FLAG, PARITY_OVERFLOW_FLAG, ADD_SUBTRACT_FLAG, CARRY_FLAG
)


FLAGS = [
    SIGN_FLAG,
    ZERO_FLAG,
    HALF_CARRY_FLAG,
    PARITY_OVERFLOW_FLAG,
    ADD_SUBTRACT_FLAG,
    CARRY_FLAG,
]


class DoubleByte:
    BYTE = 256

    def __init__(self, value):
        self.value = value
        self.low = value % self.BYTE
        self.high = value // self.BYTE


class Z80TestHandler:
    def __init__(self, registers, flags, memory, ports, instruction_text, run=True, run_fuse=False):
        self.z80 = Z80()
        self.test_registers = registers
        self.test_flags = flags
        self.test_memory = memory
        self.test_ports = ports
        self.instruction_text = instruction_text
        self.set_registers()
        self.set_flags()
        self.set_memory()
        self.set_ports()
        if run:
            self.run_test()
        elif run_fuse:
            self.run_fuse_test()

    def run_test(self):
        instruction = self.z80.instructions_by_text[self.instruction_text]
        self.z80.execute_instruction(instruction)
        self.run_assertions()

    def run_fuse_test(self):
        opcode, end_of_memory_reached = self.z80.read_memory_and_increment_pc()
        if str(opcode) not in self.z80.instructions_by_opcode:
            raise Exception("Opcode {} not recognised!!!".format(opcode))
        instruction = self.z80.instructions_by_opcode[str(opcode)]
        self.z80.execute_instruction(instruction)
        self.assert_registers()
        self.assert_memory()


    def run_assertions(self):
        self.assert_registers()
        self.assert_flags()
        self.assert_memory()
        self.assert_ports()

    def set_registers(self):
        for r in self.test_registers:
            initial_value = self.test_registers[r][0]
            register = self.z80.registers_by_name[r]
            if register.SIZE == 1:
                register.set_contents(initial_value)
            else:
                register.set_contents_value(initial_value)

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

    def set_ports(self):
        for p in self.test_ports:
            value = self.test_ports[p][0]
            self.z80.ports.set_contents_value(p, value)

    def assert_registers(self):
        additional_test_registers = set()
        for r in self.test_registers:
            reg = self.z80.registers_by_name[r]
            if reg.SIZE == 2:
                additional_test_registers.add(reg.low.name)
                additional_test_registers.add(reg.high.name)

        for r in self.z80.registers_by_name:
            if r in ["F", "AF"] and r not in self.test_registers:
                continue
            if r in additional_test_registers:
                continue
            reg = self.z80.registers_by_name[r]
            if reg.SIZE == 2 and (reg.low.name in self.test_registers or reg.high.name in self.test_registers):
                continue
            expected_value = 0
            if r in self.test_registers:
                expected_value = self.test_registers[r][1]
            actual_value =  reg.get_contents()
            assert expected_value == actual_value, f"Instruction: {self.instruction_text}, Register: {r}, expected value: {expected_value}, actual value: {actual_value}"

    def assert_flags(self):
        for f in FLAGS:
            expected_value = 0 
            if f in self.test_flags:
                expected_value = self.test_flags[f][1]
            actual_value =  self.z80.flag_register.get_flag(f)
            assert expected_value == actual_value, f"Instruction: {self.instruction_text}, Flag: {f}, expected value: {expected_value}, actual value: {actual_value}"

    def assert_memory(self):
        for m in self.test_memory:
            expected_value = self.test_memory[m][1]
            actual_value =  self.z80.memory.get_contents_value(m)
            assert expected_value == actual_value, f"Instruction: {self.instruction_text}, Memory: {m}, expected value: {expected_value}, actual value: {actual_value}"

    def assert_ports(self):
        for p in self.test_ports:
            expected_value = self.test_ports[p][1]
            actual_value =  self.z80.ports.get_contents_value(p)
            assert expected_value == actual_value, f"Instruction: {self.instruction_text}, Port: {p}, expected value: {expected_value}, actual value: {actual_value}"
