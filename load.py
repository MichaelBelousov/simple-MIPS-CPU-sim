import sys
# TODO: specify pyparsing imports
from pyparsing import * 
from collections import OrderedDict

### PATTERNS ###

COMMA = Suppress(',')
# register pattern
pregis = Combine('$'+Word(alphanums))
# r-type instruction pattern
prtype = Word(alphas) + 2*(pregis+COMMA) + pregis
# i-type instruction pattern
pitype = Word(alphas) + 2*(pregis+COMMA) + Word(alphanums)

pitypemem = Word(alphas) + pregist+ COMMA
# j-type instruction pattern
jtype_pat= Word(alphas) + Or(p_regis, Word(alphanums))

# TODO: Or all
instr_pat= Or(itype_pat, Or(rtype_pat, jtype_pat))
# TODO: rename all

### END ###

def loadrtype(i):

    pass

def add(p):
    """returns a 32-bit binint representing an add instruction"""
    opcode = '000000'
    funct = '000000'
    reg1 = str(0)
    reg2 = str()
    reg3 = str()


instr = {
        'add' : add,
        }


def eval_instr(s):
    pass

def eval_rtype(s):
    s = rtype_pattern.parseString(s)
    typ = s[0]
    # TODO: iterate over list instruction obj list
    if typ  == 'add':
        s1 = regs.get(s[2], 0)
        s2 = regs.get(s[3], 0)
        regs[ s[1] ] = s1 + s2
        return regs[s[1]]
    elif typ  == 'addi':
        s1 = regs.get(s[2], 0)
        s2 = regs.get(s[3], 0)
        regs[ s[1] ] = s1 + s2
        return regs[s[1]]
    elif typ == 'sub':
        s1 = regs.get(s[2], 0)
        s2 = regs.get(s[3], 0)
        regs[ s[1] ] = s1 - s2
        return regs[s[1]]

def eval_itype(s):
    s = itype_pattern.parseString(s)
    typ = s[0]
    if typ  == 'addi':
        s1 = regs.get(s[2], 0)
        s2 = eval(s[3])
        regs[ s[1] ] = s1 + s2
        return regs[s[1]]

def I_eval(s):
    if rtype_pattern.matches(s):
        return eval_rtype(s)
    elif itype_pattern.matches(s):
        return eval_itype(s)
    else:
        return repr(eval(s))

def stripcom(s, delim):
    """strip lines of comments and whitespace"""
    if delim in s:
        return s.split(delim)[0].strip()
    else:
        return s.strip()

if __name__ == '__main__':
    # Load input
    inp = sys.stdin
    if len(sys.argv) > 1:
        inp = open(sys.argv[1], 'r')
    for l in inp:
        l = stripcom(l, '#')
        if not l:
            continue
        print('L>>',l)
        try:
            instr_pat.parseString(l)
        except SyntaxError as e:
            print(e)

