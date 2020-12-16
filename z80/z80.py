from base import Component, Memory, InstructionBase, DoubleComponent


class CPUTest(InstructionBase):

    MEMORY_SIZE = 256 * 256

    def __init__(self):
        self.memory = Memory(self.MEMORY_SIZE)
        self._define_registers()

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
