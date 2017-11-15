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
        self.onupclock()
        ''' # previous async code
        if self.clock.outs['clock'] != self._lastclock:
            self.onupclock()
            self._lastclock = self.clock.outs['clock']
        '''
    def onupclock(self):
        raise NotImplementedError

class PC(ClockedComponent):
    # FIXME: PC is being set on the invalid first cycle
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

class Clock(Component):  # TODO: make clocked component
    def __init__(self, inittime=time()):
        super().__init__()
        self.inittime = inittime
        self.period = 0.1  # in seconds
        self.outs['clock'] = Bint(1)
    def tick(self):
        super().tick()
        # self.outs['clock'] = Bint(not self.outs['clock'])
        self.outs['clock'] = Bint(1)
    #@deprecate
    def OLD_tick(self):
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
            branchand,pcaddfour,branchshift,jumpshift):
        super().__init__(clock)
        self.cyclec = 1
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
        self.pcaddfour = pcaddfour
        self.branchshift = branchshift
        self.jumpshift = jumpshift
        self.cyclelimit = -1
    def tick(self):
        self.stat()
    def onupclock(self):
        # self.clock()
        pass
    def halt(self):
        raise KeyboardInterrupt
    def stat(self):
        if self.cyclec == self.cyclelimit:
            self.lastcycle()
            self.halt()
        else:
            self.eachcycle()
        self.cyclec += 1
    def lastcycle(self):
        pc = self.pc.reg.val
        self.eachcycle()
        if pc not in self.instrmem:
            print('No More Instructions')
        # dumps register contents
        regdump = ''
        for i in range(8):
            for j in range(4):
                r = self.regisfile.regs[bin(4*i+j)[2:].zfill(5)].val
                regdump += f'${str(4*i+j).zfill(2)}={r.hex()}({r.dec().rjust(11)})    '
            regdump += '\n'
        print(regdump, end='')
        print(f'Number of cycles={self.cyclec}')
    def precycles(self):
        pass
    def eachcycle(self):
        utilities.print_new_cycle(self.cyclec)
        pc = self.pc.reg.val
        print(f'PC={pc.hex()} {pc.dec()}')
        instr = self.instrmem.outs['read']
        print(f'instruction={instr.hex()} {instr.dec()}')
        op = self.control.ins['in']()  # TODO: change to out
        print(f'opcode={op.bin()} {op.dec()}')
        funct = self.alucont.ins['funct']()  # TODO: change to out
        print(f'funct={op.bin()} {op.dec()}')
        rs = self.instrmem.outs['read'][6:11]
        print(f'rs={rs.bin()} {rs.dec()}')
        rt = self.instrmem.outs['read'][11:16]
        print(f'rt={rt.bin()} {rt.dec()}')
        rd = self.instrmem.outs['read'][16:21]
        print(f'rd={rd.bin()} {rd.dec()}')
        imm = self.instrmem.outs['read'][16:32]
        print(f'immediate={rd.hex()} {rd.dec()}')
        regdst = self.control.outs['RegDst']
        print(f'RegDst={regdst.bin_nopre(1)}')
        jump = self.control.outs['Jump']
        print(f'Jump={jump.bin_nopre(1)}')
        branch = self.control.outs['Branch']
        print(f'Branch={branch.bin_nopre(1)}')
        memread = self.control.outs['MemRead']
        print(f'MemRead={memread.bin_nopre(1)}')
        memtoreg = self.control.outs['MemtoReg']
        print(f'MemtoReg={memtoreg.bin_nopre(1)}')
        aluop = self.control.outs['ALUOp']
        print(f'ALUOp={aluop.bin_nopre(1)}')
        memwrite = self.control.outs['MemWrite']
        print(f'MemWrite={memwrite.bin_nopre(1)}')
        alusrc = self.control.outs['ALUSrc']
        print(f'ALUSrc={alusrc.bin_nopre(1)}')
        regwrite = self.control.outs['RegWrite']
        print(f'RegWrite={regwrite.bin_nopre(1)}')
        signext = self.signext.outs['out']
        print(f'Sign_extended_immediate={signext.hex()} {signext.dec()}')
        alu_op = self.alucont.outs['ALUOp']
        print(f'ALU_operation={alu_op.bin()} {alu_op.dec()}')
        branchaddr = self.branchalu.outs['out']
        print(f'Branch_address={branchaddr.hex()} {branchaddr.dec()}')
        jumpaddr = self.branchalu.outs['out']
        print(f'Jump_address={jumpaddr.hex()} {jumpaddr.dec()}')
        writereg = self.writeregmux.outs['out']
        print(f'Write_register={writereg.hex()} {writereg.dec()}')
        rfreaddata1 = self.regisfile.outs['read_data_1']
        print(f'RF_read_data_1={rfreaddata1.hex()} {rfreaddata1.dec()}')
        rfreaddata2 = self.regisfile.outs['read_data_2']
        print(f'RF_read_data_2={rfreaddata2.hex()} {rfreaddata2.dec()}')
        aluinp2 = self.alu.ins['in_2']()
        print(f'ALU_input_2={aluinp2.hex()} {aluinp2.dec()}')
        alures = self.alu.outs['out']
        print(f'ALU_result={alures.hex()} {alures.dec()}')
        aluzero = self.alu.outs['zero']
        print(f'Zero={aluzero.bin_nopre(1)}')
        memreaddata = self.datamem.outs['read']
        print(f'MEM_read_data={memreaddata.hex()} {memreaddata.dec()}')
        writedata = self.datamem.ins['write']()
        print(f'Write_data={writedata.hex()} {writedata.dec()}')
        pcsrc = self.branchmux.outs['out']
        print(f'PCSrc={pcsrc.bin_nopre(1)}')
        pcbranch = self.branchmux.outs['out']
        print(f'PC_branch={pcbranch.hex()} {pcbranch.dec()}')
        pcnew = self.jumpmux.outs['out']
        print(f'PC_new={pcnew.hex()} {pcnew.dec()}')
        #TODO: prevent infinite loops
        if pcnew not in self.instrmem:
            self.halt()
