
class Binint:
    def __init__(self, n, pad=1):
        if isinstance(n, str):
            if n[0] == '1':
                a = ''.join( ('1' if c=='0' else '0' for c in n) )
                a = eval('0b'+a)+1
                self.val = -a
            else:
                self.val = eval('0b'+n)
        elif isinstance(n, int):
            self.val = n
        else:
            raise TypeError('must be constructed from str or int')
        self.pad = pad
    def __int__(self):
        return self.val
    def __str__(self):
        a = bin(abs(self.val))[2:]
        if self.val < 0:
            a = ''.join( ('1' if c=='0' else '0' for c in a) )
            a = bin(eval('0b'+a)+1)[2:]
        if self.val < 0:
            a = '1'+a
        else: 
            a = '0'+a
        # pad
        if len(a) < self.pad:
            sign = '1' if self.val < 0 else '0'
            a = sign*(self.pad-len(a)) + a
        return a
    def __repr__(self):
        return str(self)
    def __add__(self, other):
        if not isinstance(other, Binint):
            other = Binint(other)
        return Binint(self.val + other.val, self.pad)
    def __sub__(self, other):
        if not isinstance(other, Binint):
            other = Binint(other)
        return Binint(self.val - other.val, self.pad)
    def __lt__(self, other):
        if not isinstance(other, Binint):
            other = Binint(other)
        return self.val < other.val
    def __eq__(self, other):
        if not isinstance(other, Binint):
            other = Binint(other)
        return self.val == other.val
    def __mul__(self, other):
        if not isinstance(other, Binint):
            other = Binint(other)
        return Binint(self.val * other.val, self.pad)
    def __lshift__(self, shift):
        return Binint(self.val << shift, self.pad)
    def __rshift__(self, shift):
        return Binint(self.val >> shift, self.pad)
    def divide(self, other):
        '''other is the divisor'''
        # TODO: replace with divmod of values
        if not isinstance(other, Binint):
            other = Binint(other)
        lself = len(str(self))
        lother = len(str(other))
        l = max(lself, lother)
        quotient = Binint(0)
        divisor = Binint(str(other) + l*'0')
        remainder = self
        print('iter', 'Q', 'D', 'R')
        print(0, quotient, divisor, remainder)
        for i in range(1, len(str(self))+2):
            remainder -= divisor
            if remainder < 0:
                remainder += divisor
                quotient = Binint(str(quotient)[1:]+'0')
            else:
                quotient = Binint(str(quotient)[1:]+'1')
            divisor = Binint('0'+str(divisor)[:-1])
            print(i, quotient, divisor, remainder)
        print('int result: ({}, {})'.format(quotient.val, remainder.val))
        return quotient, remainder


