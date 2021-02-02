import pytest

from z80 import Z80
from base import (
    Component, Memory, DoubleComponent, SIGN_FLAG, ZERO_FLAG, HALF_CARRY_FLAG, PARITY_OVERFLOW_FLAG, ADD_SUBTRACT_FLAG, CARRY_FLAG,
)

def test_set_flag():
    flag_register = Component("F")

    flag_register.set_flag(SIGN_FLAG)
    assert flag_register.get_contents() == 128

    flag_register.set_flag(ZERO_FLAG)
    assert flag_register.get_contents() == 192

    flag_register.set_flag(HALF_CARRY_FLAG)
    assert flag_register.get_contents() == 208
    
    flag_register.set_flag(PARITY_OVERFLOW_FLAG)
    assert flag_register.get_contents() == 212

    flag_register.set_flag(ADD_SUBTRACT_FLAG)
    assert flag_register.get_contents() == 214

    flag_register.set_flag(CARRY_FLAG)
    assert flag_register.get_contents() == 215


def test_reset_flag():
    flag_register = Component("F")
    flag_register.set_contents(255)

    flag_register.reset_flag(SIGN_FLAG)
    assert flag_register.get_contents() == 127

    flag_register.reset_flag(ZERO_FLAG)
    assert flag_register.get_contents() == 63

    flag_register.reset_flag(HALF_CARRY_FLAG)
    assert flag_register.get_contents() == 47
    
    flag_register.reset_flag(PARITY_OVERFLOW_FLAG)
    assert flag_register.get_contents() == 43

    flag_register.reset_flag(ADD_SUBTRACT_FLAG)
    assert flag_register.get_contents() == 41

    flag_register.reset_flag(CARRY_FLAG)
    assert flag_register.get_contents() == 40


def test_addition_with_flags():
    register =  Component("A")
    assert (3, False, False) == register.addition_with_flags(1,2)
    assert (1, True, True) == register.addition_with_flags(255,2)
    assert (0, True, False) == register.addition_with_flags(128,128)
    assert (17, False, True) == register.addition_with_flags(15,2)


def test_subtraction_with_flags():
    register =  Component("A")
    assert (3, False, False) == register.subtraction_with_flags(5,2)
    assert (255, True, True) == register.subtraction_with_flags(1,2)
    assert (0, False, False) == register.subtraction_with_flags(128,128)
    assert (255, True, True) == register.subtraction_with_flags(128,129)
    assert (51, True, False) == register.subtraction_with_flags(15,220)
    assert (47, True, True) == register.subtraction_with_flags(14,223)
