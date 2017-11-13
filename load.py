import sys
# TODO: specify pyparsing imports
from pyparsing import * 
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
# i-type instruction pattern

pintliteral = Word('-'+alphanums)
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

def parseinstr(i):
    try:
        return instr[i[0]](i)
    except KeyError as e:
        print(f'no such instruction, {e}')
        raise

def loadhex(s):
    result = []
    import re
    hexre = re.compile(r'^0x[09af]{8}')  # hex at start of line
    result = hexre.findall(s)
    return result

# TODO: add label detection and assembly
def process(s, delim='#'):
    """process raw mips code"""
    # strip comments
    result = []
    if delim in s:
        result = s.split(delim)[0].strip()
    else:
        return s.strip()
    # replace labels

def process(raw, comment='#',label=':'):
    """process raw mips code"""
    # strip comments
    lines = []
    for l in raw.split('\n'):
        if comment in l:
            result = split(comment)[0].strip()
        else:
            l = s.strip()
        if l: 
            lines.append(i)
    # determine labels
    for l in lines:
        
    # replace labels



    # XXX: DONT check amount of colons
    offset=0
    for l in raw.split('\n'):
        code, label = None, None
        c = l.count(label)
        if c == 1:
            label, code = (i.strip() for i in l.split(label))
        elif c == 0:
            code = l
        else:
            raise SyntaxError('too many colons')
        result = []
        if comment in s:
            result = s.split(comment)[0].strip()
        else:
            return s.strip()
    # replace labels
    
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
    args = args.parse_args()
    if 'inputfile' in args:
        args.inputfile = open(args.inputfile,'r')
    # assemble
    bin_instr = []
    for l in args.inputfile:
        l = process(l)
        if not l:
            continue
        try:
            i = pinstr.parseString(l)
            res = parseinstr(i)
            bin_instr.append(res)
        except ParseException  as e:
            print('syntax of the instruction, "{e.line}" at {e.col}, {e.lineno}, is incorrect')
            raise
    # construct CPU
    C = MIPSSingleCycleCPU()
    C.inspector.cyclelimit = args.cycleamt
    C.loadinstr(bin_instr)
    C.run()
