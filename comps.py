from time import time
from binint import Binint as Bint
from regis import Regis, makeregispile
from pprint import pprint, pformat
import utilities

# TODO: add repr to all components

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
        self.ins['in'] = Bint(initval)
        self.outs['out'] = Bint(initval)
        self.reg = Regis(Bint(initval))
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
        if hasattr(key, '__int__'):
            return self.get(int(key),0)
        else: 
            # XXX: KeyError?
            raise TypeError('Memory Component takes integer-compatible indices')
    def tick(self):
        Component.tick(self)
        addr = self.ins['addr']()
        write = self.ins['write']()
        do_write = self.ins['write_cont']()
        do_read = self.ins['read_cont']()
        if do_read:  # this is analagous to only binary words
            self.outs['read'] = self[addr]
        if do_write:
            self[addr] = write
    def __getitem__(self, loc):  # words
        loc = Bint(loc)
        item = ''  # TODO: use Bint.append()
        item += str(dict.get(self, loc, Bint(0,pad=8)))
        item += str(dict.get(self, loc+1, Bint(0,pad=8)))
        item += str(dict.get(self, loc+2, Bint(0, pad=8)))
        item += str(dict.get(self, loc+3, Bint(0, pad=8)))
        return Bint(item)
    def __setitem__(self, loc, val):  # words
        loc = Bint(loc)
        dict.__setitem__(self, loc, val[0:8])
        dict.__setitem__(self, loc+1, val[8:16])
        dict.__setitem__(self, loc+2, val[16:24])
        dict.__setitem__(self, loc+3, val[24:32])

class Clock(Component):
    def __init__(self, inittime=time()):
        super().__init__()
        self.inittime = inittime
        self.period = 1  # in seconds
        self.outs['clock'] = Bint(1)
    def tick(self):
        super().tick()
        per = self.period
        self.outs['clock'] = Bint((self.inittime - time()) % per >= per/2)

class Control(Component):
    def __init__(self):
        super().__init__()
        self.ins['in'] = Bint(0)
        self.setouts(0,0,0,0,0,0,0,0,0)
    def setouts(self, RegDst, ALUSrc, MemtoReg, RegWrite, MemRead, 
                MemWrite, Branch, ALUOp, Jump):
            self.outs['RegDst']     = Bint(RegDst)
            self.outs['ALUSrc']     = Bint(ALUSrc)
            self.outs['MemtoReg']   = Bint(MemtoReg)
            self.outs['RegWrite']   = Bint(RegWrite)
            self.outs['MemRead']    = Bint(MemRead)
            self.outs['MemWrite']   = Bint(MemWrite)
            self.outs['Branch']     = Bint(Branch)
            self.outs['ALUOp']      = Bint(ALUOp)  # 2 bits
            self.outs['Jump']       = Bint(Jump)
    def tick(self):
        super().tick()
        op = self.ins['in']()
        if op == '000000':  # R-format
            self.setouts(1,0,0,1,0,0,0,0b10,0)
        elif op == '001000':  #addi
            self.setouts(0,1,0,1,0,0,0,0b00,0)
        elif op == '100011':  #lw
            self.setouts(0,1,1,1,1,0,0,0b00,0)
        elif op == '101011':  #sw
            self.setouts(0,1,0,0,0,1,0,0b00,0)
        elif op == '000100':  #beq
            self.setouts(0,0,0,0,0,0,1,0b01,0)
        elif op == '000100':  #j
            self.setouts(0,0,0,0,0,0,0,0b00,1)
        else:
            raise Exception('unknown opcode, {}'.format(op))
        
class ALUControl(Component):
    def __init__(self):
        super().__init__()
        self.ins['ALUOp'] = Bint(0)  # TODO:rename to in for consistency
        self.ins['funct'] = Bint(0)
        self.outs['ALUOp'] = Bint(0)
    def tick(self):
        super().tick()
        funct = self.ins['funct']()
        aluop = self.ins['ALUOp']()
        aluop0 = aluop[-1]
        aluop1 = aluop[-2]
        if not aluop:
            self.outs['ALUOp'] = Bint(0b0010, pad=4)
        elif aluop0 == '1':
            self.outs['ALUOp'] = Bint(0b0110, pad=4)
        elif aluop1 == '1':  # r-type
            if funct == '100000':
                self.outs['ALUOp'] = Bint(0b0010, pad=4)
            elif funct == '100010':
                self.outs['ALUOp'] = Bint(0b0110, pad=4)
            elif funct == '100100':
                self.outs['ALUOp'] = Bint(0b0000, pad=4)
            elif funct == '100101':
                self.outs['ALUOp'] = Bint(0b0001, pad=4)
            elif funct == '101010':
                self.outs['ALUOp'] = Bint(0b0111, pad=4)
            elif funct == '000000':
                self.outs['ALUOp'] = Bint(0, pad=4)
            else:
                raise ValueError('Bad funct value, {}'.format(funct))
        else:
            raise ValueError('Bad ALUOp')  # this is theoretically impossible

class Multiplexer(Component):
    def __init__(self):
        super().__init__()
        self.ins['control'] = Bint(0)
        self.ins['in_1'] = Bint(0)
        self.ins['in_2'] = Bint(0)
        self.outs['out'] = Bint(0)
    def tick(self):
        super().tick()
        switch = bool(self.ins['control']())
        a = self.ins['in_2']()
        b = self.ins['in_1']()
        self.outs['out'] = a if switch else b

class ALU(ClockedComponent):
    def __init__(self, clock):
        super().__init__(clock)
        self.ins['control'] = Bint(0)
        self.ins['in_1'] = Bint(0)
        self.ins['in_2'] = Bint(0)
        self.outs['zero'] = Bint(0)
        self.outs['out'] = Bint(0)
        self.lock = True
    def tick(self):
        super().tick()
        if not self.lock:
            cont = self.ins['control']()
            a = self.ins['in_1']()
            b = self.ins['in_2']()
            if cont == '0000':  # and
                self.outs['out'] = a & b
            elif cont == '0001':  # or
                self.outs['out'] = a | b
            elif cont == '0010':  # add
                self.outs['out'] = a + b
            elif cont == '0110':  # sub
                self.outs['out'] = a - b
            elif cont == '0111':  # slt
                self.outs['out'] = Bint(1) if a < b else Bint(0)
            self.outs['zero'] = Bint(1) if not self.outs['out'] else Bint(0)
            self.lock = True
    def onupclock(self):
        self.lock = False

class SignExtend(Component):
    def __init__(self):
        super().__init__()
        self.ins['in'] = Bint(0)
        self.outs['out'] = Bint(0)
    def tick(self):
        super().tick()
        in_ = self.ins['in']()
        self.outs['out'] = Bint(in_) 

class ShiftLeftTwo(Component):
    def __init__(self):
        super().__init__()
        self.ins['in'] = Bint(0)
        self.outs['out'] = Bint(0)
    def tick(self):
        super().tick()
        in_ = self.ins['in']()
        self.outs['out'] = Bint(in_ << 2)

class AddFour(Component):
    def __init__(self):
        super().__init__()
        self.ins['in'] = Bint(0)
        self.outs['out'] = Bint(0)
    def tick(self):
        super().tick()
        in_ = self.ins['in']()
        self.outs['out'] = Bint(in_ + 4)

class And(Component):
    def __init__(self):
        super().__init__()
        self.ins['in_1'] = Bint(0)
        self.ins['in_2'] = Bint(0)
        self.outs['out'] = Bint(0)
    def tick(self):
        super().tick()
        in1 = self.ins['in_1']()
        in2 = self.ins['in_2']()
        self.outs['out'] = Bint(in1 & in2)

class RegisterFile(Component):
    def __init__(self):
        super().__init__()
        self.regs = makeregispile()
        self.ins['RegWrite'] = Bint(0)  # Control->RegWrite
        self.ins['read_reg_1'] = Bint(0)
        self.ins['read_reg_2'] = Bint(0)
        self.ins['write_reg'] = Bint(0)  # which register to write to
        self.ins['write_data'] = Bint(0)  # data to write to write register
        self.outs['read_data_1'] = Bint(0)
        self.outs['read_data_2'] = Bint(0)
    def tick(self):
        super().tick()
        do_write = self.ins['RegWrite']()
        read1 = self.ins['read_reg_1']()
        read2 = self.ins['read_reg_2']()
        writedata = self.ins['write_data']()
        write = self.ins['write_reg']()
        self.outs['read_data_1'] = Bint(self.regs[str(read1)].val)
        self.outs['read_data_2'] = Bint(self.regs[str(read2)].val)
        if do_write and write != 0:  # ignore zero register writes
            assert str(write) in self.regs, '{} not a valid register num'.format(write)
            self.regs[str(write)].val = writedata
    def __repr__(self):
        return str(self)
    def __str__(self):
        valid = [str(i) for i in range(0,32)]
        d = {k:v for k,v, in self.regs.items() if k in valid}
        return pformat(d)

class Inspector(ClockedComponent):
    """Component that listens to other components and 
    inspects data to act upon it for debugging and introspective
    purposes."""
    def __init__(self, clock, pc, alu, instrmem, datamem, 
            regisfile, control, alucont, branchalu, signext, 
            writeregmux, alumux,writeregdatamux,branchmux,jumpmux, 
            branchand,pcaddfour,shiftl2):
        super().__init__(clock)
        self.cyclec = 0
        self.pc = pc
        self.alu = alu
        self.instrmem = instrmem
        self.datamem = datamem
        self.regisfile = regisfile
        self.control = control
        self.alucont = alucont
        self.branchalu = branchalu
        self.signext = signext
        self.writeregmux = writeregmux
        self.alumux = alumux
        self.writeregdatamux = writeregdatamux
        self.branchmux = branchmux
        self.jumpmux = jumpmux
        self.branchand = branchand
        self.pcaddour = pcaddfour
        self.shiftl2 = shiftl2
    def onupclock(self):
        # self.clock()
        self.oversee()
        self.stat()
    def stat(self):
        if self.cyclec == 0:  # skips first cycle cuz it's invalid
            self.cyclec += 1
            return
        self.cyclec += 1
    def oversee(self):
        if self.cyclec == 0: return
        utilities.print_new_cycle(self.cyclec)
        print('Data') 
        pprint(self.datamem)
        print('Registers')
        print(self.regisfile)
        print('PC:', self.pc.outs['out'])
        print('Instr:', self.instrmem.outs['read'])
        print('Opcode:', self.control.ins['in']())
        print('s:', self.instrmem.outs['read'][6:11])
        print('t:', self.instrmem.outs['read'][11:16])
        print('d:', self.instrmem.outs['read'][16:21])
        print('shiftamt:', self.instrmem.outs['read'][21:26])
        print('funct:', self.instrmem.outs['read'][26:32])
        print('immediate:', self.instrmem.outs['read'][16:32])
        print('RegDst', self.control.outs['RegDst'])
        print('ALUSrc', self.control.outs['ALUSrc'])
        print('MemtoReg', self.control.outs['MemtoReg'])
        print('RegWrite', self.control.outs['RegWrite'])
        print('MemRead', self.control.outs['MemRead'])
        print('MemWrite', self.control.outs['MemWrite'])
        print('Branch', self.control.outs['Branch'])
        print('ALUOp', self.control.outs['ALUOp'])
        print('Jump', self.control.outs['Jump'])
        print('DataAddr', self.datamem.ins['addr']())
        print('DataWrite', self.datamem.ins['write']())
        print('Data_dowrite', self.datamem.ins['write_cont']())
        print('Data_doread', self.datamem.ins['read_cont']())
        print('DataRead', self.datamem.outs['read'])
        # '''
        print('ALU-out', self.alu.outs['out'])
        print('ALU-in1', self.alu.ins['in_1']())
        print('ALU-in2', self.alu.ins['in_2']())
        print('ALU-in-cont', self.alu.ins['control']())
        print('ALU-cont-in', self.alucont.ins['ALUOp']())
        print('ALU-cont-funct', self.alucont.ins['funct']())
        print('ALU-cont-out', self.alucont.outs['ALUOp'])
        print('signext-in', self.signext.ins['in']())
        print('signext-out', self.signext.outs['out'])
        print('RegWrite', self.regisfile.ins['RegWrite']())
        print('RegWriteNumb(mux)', self.writeregmux.outs['out'])
        print('RegWriteNumb', self.regisfile.ins['write_reg']())
        print('RegWriteData', self.regisfile.ins['write_data']())
        # '''
