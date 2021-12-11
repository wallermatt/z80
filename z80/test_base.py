import pytest

from z80 import Z80
from base import (
    Component, Memory, DoubleComponent, SIGN_FLAG, ZERO_FLAG, HALF_CARRY_FLAG, PARITY_OVERFLOW_FLAG, ADD_SUBTRACT_FLAG, CARRY_FLAG,
    FLAG_POSITIONS
)

def test_set_flag():
    flag_register = Component("F")

    flag_register.set_flag(SIGN_FLAG)
    assert flag_register.convert_contents_to_bit_list() == [1, 0, 0, 0, 0, 0, 0, 0]

    flag_register.set_flag(ZERO_FLAG)
    assert flag_register.convert_contents_to_bit_list() == [1, 1, 0, 0, 0, 0, 0, 0]

    flag_register.set_flag(HALF_CARRY_FLAG)
    assert flag_register.convert_contents_to_bit_list() == [1, 1, 0, 1, 0, 0, 0, 0]
    
    flag_register.set_flag(PARITY_OVERFLOW_FLAG)
    assert flag_register.convert_contents_to_bit_list() == [1, 1, 0, 1, 0, 1, 0, 0]

    flag_register.set_flag(ADD_SUBTRACT_FLAG)
    assert flag_register.convert_contents_to_bit_list() == [1, 1, 0, 1, 0, 1, 1, 0]

    flag_register.set_flag(CARRY_FLAG)
    assert flag_register.convert_contents_to_bit_list() == [1, 1, 0, 1, 0, 1, 1, 1]


def test_reset_flag():
    flag_register = Component("F")
    flag_register.set_contents(255)

    flag_register.reset_flag(SIGN_FLAG)
    assert flag_register.convert_contents_to_bit_list() == [0, 1, 1, 1, 1, 1, 1, 1]

    flag_register.reset_flag(ZERO_FLAG)
    assert flag_register.convert_contents_to_bit_list() == [0, 0, 1, 1, 1, 1, 1, 1]

    flag_register.reset_flag(HALF_CARRY_FLAG)
    assert flag_register.convert_contents_to_bit_list() == [0, 0, 1, 0, 1, 1, 1, 1]
    
    flag_register.reset_flag(PARITY_OVERFLOW_FLAG)
    assert flag_register.convert_contents_to_bit_list() == [0, 0, 1, 0, 1, 0, 1, 1]
    
    flag_register.reset_flag(ADD_SUBTRACT_FLAG)
    assert flag_register.convert_contents_to_bit_list() == [0, 0, 1, 0, 1, 0, 0, 1]

    flag_register.reset_flag(CARRY_FLAG)
    assert flag_register.convert_contents_to_bit_list() == [0, 0, 1, 0, 1, 0, 0, 0]


def test_addition_with_flags():
    register =  Component("A")

    register.set_contents(1)
    register.addition_with_flags(2)
    assert register.get_contents() == 3
    assert register.potential_flags[ADD_SUBTRACT_FLAG] == False
    assert register.potential_flags[HALF_CARRY_FLAG] == False
    assert register.potential_flags[CARRY_FLAG] == False
    assert register.potential_flags[PARITY_OVERFLOW_FLAG] == False

    register.set_contents(255)
    register.addition_with_flags(2)
    assert register.get_contents() == 1
    assert register.potential_flags[ADD_SUBTRACT_FLAG] == False
    assert register.potential_flags[HALF_CARRY_FLAG] == True
    assert register.potential_flags[CARRY_FLAG] == True
    assert register.potential_flags[PARITY_OVERFLOW_FLAG] == False

    register.set_contents(128)
    register.addition_with_flags(128)
    assert register.get_contents() == 0
    assert register.potential_flags[ADD_SUBTRACT_FLAG] == False
    assert register.potential_flags[HALF_CARRY_FLAG] == False
    assert register.potential_flags[CARRY_FLAG] == True
    assert register.potential_flags[PARITY_OVERFLOW_FLAG] == True

    register.set_contents(15)
    register.addition_with_flags(2)
    assert register.get_contents() == 17
    assert register.potential_flags[ADD_SUBTRACT_FLAG] == False
    assert register.potential_flags[HALF_CARRY_FLAG] == True
    assert register.potential_flags[CARRY_FLAG] == False
    assert register.potential_flags[PARITY_OVERFLOW_FLAG] == False


def test_subtraction_with_flags():
    register =  Component("A")
    register.set_contents(5)
    register.subtraction_with_flags(2)
    assert register.get_contents() == 3
    assert register.potential_flags[ADD_SUBTRACT_FLAG] == True
    assert register.potential_flags[HALF_CARRY_FLAG] == False
    assert register.potential_flags[CARRY_FLAG] == False
    assert register.potential_flags[PARITY_OVERFLOW_FLAG] == False

    register.set_contents(1)
    register.subtraction_with_flags(2)
    assert register.get_contents() == 255
    assert register.potential_flags[ADD_SUBTRACT_FLAG] == True
    assert register.potential_flags[HALF_CARRY_FLAG] == True
    assert register.potential_flags[CARRY_FLAG] == True
    assert register.potential_flags[PARITY_OVERFLOW_FLAG] == False

    register.set_contents(128)
    register.subtraction_with_flags(128)
    assert register.get_contents() == 0
    assert register.potential_flags[ADD_SUBTRACT_FLAG] == True
    assert register.potential_flags[HALF_CARRY_FLAG] == False
    assert register.potential_flags[CARRY_FLAG] == False
    assert register.potential_flags[PARITY_OVERFLOW_FLAG] == False

    register.set_contents(128)
    register.subtraction_with_flags(129)
    assert register.get_contents() == 255
    assert register.potential_flags[ADD_SUBTRACT_FLAG] == True
    assert register.potential_flags[HALF_CARRY_FLAG] == True
    assert register.potential_flags[CARRY_FLAG] == True
    assert register.potential_flags[PARITY_OVERFLOW_FLAG] == False

    register.set_contents(15)
    register.subtraction_with_flags(220)
    assert register.get_contents() == 51
    assert register.potential_flags[ADD_SUBTRACT_FLAG] == True
    assert register.potential_flags[HALF_CARRY_FLAG] == False
    assert register.potential_flags[CARRY_FLAG] == True
    assert register.potential_flags[PARITY_OVERFLOW_FLAG] == True

    register.set_contents(14)
    register.subtraction_with_flags(223)
    assert register.get_contents() == 47
    assert register.potential_flags[ADD_SUBTRACT_FLAG] == True
    assert register.potential_flags[HALF_CARRY_FLAG] == True
    assert register.potential_flags[CARRY_FLAG] == True
    assert register.potential_flags[PARITY_OVERFLOW_FLAG] == True


def test_set_potential_flags():
    register =  Component("A")
    register.set_contents(0)
    register.set_potential_flags()
    assert register.potential_flags[SIGN_FLAG] == False
    assert register.potential_flags[ZERO_FLAG] == True

    register.set_contents(10)
    register.set_potential_flags()
    assert register.potential_flags[SIGN_FLAG] == False
    assert register.potential_flags[ZERO_FLAG] == False

    register.set_contents(255)
    register.set_potential_flags()
    assert register.potential_flags[SIGN_FLAG] == True
    assert register.potential_flags[ZERO_FLAG] == False
