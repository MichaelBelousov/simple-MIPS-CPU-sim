
class regis:
    def __init__(self, val=0, writable=True):
        self._val = val
        self.write = True
    @property
    def val(self):
        return self._val
    @val.setter
    def val(self, inval):
        if not self.writable:
            raise Warning('attempting to write to readonly reg')
        self._val = inval


regs = [regis() for r in range(0,32)]

aliases = {
    '0' : regs[0],
    'zero' : regs[0],

    '1' : regs[1],
    'at' : regs[1],

    '2' : regs[2],
    'v0' : regs[2],

    '3' : regs[3],
    'v1' : regs[3],

    '4' : regs[4],
    'a0' : regs[4],

    '5' : regs[5],
    'a1' : regs[5],
    
    '6' : regs[6],
    'a2' : regs[6],
    
    '7' : regs[7],
    'a3' : regs[7],

    '8' : regs[8],
    't0' : regs[8],
    
    '9' : regs[9],
    't1' : regs[9],

    '10' : regs[10],
    't2' : regs[10],

    '11' : regs[11],
    't3' : regs[11],

    '12' : regs[12],
    't4' : regs[12],

    '13' : regs[13],
    't5' : regs[13],

    '14' : regs[14],
    't6' : regs[14],

    '15' : regs[15],
    't7' : regs[15],

    '16' : regs[16],
    's0' : regs[16],

    '17' : regs[17],
    's1' : regs[17],

    '18' : regs[18],
    's2' : regs[18],

    '19' : regs[19],
    's3' : regs[19],

    '20' : regs[20],
    's4' : regs[20],

    '21' : regs[21],
    's5' : regs[21],

    '22' : regs[22],
    's6' : regs[22],

    '23' : regs[23],
    's7' : regs[23],

    '24' : regs[24],
    't8' : regs[24],

    '25' : regs[25],
    't9' : regs[25],

    '26' : regs[26],
    'k0' : regs[26],

    '27' : regs[27],
    'k1' : regs[27],

    '28' : regs[28],
    'gp' : regs[28],

    '29' : regs[29],
    'sp' : regs[29],

    '30' : regs[30],
    'fp' : regs[30],

    '29' : regs[31],
    'ra' : regs[31],
    }
"""dictionary mapping register names to register objects"""

del regs
