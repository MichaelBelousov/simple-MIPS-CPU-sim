from binint import Binint as Bint

class Regis:
    def __init__(self, val=Bint(0), writable=True):
        self._val = val
        self.write = writable
        self.lock = False
    @property
    def val(self):
        return self._val
    @val.setter
    def val(self, inval):
        if not self.write:
            raise Warning('Writing to read-only reg')
        if self.lock: return
        self._val = inval

def makeregispile():
    regs = []
    for r in range(0,32):
        write = True
        # special registers
        if r in (0,26,27):
            write = False
        regs.append(Regis(writable=write))
    # NOTE: could use an ordered dict for some structual compression
    aliases = {
        '0' : regs[0],
        'zero' : regs[0],
        '00000' : regs[0],
        '1' : regs[1],
        'at' : regs[1],
        '00001' : regs[1],
        '2' : regs[2],
        'v0' : regs[2],
        '00010' : regs[2],
        '3' : regs[3],
        'v1' : regs[3],
        '00011' : regs[3],
        '4' : regs[4],
        'a0' : regs[4],
        '00100' : regs[4],
        '5' : regs[5],
        'a1' : regs[5],
        '00101' : regs[5],
        '6' : regs[6],
        'a2' : regs[6],
        '00110' : regs[6],
        '7' : regs[7],
        'a3' : regs[7],
        '00111' : regs[7],
        '8' : regs[8],
        't0' : regs[8],
        '01000' : regs[8],
        '9' : regs[9],
        't1' : regs[9],
        '01001' : regs[9],
        '10' : regs[10],
        't2' : regs[10],
        '01010' : regs[10],
        '11' : regs[11],
        't3' : regs[11],
        '01011' : regs[11],
        '12' : regs[12],
        't4' : regs[12],
        '01100' : regs[12],
        '13' : regs[13],
        't5' : regs[13],
        '01101' : regs[13],
        '14' : regs[14],
        't6' : regs[14],
        '01110' : regs[14],
        '15' : regs[15],
        't7' : regs[15],
        '01111' : regs[15],
        '16' : regs[16],
        's0' : regs[16],
        '10000' : regs[16],
        '17' : regs[17],
        's1' : regs[17],
        '10001' : regs[17],
        '18' : regs[18],
        's2' : regs[18],
        '10010' : regs[18],
        '19' : regs[19],
        's3' : regs[19],
        '10011' : regs[19],
        '20' : regs[20],
        's4' : regs[20],
        '10100' : regs[20],
        '21' : regs[21],
        's5' : regs[21],
        '10101' : regs[21],
        '22' : regs[22],
        's6' : regs[22],
        '10110' : regs[22],
        '23' : regs[23],
        's7' : regs[23],
        '10111' : regs[23],
        '24' : regs[24],
        't8' : regs[24],
        '11000' : regs[24],
        '25' : regs[25],
        't9' : regs[25],
        '11001' : regs[25],
        '26' : regs[26],
        'k0' : regs[26],
        '11010' : regs[26],
        '27' : regs[27],
        'k1' : regs[27],
        '11011' : regs[27],
        '28' : regs[28],
        'gp' : regs[28],
        '11100' : regs[28],
        '29' : regs[29],
        'sp' : regs[29],
        '11101' : regs[29],
        '30' : regs[30],
        'fp' : regs[30],
        '11110' : regs[30],
        '31' : regs[31],
        'ra' : regs[31],
        '11111' : regs[31]
        }
    return aliases
