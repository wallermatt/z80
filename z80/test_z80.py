import pytest

from z80 import Z80
from instructions import SPECIAL_ARGS

from base import (
    SIGN_FLAG, ZERO_FLAG, HALF_CARRY_FLAG, PARITY_OVERFLOW_FLAG, ADD_SUBTRACT_FLAG, CARRY_FLAG,
)

def test_initial():
    z80 = Z80()
    assert len(z80.registers) == 32
    assert len(z80.instructions_by_opcode) == 1268
    assert len(z80.memory.contents) == z80.MEMORY_SIZE


def test_read_memory_and_increment_pc():
    z80 = Z80()
    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 99)
    memory_contents, end_of_memory_reached = z80.read_memory_and_increment_pc()
    assert memory_contents == 99
    assert end_of_memory_reached == False
    assert z80.program_counter.get_contents() == 1


def test_run_nop():
    z80 = Z80()
    z80.program_counter.set_contents_value(0)
    z80.run()
    assert z80.program_counter.get_contents() == z80.MEMORY_SIZE - 1


def test_substitute_left_arg():
    z80 = Z80()
    z80.program_counter.set_contents_value(0)

    substituted_arg = z80.substitute_arg(None, None)
    assert substituted_arg == None
    assert z80.program_counter.get_contents() == 0

    substituted_arg = z80.substitute_arg("a", None)
    assert substituted_arg == z80.registers_by_name["A"]
    assert z80.program_counter.get_contents() == 0

    substituted_arg = z80.substitute_arg("hl", None)
    assert substituted_arg == z80.registers_by_name["HL"]
    assert z80.program_counter.get_contents() == 0

    z80.registers_by_name["HL"].set_contents(4000)
    substituted_arg = z80.substitute_arg("(hl)", None)
    assert substituted_arg == z80.memory.get_contents(4000)
    assert z80.program_counter.get_contents() == 0

    z80.memory.load([7, 4, 11, 9, 2, 55])
    substituted_arg = z80.substitute_arg("*", None)
    assert substituted_arg == 7
    assert z80.program_counter.get_contents() == 1

    substituted_arg = z80.substitute_arg("**", None)
    assert substituted_arg == 2820
    assert z80.program_counter.get_contents() == 3

    substituted_arg = z80.substitute_arg("(**)", None)
    assert substituted_arg == z80.memory.get_contents(521)
    assert z80.program_counter.get_contents() == 5

    z80.registers_by_name["IX"].set_contents(2000)
    substituted_arg = z80.substitute_arg("(ix+*)", None)
    assert substituted_arg == z80.memory.get_contents(2055)
    assert z80.program_counter.get_contents() == 6

    z80.registers_by_name["C"].set_contents(44)
    substituted_arg = z80.substitute_arg("(c)", None)
    assert substituted_arg == 44
    assert z80.program_counter.get_contents() == 6

    for arg in SPECIAL_ARGS:
        substituted_arg = z80.substitute_arg(arg, None)
        assert substituted_arg == arg
        assert z80.program_counter.get_contents() == 6

    z80.memory.load([9, 2])
    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(521, 3)
    z80.memory.set_contents_value(522, 1)
    substituted_arg = z80.substitute_arg("(**)", "hl")
    assert len(substituted_arg) == 2
    assert substituted_arg[0].get_contents() == 3
    assert substituted_arg[1].get_contents() == 1
    assert z80.program_counter.get_contents() == 2


def test_substitute_right_arg():
    z80 = Z80()
    z80.program_counter.set_contents_value(0)

    substituted_arg = z80.substitute_right_arg(None)
    assert substituted_arg == None
    assert z80.program_counter.get_contents() == 0

    z80.registers_by_name["A"].set_contents(11)
    substituted_arg = z80.substitute_right_arg("a", None)
    assert substituted_arg == 11
    assert z80.program_counter.get_contents() == 0

    z80.registers_by_name["HL"].set_contents(4000)
    substituted_arg = z80.substitute_right_arg("hl", None)
    assert substituted_arg == 4000
    assert z80.program_counter.get_contents() == 0

    z80.memory.set_contents_value(4000, 99)
    substituted_arg = z80.substitute_right_arg("(hl)", None)
    assert substituted_arg == 99
    assert z80.program_counter.get_contents() == 0

    z80.memory.load([7, 4, 11, 9, 2, 55])
    substituted_arg = z80.substitute_right_arg("*", None)
    assert substituted_arg == 7
    assert z80.program_counter.get_contents() == 1

    substituted_arg = z80.substitute_right_arg("**", None)
    assert substituted_arg == 2820
    assert z80.program_counter.get_contents() == 3

    z80.memory.set_contents_value(521, 99)
    substituted_arg = z80.substitute_right_arg("(**)", None)
    assert substituted_arg == 99
    assert z80.program_counter.get_contents() == 5

    z80.memory.set_contents_value(2055, 98)
    z80.registers_by_name["IX"].set_contents(2000)
    substituted_arg = z80.substitute_right_arg("(ix+*)", None)
    assert substituted_arg == 98
    assert z80.program_counter.get_contents() == 6

    z80.registers_by_name["C"].set_contents(44)
    substituted_arg = z80.substitute_right_arg("(c)", None)
    assert substituted_arg == 44
    assert z80.program_counter.get_contents() == 6

    for arg in SPECIAL_ARGS:
        substituted_arg = z80.substitute_right_arg(arg, None)
        assert substituted_arg == arg
        assert z80.program_counter.get_contents() == 6

    z80.memory.load([9, 2])
    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(521, 3)
    z80.memory.set_contents_value(522, 1)
    substituted_arg = z80.substitute_right_arg("(**)", "hl")
    assert substituted_arg == 259
    assert z80.program_counter.get_contents() == 2


def test_load_execute_instruction():
    z80 = Z80()
    
    z80.program_counter.set_contents_value(0)
    z80.registers_by_name["BC"].set_contents(0)
    instruction = z80.instructions_by_text["ld bc,**"]
    z80.memory.load([4, 11])
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["BC"].get_contents() == 2820
    assert z80.program_counter.get_contents() == 2

    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(2820, 0)
    z80.registers_by_name["A"].set_contents(99)
    z80.registers_by_name["BC"].set_contents(2820)
    instruction = z80.instructions_by_text["ld (bc),a"]
    z80.execute_instruction(instruction)
    assert z80.memory.get_contents_value(2820) == 99
    assert z80.registers_by_name["BC"].get_contents() == 2820
    assert z80.program_counter.get_contents() == 0

    z80.program_counter.set_contents_value(0)
    z80.registers_by_name["B"].set_contents(0)
    instruction = z80.instructions_by_text["ld b,*"]
    z80.memory.load([11])
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["B"].get_contents() == 11
    assert z80.program_counter.get_contents() == 1

    z80.program_counter.set_contents_value(0)
    z80.registers_by_name["A"].set_contents(0)
    z80.registers_by_name["BC"].set_contents(2820)
    z80.memory.set_contents_value(2820, 99)
    instruction = z80.instructions_by_text["ld a,(bc)"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 99
    assert z80.program_counter.get_contents() == 0

    z80.memory.load([9, 2])
    z80.registers_by_name["HL"].set_contents(1000)
    instruction = z80.instructions_by_text["ld (**),hl"]
    z80.execute_instruction(instruction)
    assert z80.memory.get_contents_value(521) == 232
    assert z80.memory.get_contents_value(522) ==  3
    assert z80.program_counter.get_contents() == 2

    z80.program_counter.set_contents_value(0)
    z80.memory.load([9, 2])
    z80.registers_by_name["HL"].set_contents(0)
    z80.memory.set_contents_value(521, 232)
    z80.memory.set_contents_value(522, 3)
    instruction = z80.instructions_by_text["ld hl,(**)"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["HL"].get_contents() == 1000
    assert z80.program_counter.get_contents() == 2

    z80.program_counter.set_contents_value(0)
    z80.memory.load([54])
    z80.registers_by_name["HL"].set_contents(1000)
    z80.memory.set_contents_value(1000, 0)
    z80.memory.set_contents_value(1001, 100)
    instruction = z80.instructions_by_text["ld (hl),*"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["HL"].get_contents() == 1000
    assert z80.memory.get_contents_value(1000) == 54
    assert z80.memory.get_contents_value(1001) ==  100
    assert z80.program_counter.get_contents() == 1

    z80.program_counter.set_contents_value(0)
    z80.registers_by_name["B"].set_contents(0)
    z80.registers_by_name["C"].set_contents(100)
    instruction = z80.instructions_by_text["ld b,c"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["B"].get_contents() == 100
    assert z80.registers_by_name["C"].get_contents() == 100
    assert z80.program_counter.get_contents() == 0

def test_exchange_multi_instruction():
    z80 = Z80()
    
    z80.program_counter.set_contents_value(0)
    z80.registers_by_name["BC"].set_contents(1)
    z80.registers_by_name["DE"].set_contents(2)
    z80.registers_by_name["HL"].set_contents(3)
    z80.registers_by_name["BC'"].set_contents(10)
    z80.registers_by_name["DE'"].set_contents(20)
    z80.registers_by_name["HL'"].set_contents(30)
    instruction = z80.instructions_by_text["exx"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["BC"].get_contents() == 10
    assert z80.registers_by_name["DE"].get_contents() == 20
    assert z80.registers_by_name["HL"].get_contents() == 30
    assert z80.registers_by_name["BC'"].get_contents() == 1
    assert z80.registers_by_name["DE'"].get_contents() == 2
    assert z80.registers_by_name["HL'"].get_contents() == 3
    assert z80.program_counter.get_contents() == 0


def test_exchange_instruction():
    z80 = Z80()

    z80.program_counter.set_contents_value(0)
    z80.registers_by_name["DE"].set_contents(10)
    z80.registers_by_name["HL"].set_contents(20)
    instruction = z80.instructions_by_text["ex de,hl"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["DE"].get_contents() == 20
    assert z80.registers_by_name["HL"].get_contents() == 10
    assert z80.program_counter.get_contents() == 0

    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(1000, 1)
    z80.memory.set_contents_value(1001, 2)
    z80.registers_by_name["SP"].set_contents(1000)
    z80.registers_by_name["HL"].set_contents(20)
    instruction = z80.instructions_by_text["ex (sp),hl"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["HL"].get_contents() == 513
    assert z80.memory.get_contents_value(1000) == 20
    assert z80.memory.get_contents_value(1001) == 0
    assert z80.program_counter.get_contents() == 0

    z80.program_counter.set_contents_value(0)
    z80.registers_by_name["A"].set_contents(0)
    z80.registers_by_name["BC"].set_contents(2820)
    z80.memory.set_contents_value(2820, 99)
    instruction = z80.instructions_by_text["ld a,(bc)"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 99
    assert z80.program_counter.get_contents() == 0


def test_add_execute():
    z80 = Z80()
    
    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(0)
    z80.registers_by_name["HL"].set_contents(2820)
    z80.memory.set_contents_value(2820, 99)
    instruction = z80.instructions_by_text["add a,(hl)"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 99
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 0
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 0
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0

    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(10)
    instruction = z80.instructions_by_text["add a,a"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 20
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 1
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 0
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0

    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(10)
    z80.registers_by_name["B"].set_contents(250)
    instruction = z80.instructions_by_text["add a,b"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 4
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 1
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 0
    assert z80.flag_register.get_flag(CARRY_FLAG) == 1

    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["IY"].set_contents(10)
    z80.registers_by_name["DE"].set_contents(250)
    instruction = z80.instructions_by_text["add iy,de"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["IY"].get_contents() == 260
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 0
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 0
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0

    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 99)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(10)
    instruction = z80.instructions_by_text["add a,*"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 109
    assert z80.program_counter.get_contents() == 1
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 0
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 0
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0

    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(10)
    z80.registers_by_name["IYL"].set_contents(255)
    instruction = z80.instructions_by_text["add a,iyl"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 9
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 1
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 0
    assert z80.flag_register.get_flag(CARRY_FLAG) == 1

    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 99)
    z80.memory.set_contents_value(116, 120)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(10)
    z80.registers_by_name["IY"].set_contents(17)
    instruction = z80.instructions_by_text["add a,(iy+*)"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 130
    assert z80.program_counter.get_contents() == 1
    assert z80.flag_register.get_flag(SIGN_FLAG) == 1
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 1
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 1
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 0
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0

def test_subtract_execute():
    z80 = Z80()
    
    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(100)
    z80.registers_by_name["B"].set_contents(99)
    instruction = z80.instructions_by_text["sub b"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 1
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 0
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 1
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0

    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(1)
    z80.registers_by_name["IXL"].set_contents(99)
    instruction = z80.instructions_by_text["sub ixl"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 158
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 1
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 1
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 1
    assert z80.flag_register.get_flag(CARRY_FLAG) == 1

    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(1)
    z80.registers_by_name["IX"].set_contents(99)
    z80.memory.set_contents_value(0, 10)
    z80.memory.set_contents_value(109, 1)
    instruction = z80.instructions_by_text["sub (ix+*)"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 0
    assert z80.program_counter.get_contents() == 1
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 1
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 0
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 1
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0

    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(1)
    z80.memory.set_contents_value(0, 10)
    instruction = z80.instructions_by_text["sub *"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 247
    assert z80.program_counter.get_contents() == 1
    assert z80.flag_register.get_flag(SIGN_FLAG) == 1
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 1
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 1
    assert z80.flag_register.get_flag(CARRY_FLAG) == 1

def test_adc_execute():
    z80 = Z80()
    
    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(0)
    z80.registers_by_name["HL"].set_contents(2820)
    z80.memory.set_contents_value(2820, 99)
    instruction = z80.instructions_by_text["adc a,(hl)"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 99
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 0
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 0
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0
    
    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_flag(CARRY_FLAG)
    z80.registers_by_name["A"].set_contents(0)
    z80.registers_by_name["HL"].set_contents(2820)
    z80.memory.set_contents_value(2820, 99)
    instruction = z80.instructions_by_text["adc a,(hl)"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 100
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 0
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 0
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0

    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_flag(CARRY_FLAG)
    z80.registers_by_name["HL"].set_contents(4000)
    z80.registers_by_name["BC"].set_contents(500)
    z80.memory.set_contents_value(2820, 99)
    instruction = z80.instructions_by_text["adc hl,bc"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["HL"].get_contents() == 4501
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 1
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 0
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0

def test_sbc_execute():
    z80 = Z80()
    
    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(100)
    z80.registers_by_name["B"].set_contents(99)
    instruction = z80.instructions_by_text["sbc a,b"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 1
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 0
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 1
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0

    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_flag(CARRY_FLAG)
    z80.registers_by_name["A"].set_contents(100)
    z80.registers_by_name["B"].set_contents(99)
    instruction = z80.instructions_by_text["sbc a,b"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 0
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 1
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 0
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 1
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0

def test_inc_execute():
    z80 = Z80()
    
    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(100)
    instruction = z80.instructions_by_text["inc a"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 101
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 0
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 0
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0

    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["IX"].set_contents(5000)
    z80.memory.set_contents_value(0, 55)
    z80.memory.set_contents_value(5055, 77)
    instruction = z80.instructions_by_text["inc (ix+*)"]
    z80.execute_instruction(instruction)
    assert z80.memory.get_contents_value(5055) == 78
    assert z80.program_counter.get_contents() == 1
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 0
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 0
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0


def test_dec_execute():
    z80 = Z80()
    
    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["A"].set_contents(100)
    instruction = z80.instructions_by_text["dec a"]
    z80.execute_instruction(instruction)
    assert z80.registers_by_name["A"].get_contents() == 99
    assert z80.program_counter.get_contents() == 0
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 0
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 1
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0

    z80.program_counter.set_contents_value(0)
    z80.flag_register.set_contents(0)
    z80.registers_by_name["IX"].set_contents_value(5000)
    z80.memory.set_contents_value(0, 55)
    z80.memory.set_contents_value(5055, 77)
    instruction = z80.instructions_by_text["dec (ix+*)"]
    z80.execute_instruction(instruction)
    assert z80.memory.get_contents_value(5055) == 76
    assert z80.program_counter.get_contents() == 1
    assert z80.flag_register.get_flag(SIGN_FLAG) == 0
    assert z80.flag_register.get_flag(ZERO_FLAG) == 0
    assert z80.flag_register.get_flag(HALF_CARRY_FLAG) == 0
    assert z80.flag_register.get_flag(PARITY_OVERFLOW_FLAG) == 0
    assert z80.flag_register.get_flag(ADD_SUBTRACT_FLAG) == 1
    assert z80.flag_register.get_flag(CARRY_FLAG) == 0


def test_push_execute():
    z80 = Z80()

    z80.program_counter.set_contents_value(0)
    z80.stack_pointer.set_contents_value(50000)
    z80.memory.set_contents_value(49999, 0)
    z80.memory.set_contents_value(49998, 0)
    z80.registers_by_name["IX"].set_contents_value(5000)
    instruction = z80.instructions_by_text["push ix"]
    z80.execute_instruction(instruction)
    assert z80.stack_pointer.get_contents() == 49998
    assert z80.memory.get_contents_value(49999) == 19
    assert z80.memory.get_contents_value(49998) == 136
    assert z80.program_counter.get_contents() == 0


def test_pop_execute():
    z80 = Z80()
    
    z80.program_counter.set_contents_value(0)
    z80.stack_pointer.set_contents_value(49998)
    z80.memory.set_contents_value(49999, 19)
    z80.memory.set_contents_value(49998, 136)
    z80.registers_by_name["IX"].set_contents_value(0)
    instruction = z80.instructions_by_text["pop ix"]
    z80.execute_instruction(instruction)
    assert z80.stack_pointer.get_contents() == 50000
    assert z80.memory.get_contents_value(49999) == 19
    assert z80.memory.get_contents_value(49998) == 136
    assert z80.program_counter.get_contents() == 0


def test_jump_execute():
    z80 = Z80()
    
    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 19)
    z80.memory.set_contents_value(1, 136)
    instruction = z80.instructions_by_text["jp **"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 34835
    
    z80.program_counter.set_contents_value(0)
    z80.registers_by_name["HL"].set_contents_value(5000)
    instruction = z80.instructions_by_text["jp (hl)"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 5000
    
    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 19)
    z80.memory.set_contents_value(1, 136)
    z80.flag_register.set_flag(ZERO_FLAG)
    instruction = z80.instructions_by_text["jp nz,**"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 2

    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 19)
    z80.memory.set_contents_value(1, 136)
    z80.flag_register.reset_flag(ZERO_FLAG)
    instruction = z80.instructions_by_text["jp nz,**"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 34835

    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 19)
    z80.memory.set_contents_value(1, 136)
    z80.flag_register.set_flag(ZERO_FLAG)
    instruction = z80.instructions_by_text["jp z,**"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 34835

    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 19)
    z80.memory.set_contents_value(1, 136)
    z80.flag_register.set_flag(CARRY_FLAG)
    instruction = z80.instructions_by_text["jp c,**"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 34835

    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 19)
    z80.memory.set_contents_value(1, 136)
    z80.flag_register.set_flag(CARRY_FLAG)
    instruction = z80.instructions_by_text["jp nc,**"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 2

    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 19)
    z80.memory.set_contents_value(1, 136)
    z80.flag_register.set_flag(PARITY_OVERFLOW_FLAG)
    instruction = z80.instructions_by_text["jp po,**"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 34835

    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 19)
    z80.memory.set_contents_value(1, 136)
    z80.flag_register.set_flag(PARITY_OVERFLOW_FLAG)
    instruction = z80.instructions_by_text["jp pe,**"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 2

    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 19)
    z80.memory.set_contents_value(1, 136)
    z80.flag_register.set_flag(SIGN_FLAG)
    instruction = z80.instructions_by_text["jp p,**"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 2

    z80.program_counter.set_contents_value(0)
    z80.memory.set_contents_value(0, 19)
    z80.memory.set_contents_value(1, 136)
    z80.flag_register.set_flag(SIGN_FLAG)
    instruction = z80.instructions_by_text["jp m,**"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 34835



'''


('djnz *', 'The b register is decremented, and if not zero, the signed value * is added to pc. The jump is measured from the start of the instruction opcode.')

cc Condition
Relevant
Flag
000 Non-Zero (NZ) Z
001 Zero (Z) Z
010 No Carry (NC) C
011 Carry (C) C
100 Parity Odd (PO) P/V
101 Parity Even (PE) P/V
110 Sign Positive (P) S
111 Sign Negative (M) S

'''

def test_jump_relative_execute():
    z80 = Z80()

    z80.program_counter.set_contents_value(1)
    z80.memory.set_contents_value(1, 19)
    instruction = z80.instructions_by_text["jr *"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 19

def test_dec_jump_relative_execute():
    z80 = Z80()