from comps import *
Mux = Multiplexer  # Multiplexer class alias
from regis import Regis 
        
class CPU:
    def __init__(self):
        self.comps = []
    def run(self):
        while True:
            self.tick()
    def tick(self):
        for c in self.comps:
            c.tick()
        self.stat()
    def loadinstr(self, instrs=[]):
        """load a list of instructions into the CPU
        instruction memory."""
        pass
    def stat(self):
        """determine stats of the system, e.g. cycle change, curr instr"""
        pass

class MIPSSingleCycleCPU(CPU):
    def __init__(self):
        super().__init__()
        # construct components
        clock = Clock()
        pc = PC(0, clock)
        alu = ALU()
        instrmem = Memory()
        self.instrmem = instrmem
        datamem = Memory()
        regisfile = RegisterFile()
        control = Control()
        alucont = ALUControl()
        branchalu = ALU()
        signext = SignExtend()
        writeregmux = Mux()
        alumux = Mux()
        writeregdatamux = Mux()
        branchmux = Mux()
        jumpmux = Mux()
        branchand = And()
        pcaddfour = AddFour()
        shiftl2 = ShiftLeftTwo()
        self.comps = [clock,pc,alu,instrmem,datamem,regisfile,control,alucont,branchalu,
                        signext,writeregmux,alumux,writeregdatamux,branchmux,jumpmux,
                        branchand,pcaddfour,shiftl2]
        # connect component
        pc.bind('in', jumpmux, 'out')
        alu.bind('in_1', regisfile, 'read_data_1')
        alu.bind('in_2', alumux, 'out', mask=(6,10))
        alu.bind('control', alucont, 'ALUop')
        instrmem.bind('addr', pc, 'out')
        instrmem.ins['write_cont'] = 0
        instrmem.ins['read_cont'] = 1
        datamem.bind('addr', pc, 'out')
        datamem.bind('write', pc, 'out')
        datamem.bind('write_cont', control, 'MemWrite')
        datamem.bind('read_cont', control, 'MemRead')
        regisfile.bind('RegWrite', control, 'RegWrite')
        regisfile.bind('read_reg_1', instrmem, 'read', mask=(6,11))
        regisfile.bind('read_reg_2', instrmem, 'read', mask=(11,16))
        regisfile.bind('write_reg', writeregmux, 'out', mask=(27,32))
        regisfile.bind('write_data', writeregdatamux, 'out')
        control.bind('in', instrmem, 'read', mask=(0,6))
        alucont.bind('ALUOp', control, 'ALUOp')
        alucont.bind('funct', instrmem, 'ALUOp', mask=(27,32))
        branchalu.bind('in_1', pcaddfour, 'out')
        branchalu.bind('in_2', shiftl2, 'out')
        branchalu.ins['control'] = bin(0b0010)
        signext.bind('in', instrmem, 'read', mask=(16,32))
        writeregmux.bind('in_1', instrmem, 'read', mask=(11,16))
        writeregmux.bind('in_2', instrmem, 'read', mask=(16,21))
        writeregmux.bind('control', control, 'RegDst')
        alumux.bind('in_1', regisfile, 'read_data_2') 
        alumux.bind('in_2', signext, 'out') 
        alumux.bind('control', control, 'ALUSrc')
        writeregdatamux.bind('in_1', alu, 'out')  # flipped in the diagram
        writeregdatamux.bind('in_2', datamem, 'read') 
        writeregdatamux.bind('control', control, 'MemtoReg')
        branchmux.bind('in_1', pcaddfour, 'out') 
        branchmux.bind('in_2', branchalu, 'out') 
        branchmux.bind('control', branchand, 'out')
        jumpmux.bind('in_1', branchmux, 'out')  # flipped in the diagram
        jumpmux.bind('in_2', shiftl2, 'out')
        jumpmux.bind('control', control, 'Jump')
        branchand.bind('in_1', control, 'Branch')
        branchand.bind('in_2', alu, 'zero')
        pcaddfour.bind('in', pc, 'out')
        shiftl2.bind('in', instrmem, 'read', mask=(6,32))
        # introspective component
        self.comps.append(Inspector(clock, self.comps))
    def loadinstr(self, instrs=[]):
        for i in range(0, len(instrs)):
            self.instrmem[i] = instrs[i]
    def stat(self):
        pass
