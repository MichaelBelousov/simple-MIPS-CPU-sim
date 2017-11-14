import sys
from pyparsing import ParseException, Suppress, Combine, Word, alphanums, alphas
import re  # for instruction dump
import argparse
from MIPSCPU import *
from regnum import regnums

### PATTERNS ###

COMMA = Suppress(',')
LPAR = Suppress('(')
RPAR = Suppress(')')
# register pattern
pregis = Combine('$'+Word(alphanums))
# r-type instruction pattern
prtype = Word(alphas) + 2*(pregis+COMMA) + pregis

pintliteral = Word('-'+alphanums)
# i-type instruction pattern
pitypemem = Word(alphas) + pregis + COMMA + pintliteral + LPAR + pregis + RPAR
pitypenrm = Word(alphas) + 2*(pregis+COMMA) + pintliteral

pitype = pitypemem | pitypenrm
# j-type instruction pattern
pjtype = Word(alphas) + (pregis | Word(alphanums))
pnop = 'nop'

pinstr = pitype | prtype | pjtype | pnop

### END ###

def makeinstrsheet(instrs):
    res = 'Address    Code           Basic                       Source\n'
    for i in instrs:
        res += '\n'
    return res

# functions that return the binary data representing an instruction
def rep_rtype(i):
    try:
        r = regnums[i[2][1:]]
        r += regnums[i[3][1:]]
        r += regnums[i[1][1:]]
        r += '00000'  # shiftamt
    except KeyError as e:
        print(f'the register alias, {e}, is unknown')
        raise
    return r
def rep_itype(i):
    try:
        r = regnums[i[2][1:]]
        r += regnums[i[1][1:]]
        r += str(Bint(eval(i[3]),pad=16))
    except KeyError as e:
        print(f'Unknown register, {e}')
        raise
    return r
def rep_itypemem(i):
    try:
        r = regnums[i[3][1:]]  # registers
        r += regnums[i[1][1:]]
        r += str(Bint(i[2],pad=16))  # immediate
    except KeyError as e:
        print(f'Unknown register, {e}')
        raise
    return r
def add(p):
    opcode = '000000'
    funct = '100000'
    return Bint(opcode+rep_rtype(p)+funct)
def sub(p):
    opcode = '000000'
    funct = '100010'
    return Bint(opcode+rep_rtype(p)+funct)
def _and(p):
    opcode = '000000'
    funct = '100100'
    return Bint(opcode+rep_rtype(p)+funct)
def _or(p):
    opcode = '000000'
    funct = '100101'
    return Bint(opcode+rep_rtype(p)+funct)
def slt(p):
    opcode = '000000'
    funct = '101010'
    return Bint(opcode+rep_rtype(p)+funct)
def addi(p):
    opcode = '001000'
    return Bint(opcode+rep_itype(p))
def lw(p):
    opcode = '100011'
    return Bint(opcode+rep_itypemem(p))
def sw(p):
    opcode = '101011'
    return Bint(opcode+rep_itypemem(p))
def beq(p):
    opcode = '000100'
    return Bint(opcode+rep_itype(p))
def j(p):
    opcode = '000010'
    return Bint(opcode+str(Bint(p[1],pad=26)))
def nop(p):
    return Bint(0)

instr = {
        'add' : add,
        'addi' : addi,
        'sub' : sub,
        'and' : _and,
        'or' : _or,
        'slt' : slt,
        'lw' : lw,
        'sw' : sw,
        'beq' : beq,
        'j' : j,
        'nop' : nop
        }

def assembleinstr(i):
    try:
        return instr[i[0]](i)
    except KeyError as e:
        print(f'no such instruction, {e}')
        raise

def loaddump(s):
    result = {}
    for line in s.split('\n'):
        try:
            line = line.split()
            addr, code = (Bint(eval(l)) for l in line[0:2])
            result[addr] = code
        except: pass  # XXX: replace with properly handled exception
    return result

class LabelDict(dict):
    def __init__(self):
        # add reserved keywords to prevent using them as labels
        self.reserved = tuple(instr.keys())
    def __setitem__(self, itm, val):
        if itm in self.reserved:
            raise TypeError('You have a reserved as label')
        if itm in self:
            raise TypeError('You have a duplicate')
        return super().__setitem__(itm,val)

def assemble(content, comment='#',labeld=':'):
    """process raw mips code"""
    lines = []
    i = 0
    labels = LabelDict()
    # TODO: add syntax exceptions
    for l in content.split('\n'):
        # strip comments
        if comment in l:
            l = l.partition('#')[0].strip()
        else:
            l = l.strip()
        # separate labels
        label = None
        if labeld in l:
            label, _, l = (i.strip() for i in l.partition(labeld))
        if label:
            labels[label] = i if l else i+4
        if l: 
            lines.append(l)
            i += 4
    # replace labels
    for i, l in enumerate(lines):
        for label in labels:
            lines[i] = lines[i].replace(label, Bint(labels[label]).hex())
    # assemble
    offset = 0x00400000
    result = {}
    i = offset
    for l in lines:
        try:
            parsed = pinstr.parseString(l)
            res = assembleinstr(parsed)
            result[offset+i] = res
        except ParseException  as e:
            print(f'syntax of the instruction, "{e.line}" at {e.col}, {e.lineno}, is incorrect')
            raise
        i += 4
    return result
    
if __name__ == '__main__':
    # Load input
    args = argparse.ArgumentParser(description='Simulate a single-cycle MIPS processor')
    args.add_argument('inputfile', metavar='INPUTFILE', type=str, nargs='?', default=sys.stdin,
                        help='file to read input from, if absent defaults to stdin')
    args.add_argument('cycleamt', metavar='CYCLEAMOUNT', type=int, nargs='?',
                        help='amount of cycles to run before stopping')
    args.add_argument('-v', '--verbose', action='store_true',
                        help='run in verbose mode')
    args.add_argument('-p1', '--phase1', action='store_true',
                        help='only run phase1 code')
    args.add_argument('-r', '--raw', action='store_true',
                        help='input is')
    args = args.parse_args()
    if 'inputfile' is not sys.stdin:
        args.inputfile = open(args.inputfile,'r')
    inp = args.inputfile.read()
    bin_instr = {}
    if args.raw:
        bin_instr = process(inp)
    else:
        bin_instr = loaddump(inp)
    # construct CPU
    C = MIPSSingleCycleCPU()
    C.inspector.cyclelimit = args.cycleamt
    C.loadinstr(bin_instr)
    C.run()
