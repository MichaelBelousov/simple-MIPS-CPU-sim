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

pitypemem = Word(alphas) + pregis + COMMA + Word(nums) + LPAR + pregis + RPAR
pitypenrm = Word(alphas) + 2*(pregis+COMMA) + Word(alphanums)

pitype = pitypemem | pitypenrm
# j-type instruction pattern
pjtype = Word(alphas) + (pregis | Word(alphanums))

pinstr = pitype | prtype | pjtype

### END ###

# TODO: fix names
# functions that return the binary data representing an instruction
def rep_rtype(i):
    try:
        r = regnums[i[2][1:]]
        r += regnums[i[3][1:]]
        r += regnums[i[1][1:]]
        r += '00000'  # shiftamt
    except KeyError as e:
        raise KeyError('the register alias, {}, is unknown'.format(e))
    return r
def rep_itype(i):
    try:
        r = regnums[i[2][1:]]
        r += regnums[i[1][1:]]
        r += str(Bint(eval(i[3]),pad=16))
    except KeyError as e:
        raise KeyError('Unknown register, {}'.format(e))
    return r
def rep_itypemem(i):
    try:
        r = regnums[i[1][1:]]
        r += regnums[i[3][1:]]
        r += str(Bint(i[2],pad=16))
    except KeyError as e:
        raise KeyError('Unknown register, {}'.format(e))
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
    return Bint(opcode+Bint(p[1],pad=26))

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
        'j' : j
        }

def parseinstr(i):
    try:
        return instr[i[0]](i)
    except KeyError as e:
        raise KeyError('no such instruction, {}'.format(e))

def stripcom(s, delim):
    """strip lines of comments and whitespace"""
    if delim in s:
        return s.split(delim)[0].strip()
    else:
        return s.strip()

if __name__ == '__main__':
    # Load input
    args = argparse.ArgumentParser(description='Simulate a single-cycle MIPS processor')
    args.add_argument('inputfile', metavar='INPUTFILE', type=str, nargs='?', default=sys.stdin,
                        help='file to read input from, if absent defaults to stdin')
    args.add_argument('-v', '--verbose', action='store_true',
                        help='run in verbose mode')
    args.add_argument('-p1', '--phase1', action='store_true',
                        help='only run phase1 code')
    args = args.parse_args()
    bin_instr = []
    for l in args.inputfile:
        l = stripcom(l, '#')
        if not l:
            continue
        try:
            i = pinstr.parseString(l)
            res = parseinstr(i)
            bin_instr.append(res)
        except SyntaxError as e:  # TODO: replace with pyparsing exception
            raise SyntaxError('syntax of the instruction, "{}", is incorrect'.format(l))
    # construct CPU
    C = MIPSSingleCycleCPU()
    C.loadinstr(bin_instr)
    C.run()
