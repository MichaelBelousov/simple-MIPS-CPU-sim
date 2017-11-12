from time import time
from binint import Binint as Bint
from regis import Regis, makeregispile

# NOTE: Abstract base class? (import ABC)
class Component:
    def __init__(self):
        self.outs = {}
        self.ins = {}
    def tick(self):
        pass
        # raise NotImplementedError
    def bind(self, _in, comp, _out, mask=(0,32)):
        """bind another comp's output to this comps input"""
        i = mask[0]
        j = mask[1]
        def cb():
            res = Bint(0)
            if comp.outs[_out] is not None:
                res = Bint(comp.outs[_out][i:j], pad=j-i)
            return res
        self.ins[_in] = cb

class ClockedComponent(Component):
    def __init__(self, clock):
        super().__init__()
        self._lastclock = False
        self.clock = clock
    def tick(self):
        super().tick()
        if self.clock.outs['clock'] != self._lastclock:
            self.onupclock()
            self._lastclock = self.clock.outs['clock']
    def onupclock(self):
        raise NotImplementedError

class PC(ClockedComponent):
    def __init__(self, initval, clock):
        super().__init__(clock)
        self.ins['in'] = 0
        self.outs['out'] = 0
        self.reg = Regis(initval)
    def onupclock(self):
        self.reg.val = self.ins['in']()
        self.outs['out'] = self.reg.val

class Memory(Component, dict):
    def __init__(self):
        Component.__init__(self)
        self.ins['addr'] = Bint(0)
        self.ins['write'] = Bint(0)
        self.ins['write_cont'] = Bint(0)
        self.ins['read_cont'] = Bint(0)
        self.outs['read'] = Bint(0)  # TODO: change to out for consistency
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.get(key,0)
        else: 
            raise TypeError('Memory Component takes integer address indices')
    def tick(self):
        Component.tick(self)
        addr = self.ins['addr']()
        write = self.ins['write']()
        do_write = self.ins['write_cont']
        do_read = self.ins['read_cont']
        if do_read:
            self.outs['read'] = Bint(self[addr])
        elif do_write:
            self[addr] = write

class Clock(Component):
    def __init__(self, inittime=time()):
        super().__init__()
        self.inittime = inittime
        self.period = 1  # in seconds
        self.outs['clock'] = False
    def tick(self):
        super().tick()
        per = self.period
        self.outs['clock'] = Bint((self.inittime - time()) % per >= per/2)

class Control(Component):
    def __init__(self):
        super().__init__()
        self.ins['in'] = None
        self.setouts(0,0,0,0,0,0,0,0,0)
    def setouts(self, RegDst, Jump, Branch, MemRead, MemtoReg, ALUOp,
                MemWrite, ALUSrc, RegWrite):
            self.outs['RegDst']     = Bint(RegDst)
            self.outs['Jump']       = Bint(Jump)
            self.outs['Branch']     = Bint(Branch)
            self.outs['MemRead']    = Bint(MemRead)
            self.outs['MemtoReg']   = Bint(MemtoReg)
            self.outs['ALUOp']      = Bint(ALUOp)  # 2 bits
            self.outs['MemWrite']   = Bint(MemWrite)
            self.outs['ALUSrc']     = Bint(ALUSrc)
            self.outs['RegWrite']   = Bint(RegWrite)
    def tick(self):
        super().tick()
        op = self.ins['in']()[0:6]
        if op == 0b000000:  # R-format
            self.setouts(1,0,0,1,0,0b10,0,1,0)
        elif op == 0b001000:  #addi
            self.setouts(0,0,0,0,0,0b00,0,0,0)  # TODO: implement
        elif op == 0b100011:  #lw
            self.setouts(0,1,1,1,1,0b00,0,0,0)
        elif op == 0b101011:  #sw
            self.setouts(0,1,0,0,0,0b00,0,0,0)
        elif op == 0b000100:  #beq
            self.setouts(0,0,0,0,0,0b01,1,0,1)
        elif op == 0b000100:  #j
            self.setouts(0,0,0,0,0,0b00,0,0,0)  # TODO: implement
        else:
            raise Exception('unknown opcode, {}'.format(op))
        
class ALUControl(Component):
    def __init__(self):
        super().__init__()
        self.ins['ALUOp'] = None
        self.ins['funct'] = None
        self.outs['ALUOp'] = None
    def tick(self):
        super().tick()
        funct = self.ins['funct']()[26:]
        aluop0 = self.ins['ALUop']()[0]
        aluop1 = self.ins['ALUop']()[1]
        if not (aluop0 or aluop1):
            self.outs['ALUOp'] = Bint(0b0010, pad=4)
        elif aluop0 == 1:
            self.outs['ALUOp'] = Bint(0b0110, pad=4)
        elif aluop1 == 1:  # add
            if funct[2:] == 0b0000:
                self.outs['ALUOp'] = Bint(0b0110, pad=4)
            elif funct[2:] == 0b0010:
                self.outs['ALUOp'] = Bint(0b0000, pad=4)
            elif funct[2:] == 0b0101:
                self.outs['ALUOp'] = Bint(0b0001, pad=4)
            elif funct[2:] == 0b1010:
                self.outs['ALUOp'] = Bint(0b0111, pard=4)

class Multiplexer(Component):
    def __init__(self):
        super().__init__()
        self.ins['control'] = None
        self.ins['in_1'] = None
        self.ins['in_2'] = None
        self.outs['out'] = None
    def tick(self):
        super().tick()
        switch = bool(self.ins['control']())
        self.outs['out'] = self.ins['in_2']() if switch else self.ins['in_1']()

class ALU(Component):
    def __init__(self):
        super().__init__()
        self.ins['control'] = None
        self.ins['in_1'] = None
        self.ins['in_2'] = None
        self.outs['zero'] = None
        self.outs['out'] = None
    def tick(self):
        super().tick()
        cont = self.ins['control']()
        a = self.ins['in_1']
        b = self.ins['in_2']
        if cont == 0b0000:  # and
            self.outs['out'] = a & b
        elif cont == 0b0001:  # or
            self.outs['out'] = a | b
        elif cont == 0b0010:  # add
            self.outs['out'] = a + b
        elif cont == 0b0110:  # sub
            self.outs['out'] = a - b
        elif cont == 0b0111:  # slt
            self.outs['out'] = Bint(1) if a < b else Bint(0)
        self.outs['zero'] = Bint(1) if not self.outs['out'] else Bint(0)

class SignExtend(Component):
    def __init__(self):
        super().__init__()
        self.ins['in'] = None
        self.outs['out'] = None
    def tick(self):
        super().tick()
        in_ = self.ins['in']()
        self.outs['out'] = Bint(in_, pad=32)

class ShiftLeftTwo(Component):
    def __init__(self):
        super().__init__()
        self.ins['in'] = None
        self.outs['out'] = None
    def tick(self):
        super().tick()
        in_ = self.ins['in']()
        self.outs['out'] = Bint(in_ << 2, pad=32)

class AddFour(Component):
    def __init__(self):
        super().__init__()
        self.ins['in'] = None
        self.outs['out'] = None
    def tick(self):
        super().tick()
        in_ = self.ins['in']()
        self.outs['out'] = Bint(in_ + 4)

class And(Component):
    def __init__(self):
        super().__init__()
        self.ins['in_1'] = None
        self.ins['in_2'] = None
        self.outs['out'] = None
    def tick(self):
        super().tick()
        in1 = self.ins['in_1']()
        in2 = self.ins['in_2']()
        self.outs['out'] = Bint(in1 & in2)

class RegisterFile(Component):
    def __init__(self):
        super().__init__()
        self.regs = makeregispile()
        self.ins['RegWrite'] = None  # Control->RegWrite
        self.ins['read_reg_1'] = None
        self.ins['read_reg_2'] = None
        self.ins['write_reg'] = None  # which register to write to
        self.ins['write_data'] = None  # data to write to write register
        self.outs['read_data_1'] = None
        self.outs['read_data_2'] = None
    def tick(self):
        super().tick()
        do_write = self.ins['RegWrite']()
        read1 = self.ins['read_reg_1']()
        read2 = self.ins['read_reg_2']()
        write = self.ins['write_reg']()
        writedata = self.ins['write_data']()
        self.outs['read_data_1'] = self.regs[str(read1)]
        self.outs['read_data_2'] = self.regs[str(read2)]
        if do_write:
            self.regs[str(write)] = writedata

class Inspector(ClockedComponent):
    def __init__(self, clock, comps):
        super().__init__(clock)
        self.comps = comps
    def onupclock(self):
        print('CLOCK')        
