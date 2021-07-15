import pytest

from z80 import Z80
from instructions import SPECIAL_ARGS

from base import (
    SIGN_FLAG, ZERO_FLAG, HALF_CARRY_FLAG, PARITY_OVERFLOW_FLAG, ADD_SUBTRACT_FLAG, CARRY_FLAG,
)

from helper import Z80TestHandler, DoubleByte


def test_handler():
    Z80TestHandler(
        {"A": (0,0), "PC": (0,1)},
        {SIGN_FLAG: (0,0)},
        {0: (0, 0)},
        {0: (0, 0)},
        "ld a,*"
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
        if arg.isdigit():
            assert substituted_arg == int(arg)
        else:
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


def test_jump_relative_execute():
    z80 = Z80()

    z80.program_counter.set_contents_value(1)
    z80.memory.set_contents_value(1, 19)
    instruction = z80.instructions_by_text["jr *"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 19

def test_dec_jump_relative_execute_zero():
    z80 = Z80()
    
    z80.program_counter.set_contents_value(1)
    z80.registers_by_name["B"].set_contents(1)
    z80.memory.set_contents_value(1, 19)
    instruction = z80.instructions_by_text["djnz *"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 2
    

def test_dec_jump_relative_execute_non_zero():
    z80 = Z80()

    z80.program_counter.set_contents_value(1)
    z80.registers_by_name["B"].set_contents(2)
    z80.memory.set_contents_value(1, 19)
    instruction = z80.instructions_by_text["djnz *"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 19
    

def test_call_nn_execute():
    z80 = Z80()

    z80.program_counter.set_contents_value(1000)
    z80.stack_pointer.set_contents_value(50000)
    z80.memory.set_contents_value(1000, 19)
    z80.memory.set_contents_value(1001, 1)
    instruction = z80.instructions_by_text["call **"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 275
    assert z80.stack_pointer.get_contents() == 49998
    assert z80.memory.get_contents_value(49999) == 3
    assert z80.memory.get_contents_value(49998) == 234


def test_call_nz_execute():
    z80 = Z80()

    z80.program_counter.set_contents_value(1000)
    z80.stack_pointer.set_contents_value(50000)
    z80.memory.set_contents_value(1000, 19)
    z80.memory.set_contents_value(1001, 1)
    z80.flag_register.set_flag(ZERO_FLAG)
    instruction = z80.instructions_by_text["call nz,**"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 1002
    assert z80.stack_pointer.get_contents() == 50000

    z80.program_counter.set_contents_value(1000)
    z80.stack_pointer.set_contents_value(50000)
    z80.memory.set_contents_value(1000, 19)
    z80.memory.set_contents_value(1001, 1)
    z80.flag_register.reset_flag(ZERO_FLAG)
    instruction = z80.instructions_by_text["call nz,**"]
    z80.execute_instruction(instruction)
    assert z80.program_counter.get_contents() == 275
    assert z80.stack_pointer.get_contents() == 49998
    assert z80.memory.get_contents_value(49999) == 3
    assert z80.memory.get_contents_value(49998) == 234


def test_call_nz_execute_non_zero():
    # Constant attributes - value, low, high
    pc = DoubleByte(1000)
    sp = DoubleByte(50000)
    var = DoubleByte(275)

    Z80TestHandler(
        # Register: (before, after)
        {
            "PC": (pc.value, var.value),
            "SP": (sp.value, sp.value - 2)
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0,0)
        },
        # Memory location: (before, after)
        {
            pc.value : (var.low, var.low),
            pc.value + 1: (var.high, var.high),
            sp.value - 1: (0, pc.high),
            sp.value - 2: (0, pc.low + 2)
        },
        # Ports: (before, after)
        {},
        # Command
        "call nz,**"
    )

def test_call_nz_execute_zero():
    # Constant attributes - value, low, high
    pc = DoubleByte(1000)
    sp = DoubleByte(50000)
    var = DoubleByte(275)

    Z80TestHandler(
        # Register: (before, after)
        {
            "PC": (pc.value, pc.value + 2),
            "SP": (sp.value, sp.value)
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (1,1)
        },
        # Memory location: (before, after)
        {
            pc.value : (var.low, var.low),
            pc.value + 1: (var.high, var.high),
            sp.value - 1: (0, 0),
            sp.value - 2: (0, 0)
        },
        # Ports: (before, after)
        {},
        # Command
        "call nz,**"
    )


def test_dec_jump_relative_execute_non_zero_helper():
        # Constant attributes - value, low, high
    pc = DoubleByte(1)
    b = DoubleByte(2)
    var = DoubleByte(19)

    Z80TestHandler(
        # Register: (before, after)
        {
            "PC": (pc.value, var.low),
            "B": (b.value, b.value - 1)
        },
        # Flag: (before, after)
        {},
        # Memory location: (before, after)
        {
            pc.value : (var.low, var.low),
        },
        # Ports: (before, after)
        {},
        # Command
        "djnz *"
    )

def test_dec_jump_relative_execute_zero_helper():
    # Constant attributes - value, low, high
    pc = DoubleByte(1)
    b = DoubleByte(1)
    var = DoubleByte(19)

    Z80TestHandler(
        # Register: (before, after)
        {
            "PC": (pc.value, pc.value + 1),
            "B": (b.value, b.value - 1)
        },
        # Flag: (before, after)
        {},
        # Memory location: (before, after)
        {
            pc.value : (var.low, var.low),
        },
        # Ports: (before, after)
        {},
        # Command
        "djnz *"
    )

def test_cp_e_equal():
    # Constant attributes - value, low, high
    pc = DoubleByte(0)

    Z80TestHandler(
        # Register: (before, after)
        {
            "PC": (pc.value, pc.value),
            "A": (10, 10),
            "E": (10, 10)
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0, 1),
            CARRY_FLAG: (0, 0),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        {},
        # Ports: (before, after)
        {},
        # Command
        "cp e"
    )

def test_cp_b_gt():
    # Constant attributes - value, low, high
    pc = DoubleByte(0)

    Z80TestHandler(
        # Register: (before, after)
        {
            "PC": (pc.value, pc.value),
            "A": (10, 10),
            "B": (20, 20)
        },
        # Flag: (before, after)
        {
            SIGN_FLAG: (0, 1),
            ZERO_FLAG: (0, 0),
            CARRY_FLAG: (0, 1),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        {},
        # Ports: (before, after)
        {},
        # Command
        "cp b"
    )

def test_cp_iy_disp_mem_lt():
    # Constant attributes - value, low, high
    pc = DoubleByte(0)
    iy = DoubleByte(1000)
    disp = 50

    Z80TestHandler(
        # Register: (before, after)
        {
            "PC": (pc.value, pc.value + 1),
            "A": (10, 10),
            "IY": (iy.value, iy.value)
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0, 0),
            CARRY_FLAG: (0, 0),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {
            pc.value: (disp, disp),
            iy.value + disp: (5, 5)
        },
        # Ports: (before, after)
        {},
        # Command
        "cp (iy+*)"
    )


def test_cpi():
    # Constant attributes - value, low, high
    pc = DoubleByte(0)
    hl = DoubleByte(1000)
    bc = DoubleByte(2000)

    Z80TestHandler(
        # Register: (before, after)
        {
            "PC": (pc.value, pc.value),
            "A": (10, 10),
            "HL": (hl.value, hl.value + 1),
            "BC": (bc.value, bc.value - 1)
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0, 1),
            CARRY_FLAG: (0, 0),
            ADD_SUBTRACT_FLAG: (0, 1),
            PARITY_OVERFLOW_FLAG: (0, 1)
        },
        # Memory location: (before, after)
        {
            hl.value: (10, 10),
            hl.value + 1: (0, 0)
        },
        # Ports: (before, after)
        {},
        # Command
        "cpi"
    )


def test_cpir_found():
    # Constant attributes - value, low, high
    pc = DoubleByte(0)
    hl = DoubleByte(1000)
    bc = DoubleByte(5)

    Z80TestHandler(
        # Register: (before, after)
        {
            "PC": (pc.value, pc.value),
            "A": (10, 10),
            "HL": (hl.value, hl.value + bc.value - 1),
            "BC": (bc.value, 1)
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0, 1),
            CARRY_FLAG: (0, 0),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {
            hl.value + bc.value - 2: (10, 10)
        },
        # Ports: (before, after)
        {},
        # Command
        "cpir"
    )


def test_cpir_not_found():
    # Constant attributes - value, low, high
    pc = DoubleByte(0)
    hl = DoubleByte(1000)
    bc = DoubleByte(5)

    Z80TestHandler(
        # Register: (before, after)
        {
            "PC": (pc.value, pc.value),
            "A": (10, 10),
            "HL": (hl.value, hl.value + bc.value),
            "BC": (bc.value, 0)
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0, 0),
            CARRY_FLAG: (0, 0),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {},
        # Command
        "cpir"
    )


def test_cpd():
    # Constant attributes - value, low, high
    pc = DoubleByte(0)
    hl = DoubleByte(1000)
    bc = DoubleByte(2000)

    Z80TestHandler(
        # Register: (before, after)
        {
            "PC": (pc.value, pc.value),
            "A": (10, 10),
            "HL": (hl.value, hl.value - 1),
            "BC": (bc.value, bc.value - 1)
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0, 1),
            CARRY_FLAG: (0, 0),
            ADD_SUBTRACT_FLAG: (0, 1),
            PARITY_OVERFLOW_FLAG: (0, 1)
        },
        # Memory location: (before, after)
        {
            hl.value: (10, 10),
        },
        # Ports: (before, after)
        {},
        # Command
        "cpd"
    )


def test_cpdr_found():
    # Constant attributes - value, low, high
    pc = DoubleByte(0)
    hl = DoubleByte(1000)
    bc = DoubleByte(5)

    Z80TestHandler(
        # Register: (before, after)
        {
            "PC": (pc.value, pc.value),
            "A": (10, 10),
            "HL": (hl.value, hl.value - bc.value + 1),
            "BC": (bc.value, 1)
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0, 1),
            CARRY_FLAG: (0, 0),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {
            hl.value - bc.value + 2: (10, 10)
        },
        # Ports: (before, after)
        {},
        # Command
        "cpdr"
    )


def test_cpdr_not_found():
    # Constant attributes - value, low, high
    pc = DoubleByte(0)
    hl = DoubleByte(1000)
    bc = DoubleByte(5)

    Z80TestHandler(
        # Register: (before, after)
        {
            "PC": (pc.value, pc.value),
            "A": (10, 10),
            "HL": (hl.value, hl.value - bc.value),
            "BC": (bc.value, 0)
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0, 0),
            CARRY_FLAG: (0, 0),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {},
        # Command
        "cpdr"
    )


def test_cpl():
    # Constant attributes - value, low, high
    a_initial = 254
    a_complement = 1

    Z80TestHandler(
        # Register: (before, after)
        {
            "A": (a_initial, a_complement),
        },
        # Flag: (before, after)
        {
            HALF_CARRY_FLAG: (0, 1),
            ADD_SUBTRACT_FLAG: (0, 1)
        },
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {},
        # Command
        "cpl"
    )


def test_ldi():
    # Constant attributes - value, low, high
    hl = DoubleByte(1000)
    de = DoubleByte(20000)
    bc = DoubleByte(5)

    Z80TestHandler(
        # Register: (before, after)
        {
            "HL": (hl.value, hl.value + 1),
            "DE": (de.value, de.value + 1),
            "BC": (bc.value, bc.value - 1)
        },
        # Flag: (before, after)
        {
            HALF_CARRY_FLAG: (1, 0),
            PARITY_OVERFLOW_FLAG: (0, 1),
            ADD_SUBTRACT_FLAG: (1, 0)
        },
        # Memory location: (before, after)
        {
            hl.value: (99, 99),
            de.value: (0, 99)
        },
        # Ports: (before, after)
        {},
        # Command
        "ldi"
    )

def test_ldd():
    # Constant attributes - value, low, high
    hl = DoubleByte(1000)
    de = DoubleByte(20000)
    bc = DoubleByte(5)

    Z80TestHandler(
        # Register: (before, after)
        {
            "HL": (hl.value, hl.value - 1),
            "DE": (de.value, de.value - 1),
            "BC": (bc.value, bc.value - 1)
        },
        # Flag: (before, after)
        {
            HALF_CARRY_FLAG: (1, 0),
            PARITY_OVERFLOW_FLAG: (0, 1),
            ADD_SUBTRACT_FLAG: (1, 0)
        },
        # Memory location: (before, after)
        {
            hl.value: (99, 99),
            de.value: (0, 99)
        },
        # Ports: (before, after)
        {},
        # Command
        "ldd"
    )

def test_ldir():
    # Constant attributes - value, low, high
    hl = DoubleByte(1000)
    de = DoubleByte(20000)
    bc = DoubleByte(4)

    Z80TestHandler(
        # Register: (before, after)
        {
            "HL": (hl.value, hl.value + bc.value),
            "DE": (de.value, de.value + bc.value),
            "BC": (bc.value, 0)
        },
        # Flag: (before, after)
        {
            HALF_CARRY_FLAG: (1, 0),
            PARITY_OVERFLOW_FLAG: (1, 0),
            ADD_SUBTRACT_FLAG: (1, 0)
        },
        # Memory location: (before, after)
        {
            hl.value: (99, 99),
            hl.value + 1: (98, 98),
            hl.value + 2: (97, 97),
            hl.value + 3: (96, 96),
            hl.value + 4: (95, 95),
            de.value: (0, 99),
            de.value + 1: (0, 98),
            de.value + 2: (0, 97),
            de.value + 3: (0, 96),
            de.value + 4: (0, 0)
        },
        # Ports: (before, after)
        {},
        # Command
        "ldir"
    )


def test_lddr():
    # Constant attributes - value, low, high
    hl = DoubleByte(1000)
    de = DoubleByte(20000)
    bc = DoubleByte(4)

    Z80TestHandler(
        # Register: (before, after)
        {
            "HL": (hl.value, hl.value - bc.value),
            "DE": (de.value, de.value - bc.value),
            "BC": (bc.value, 0)
        },
        # Flag: (before, after)
        {
            HALF_CARRY_FLAG: (1, 0),
            PARITY_OVERFLOW_FLAG: (1, 0),
            ADD_SUBTRACT_FLAG: (1, 0)
        },
        # Memory location: (before, after)
        {
            hl.value: (99, 99),
            hl.value - 1: (98, 98),
            hl.value - 2: (97, 97),
            hl.value - 3: (96, 96),
            hl.value - 4: (95, 95),
            de.value: (0, 99),
            de.value - 1: (0, 98),
            de.value - 2: (0, 97),
            de.value - 3: (0, 96),
            de.value - 4: (0, 0)
        },
        # Ports: (before, after)
        {},
        # Command
        "lddr"
    )

def test_and_const():
    # Constant attributes - value, low, high
    a = DoubleByte(170)
    const = DoubleByte(85)

    Z80TestHandler(
        # Register: (before, after)
        {
            "A": (a.value, a.value & const.value),   # 0
            "PC": (0, 1),
        },
        # Flag: (before, after)
        {
            SIGN_FLAG: (1, 0),
            HALF_CARRY_FLAG: (0, 1),
            PARITY_OVERFLOW_FLAG: (0, 0),
            ADD_SUBTRACT_FLAG: (1, 0),
            ZERO_FLAG: (0, 1),
            CARRY_FLAG: (1, 0)
        },
        # Memory location: (before, after)
        {
            0: (const.value, const.value),
        },
        # Ports: (before, after)
        {},
        # Command
        "and *"
    )

def test_and_hl():
    # Constant attributes - value, low, high
    a = DoubleByte(255)
    hl = DoubleByte(10000)
    const = DoubleByte(85)

    Z80TestHandler(
        # Register: (before, after)
        {
            "A": (a.value, a.value & const.value),  
            "HL": (hl.value, hl.value),
        },
        # Flag: (before, after)
        {
            SIGN_FLAG: (1, 0),
            HALF_CARRY_FLAG: (0, 1),
            PARITY_OVERFLOW_FLAG: (0, 1),
            ADD_SUBTRACT_FLAG: (1, 0),
            ZERO_FLAG: (1, 0),
            CARRY_FLAG: (1, 0)
        },
        # Memory location: (before, after)
        {
            hl.value: (const.value, const.value),
        },
        # Ports: (before, after)
        {},
        # Command
        "and (hl)"
    )

def test_and_a():
    # Constant attributes - value, low, high
    a = DoubleByte(255)

    Z80TestHandler(
        # Register: (before, after)
        {
            "A": (a.value, a.value & a.value),   # a
        },
        # Flag: (before, after)
        {
            SIGN_FLAG: (0, 1),
            HALF_CARRY_FLAG: (0, 1),
            PARITY_OVERFLOW_FLAG: (0, 0),
            ADD_SUBTRACT_FLAG: (1, 0),
            ZERO_FLAG: (1, 0),
            CARRY_FLAG: (1, 0)
        },
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {},
        # Command
        "and a"
    )

def test_or_const():
    # Constant attributes - value, low, high
    a = DoubleByte(170)
    const = DoubleByte(85)

    Z80TestHandler(
        # Register: (before, after)
        {
            "A": (a.value, a.value | const.value),   
            "PC": (0, 1),
        },
        # Flag: (before, after)
        {
            SIGN_FLAG: (0, 1),
            HALF_CARRY_FLAG: (1, 0),
            PARITY_OVERFLOW_FLAG: (0, 0),
            ADD_SUBTRACT_FLAG: (1, 0),
            ZERO_FLAG: (1, 0),
            CARRY_FLAG: (1, 0)
        },
        # Memory location: (before, after)
        {
            0: (const.value, const.value),
        },
        # Ports: (before, after)
        {},
        # Command
        "or *"
    )

def test_xor_const():
    # Constant attributes - value, low, high
    a = DoubleByte(170)
    const = DoubleByte(100)

    Z80TestHandler(
        # Register: (before, after)
        {
            "A": (a.value, a.value ^ const.value),   
            "PC": (0, 1),
        },
        # Flag: (before, after)
        {
            SIGN_FLAG: (0, 1),
            HALF_CARRY_FLAG: (1, 0),
            PARITY_OVERFLOW_FLAG: (0, 0),
            ADD_SUBTRACT_FLAG: (1, 0),
            ZERO_FLAG: (1, 0),
            CARRY_FLAG: (1, 0)
        },
        # Memory location: (before, after)
        {
            0: (const.value, const.value),
        },
        # Ports: (before, after)
        {},
        # Command
        "xor *"
    )

def test_daa_add_h():
    # Constant attributes - value, low, high
    a = DoubleByte(12)

    Z80TestHandler(
        # Register: (before, after)
        {
            "A": (a.value, a.value + 6),   
        },
        # Flag: (before, after)
        {
            HALF_CARRY_FLAG: (1, 1),
            ADD_SUBTRACT_FLAG: (0, 0),
        },
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {},
        # Command
        "daa"
    )


def test_daa_add_c():
    # Constant attributes - value, low, high
    a = DoubleByte(18)

    Z80TestHandler(
        # Register: (before, after)
        {
            "A": (a.value, a.value + 96),   
        },
        # Flag: (before, after)
        {
            CARRY_FLAG: (1, 1),
            ADD_SUBTRACT_FLAG: (0, 0),
            PARITY_OVERFLOW_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {},
        # Command
        "daa"
    )


def test_ret():
    # Constant attributes - value, low, high
    sp = DoubleByte(1000)
    low = DoubleByte(100)
    high = DoubleByte(2)

    Z80TestHandler(
        # Register: (before, after)
        {
            "SP": (sp.value, sp.value + 2),   
            "PC": (0, 612),
        },
        # Flag: (before, after)
        {},
        # Memory location: (before, after)
        {
            sp.value: (low.value, low.value),
            sp.value + 1: (high.value, high.value),
        },
        # Ports: (before, after)
        {},
        # Command
        "ret"
    )

def test_ret_m_1():
    # Constant attributes - value, low, high
    sp = DoubleByte(1000)
    low = DoubleByte(100)
    high = DoubleByte(2)

    Z80TestHandler(
        # Register: (before, after)
        {
            "SP": (sp.value, sp.value + 2),   
            "PC": (0, 612),
        },
        # Flag: (before, after)
        {SIGN_FLAG: (1,1)},
        # Memory location: (before, after)
        {
            sp.value: (low.value, low.value),
            sp.value + 1: (high.value, high.value),
        },
        # Ports: (before, after)
        {},
        # Command
        "ret m"
    )

def test_ret_m_0():
    # Constant attributes - value, low, high

    Z80TestHandler(
        # Register: (before, after)
        {},
        # Flag: (before, after)
        {SIGN_FLAG: (0,0)},
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {},
        # Command
        "ret m"
    )

def test_bit_0_d():
    # 'bit 0,d', 'Tests bit 0 of d.'
    
    # Constant attributes - value, low, high

    Z80TestHandler(
        # Register: (before, after)
        {
            "D": (127, 127),   
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0,1),
            HALF_CARRY_FLAG: (0,1),
            ADD_SUBTRACT_FLAG: (1,0),
        },
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {},
        # Command
        "bit 0,d"
    )

def test_bit_ix():
    # Tests bit 5 of the memory location pointed to by ix plus *.'
    
    # Constant attributes - value, low, high

    Z80TestHandler(
        # Register: (before, after)
        {
            "IX": (1000, 1000),
            "PC": (0, 1)   
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (1,0),
            HALF_CARRY_FLAG: (0,1),
            ADD_SUBTRACT_FLAG: (1,0),
        },
        # Memory location: (before, after)
        { 
            0: (20, 20),
            1020: (4, 4)
        },
        # Ports: (before, after)
        {},
        # Command
        "bit 5,(ix+*)"
    )

def test_in_a_val():
    # in a,(*), a byte from port * is written to a
    
    # Constant attributes - value, low, high
    port = DoubleByte(150)

    Z80TestHandler(
        # Register: (before, after)
        {
            "A": (0, 99),
            "PC": (0, 1)   
        },
        # Flag: (before, after)
        {},
        # Memory location: (before, after)
        { 
            0: (port.value, port.value),
        },
        # Ports: (before, after)
        {
            port.value: (99, 99)
        },
        # Command
        "in a,(*)"
    )

def test_in_e_c():
    # in e,(c), a byte from port (c) is written to e
    
    # Constant attributes - value, low, high
    c = DoubleByte(5000)
    port = DoubleByte(150)
    input = DoubleByte(99)

    Z80TestHandler(
        # Register: (before, after)
        {
            "E": (0, input.value),
            "C": (port.value, port.value)
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (1,0),
            HALF_CARRY_FLAG: (1,0),
            ADD_SUBTRACT_FLAG: (1,0),
        },
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {
            port.value: (input.value, input.value)
        },
        # Command
        "in e,(c)"
    )

def test_in_c():
    # in (c) - just changes flags
    
    # Constant attributes - value, low, high
    port = DoubleByte(150)
    input = DoubleByte(99)

    Z80TestHandler(
        # Register: (before, after)
        {
            "C": (port.value, port.value)
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (1,0),
            HALF_CARRY_FLAG: (1,0),
            ADD_SUBTRACT_FLAG: (1,0),
        },
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {
            port.value: (input.value, input.value)
        },
        # Command
        "in (c)"
    )

def test_out_val_a():
    # out (*),a', 'The value of a is written to port *
    
    # Constant attributes - value, low, high
    port = DoubleByte(150)

    Z80TestHandler(
        # Register: (before, after)
        {
            "A": (99, 99),
            "PC": (0, 1)   
        },
        # Flag: (before, after)
        {},
        # Memory location: (before, after)
        { 
            0: (port.value, port.value),
        },
        # Ports: (before, after)
        {
            port.value: (0, 99)
        },
        # Command
        "out (*),a"
    )

def test_out_c_h():
    # out (c),h', 'The value of h is written to port (c)
    
    # Constant attributes - value, low, high
    h = DoubleByte(99)
    port = DoubleByte(150)

    Z80TestHandler(
        # Register: (before, after)
        {
            "C": (port.value, port.value),
            "H": (h.value, h.value),
        },
        # Flag: (before, after)
        {},
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {
            port.value: (0, h.value)
        },
        # Command
        "out (c),h"
    )

def test_outi():
    # A byte from the memory location pointed to by hl is written to port c. 
    # Then hl is incremented and b is decremented.
    
    # Constant attributes - value, low, high
    hl = DoubleByte(1000)
    b = DoubleByte(10)
    port = DoubleByte(150)
    out = DoubleByte(99)

    Z80TestHandler(
        # Register: (before, after)
        {
            "B": (b.value, b.value - 1),
            "C": (port.value, port.value),
            "HL": (hl.value, hl.value + 1),
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (1, 0),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {
            hl.value: (out.value, out.value)
        },
        # Ports: (before, after)
        {
            port.value: (0, out.value)
        },
        # Command
        "outi"
    )

def test_outi_zero_flag_set():
    # A byte from the memory location pointed to by hl is written to port c. 
    # Then hl is incremented and b is decremented.
    
    # Constant attributes - value, low, high
    hl = DoubleByte(1000)
    b = DoubleByte(2)
    port = DoubleByte(150)
    out = DoubleByte(99)

    Z80TestHandler(
        # Register: (before, after)
        {
            "B": (b.value, b.value - 1),
            "C": (port.value, port.value),
            "HL": (hl.value, hl.value + 1),
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0, 1),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {
            hl.value: (out.value, out.value)
        },
        # Ports: (before, after)
        {
            port.value: (0, out.value)
        },
        # Command
        "outi"
    )

def test_otir():
    # A byte from the memory location pointed to by hl is written to port c. Then hl is incremented and b is decremented. If b is not zero, this operation is repeated. Interrupts can trigger while this instruction is processing
    
    # Constant attributes - value, low, high
    hl = DoubleByte(1000)
    b = DoubleByte(3)
    port = DoubleByte(150)
    out = DoubleByte(99)

    Z80TestHandler(
        # Register: (before, after)
        {
            "B": (b.value, 0),
            "C": (port.value, port.value),
            "HL": (hl.value, hl.value + b.value),
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0, 1),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {
            hl.value: (out.value, out.value),
            hl.value + 1: (out.value + 1, out.value + 1),
            hl.value + 2: (out.value + 2, out.value + 2),
        },
        # Ports: (before, after)
        {
            port.value: (0, out.value + b.value - 1)
        },
        # Command
        "otir"
    )

def test_outd():
    # A byte from the memory location pointed to by hl is written to port c. 
    # Then hl is decremented and b is decremented.
    
    # Constant attributes - value, low, high
    hl = DoubleByte(1000)
    b = DoubleByte(10)
    port = DoubleByte(150)
    out = DoubleByte(99)

    Z80TestHandler(
        # Register: (before, after)
        {
            "B": (b.value, b.value - 1),
            "C": (port.value, port.value),
            "HL": (hl.value, hl.value - 1),
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (1, 0),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {
            hl.value: (out.value, out.value)
        },
        # Ports: (before, after)
        {
            port.value: (0, out.value)
        },
        # Command
        "outd"
    )

def test_otdr():
    # A byte from the memory location pointed to by hl is written to port c. Then hl and b are decremented. If b is not zero, this operation is repeated. Interrupts can trigger while this instruction is processing.
    
    # Constant attributes - value, low, high
    hl = DoubleByte(1000)
    b = DoubleByte(3)
    port = DoubleByte(150)
    out = DoubleByte(99)

    Z80TestHandler(
        # Register: (before, after)
        {
            "B": (b.value, 0),
            "C": (port.value, port.value),
            "HL": (hl.value, hl.value - b.value),
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0, 1),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {
            hl.value: (out.value, out.value),
            hl.value - 1: (out.value + 1, out.value + 1),
            hl.value - 2: (out.value + 2, out.value + 2),
        },
        # Ports: (before, after)
        {
            port.value: (0, out.value + b.value - 1)
        },
        # Command
        "otdr"
    )

def test_ini():
    # A byte from port c is written to the memory location pointed to by hl. Then hl is incremented and b is decremented.
    
    # Constant attributes - value, low, high
    hl = DoubleByte(1000)
    b = DoubleByte(10)
    port = DoubleByte(150)
    in_ = DoubleByte(99)

    Z80TestHandler(
        # Register: (before, after)
        {
            "B": (b.value, b.value - 1),
            "C": (port.value, port.value),
            "HL": (hl.value, hl.value + 1),
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (1, 0),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {
            hl.value: (0, in_.value)
        },
        # Ports: (before, after)
        {
            port.value: (in_.value, in_.value)
        },
        # Command
        "ini"
    )

def test_ind():
    # A byte from port c is written to the memory location pointed to by hl. Then hl and b are decremented.
    
    # Constant attributes - value, low, high
    hl = DoubleByte(1000)
    b = DoubleByte(10)
    port = DoubleByte(150)
    in_ = DoubleByte(99)

    Z80TestHandler(
        # Register: (before, after)
        {
            "B": (b.value, b.value - 1),
            "C": (port.value, port.value),
            "HL": (hl.value, hl.value - 1),
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (1, 0),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {
            hl.value: (0, in_.value)
        },
        # Ports: (before, after)
        {
            port.value: (in_.value, in_.value)
        },
        # Command
        "ind"
    )

def test_inir():
    # A byte from port c is written to the memory location pointed to by hl. Then hl is incremented and b is decremented. If b is not zero, this operation is repeated. Interrupts can trigger while this instruction is processing.
    
    # Constant attributes - value, low, high
    hl = DoubleByte(1000)
    b = DoubleByte(3)
    port = DoubleByte(150)
    in_ = DoubleByte(99)

    Z80TestHandler(
        # Register: (before, after)
        {
            "B": (b.value, 0),
            "C": (port.value, port.value),
            "HL": (hl.value, hl.value + b.value),
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0, 1),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {
            hl.value: (0, in_.value),
            hl.value + 1: (0, in_.value),
            hl.value + 2: (0, in_.value),
        },
        # Ports: (before, after)
        {
            port.value: (in_.value, in_.value)
        },
        # Command
        "inir"
    )

def test_indr():
    # A byte from port c is written to the memory location pointed to by hl. Then hl and b are decremented. If b is not zero, this operation is repeated. Interrupts can trigger while this instruction is processing.
    
    # Constant attributes - value, low, high
    hl = DoubleByte(1000)
    b = DoubleByte(3)
    port = DoubleByte(150)
    in_ = DoubleByte(99)

    Z80TestHandler(
        # Register: (before, after)
        {
            "B": (b.value, 0),
            "C": (port.value, port.value),
            "HL": (hl.value, hl.value - b.value),
        },
        # Flag: (before, after)
        {
            ZERO_FLAG: (0, 1),
            ADD_SUBTRACT_FLAG: (0, 1),
        },
        # Memory location: (before, after)
        {
            hl.value: (0, in_.value),
            hl.value - 1: (0, in_.value),
            hl.value - 2: (0, in_.value),
        },
        # Ports: (before, after)
        {
            port.value: (in_.value, in_.value)
        },
        # Command
        "indr"
    )

def test_rl():
    # The contents of e are rotated left one bit position. The contents of bit 7
    # are copied to the carry flag and the previous contents of the carry flag 
    # are copied to bit 0

    # Constant attributes - value, low, high
    e = DoubleByte(99)  # [0, 1, 1, 0, 0, 0, 1, 1]
                        # [1, 1, 0, 0, 0, 1, 1, 1]

    Z80TestHandler(
        # Register: (before, after)
        {
            "E": (e.value, 199),
        },
        # Flag: (before, after)
        {
            SIGN_FLAG: (0, 1),
            CARRY_FLAG: (1, 0),
            HALF_CARRY_FLAG: (1, 0),
            ADD_SUBTRACT_FLAG: (1, 0),
        },
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {},
        # Command
        "rl e"
    )

def test_rla():
    # The contents of the Accumulator (Register A) are rotated left 1 bit position through the
    # Carry flag. The previous contents of the Carry flag are copied to bit 0. Bit 0 is the 
    # least significant bit.

    # Constant attributes - value, low, high
    a = DoubleByte(99)  # [0, 1, 1, 0, 0, 0, 1, 1]
                        # [1, 1, 0, 0, 0, 1, 1, 1]

    Z80TestHandler(
        # Register: (before, after)
        {
            "A": (a.value, 199),
        },
        # Flag: (before, after)
        {
            SIGN_FLAG: (0, 0),
            CARRY_FLAG: (1, 0),
            HALF_CARRY_FLAG: (1, 0),
            ADD_SUBTRACT_FLAG: (1, 0),
        },
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {},
        # Command
        "rla"
    )

def test_rlc():
    # The contents of register r are rotated left 1 bit position. The contents of bit 7 are copied to
    # the Carry flag and also to bit 0. 

    # Constant attributes - value, low, high
    c = DoubleByte(99)  # [0, 1, 1, 0, 0, 0, 1, 1]
                        # [1, 1, 0, 0, 0, 1, 1, 0]

    Z80TestHandler(
        # Register: (before, after)
        {
            "C": (c.value, 198),
        },
        # Flag: (before, after)
        {
            SIGN_FLAG: (0, 1),
            CARRY_FLAG: (1, 0),
            HALF_CARRY_FLAG: (1, 0),
            ADD_SUBTRACT_FLAG: (1, 0),
        },
        # Memory location: (before, after)
        {},
        # Ports: (before, after)
        {},
        # Command
        "rlc c"
    )

'''


ccf
di
ei
halt
im

nop

res


rlc p227
rlca
rld
rr
rra
rrc
rrca
rrd
rst
scf
set
sla
sll
sra
srl


interrupt gubbins
-----------------
reti
retn
'''

