import sys
import utils
from pyparsing import * 
from collections import OrderedDict

### PATTERNS ###

COMMA = Suppress(',')
# register pattern
p_regis = Combine('$'+Word(alphanums))
# r-type instruction pattern
rtype_pattern = Word(alphas) + 2*(p_regis+COMMA) + p_regis
# i-type instruction pattern
itype_pattern = Word(alphas) + 2*(p_regis+COMMA) + Word(alphanums)

### END ###

### ENV ###

# all accesses must use default of 0

regs = {}

mem = OrderedDict()

### END ###

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

### MAIN ###

# TODO: Add simple history
while True:
    try:
        inp = input('%=>')
        print(I_eval(inp))
    except KeyboardInterrupt as e:
        print('\nexiting...')
        sys.exit()
    except EOFError as e:
        print('\nexiting...')
        sys.exit()
    except Exception as e:
        print(e)
