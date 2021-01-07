import pytest

from z80 import Z80

def test_initial():
    z80 = Z80()
    assert len(z80.registers) == 32
    assert len(z80.instructions_by_opcode) == 1268
    assert len(z80.memory.contents) == z80.MEMORY_SIZE


def test_read_memory_and_increment_pc():
    z80 = Z80()
    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 99)
    memory_contents = z80.read_memory_and_increment_pc()
    assert memory_contents == 99
    assert z80.program_counter.get_contents() == 1


def test_run():
    z80 = Z80()
    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 99)
    z80.run()
    assert z80.program_counter.get_contents() == 1
