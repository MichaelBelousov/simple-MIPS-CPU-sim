# TODO: make immutable
class Binint:
    """high-level binary integer type"""
    # TODO: add class method for getting a string without constructing object
    def __init__(self, n, pad=32):
        # TODO: rename pad to bits
        if isinstance(n, str):
            if n.startswith('0b') or n.startswith('0x'):
                self.val = eval(n)
            elif n.startswith('1'):
                a = ''.join( ('1' if c=='0' else '0' for c in n) )
                a = eval('0b'+a)+1
                self.val = -a
            elif n.count('1') + n.count('0') == len(n):
                self.val = eval('0b'+n)
            elif not n:
                self.val = 0
            else:
                self.val = eval(n)
        elif isinstance(n, Binint):
            self.val = n.val
        elif isinstance(n, int):
            self.val = n
        else:
            raise TypeError('must be constructed from str or int')
        self.pad = pad
    def __int__(self):
        return self.val
    def __str__(self):
        a = '0'+bin(abs(self.val))[2:]
        if self.val < 0:
            a = ''.join( ('1' if c=='0' else '0' for c in a) )
            a = bin(eval('0b'+a)+1)[2:]
        sign = '0' if self.val >= 0 else '1'
        a = a.rjust(self.pad, sign)[-self.pad:]
        return a
    def __bool__(self):
        return bool(self.val)
    def __float__(self):
        # TODO: replace with IEEE754 floating point value
        return float(self.val)
    def __len__(self):
        return len(str(self))
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
    def __and__(self, other):
        return Binint(self.val & other.val)
    def __or__(self, other):
        return Binint(self.val | other.val)
    def __lshift__(self, shift):
        return Binint(self.val << shift, self.pad)
    def __rshift__(self, shift):
        return Binint(self.val >> shift, self.pad)
    def __divmod__(self, other):
        '''other is the divisor'''
        if not isinstance(other, Binint):
            other = Binint(other)
        div, rem = divmod(self.val, other.val)
        return Binint(div, self.pad), Binint(rem, self.pad)
    def __getitem__(self, item):
        return Binint(str(self)[item])
    def append(self, other):
        return Binint(str(self) + str(other))
    def prepend(self, other):
        return Binint(str(other) + str(self))
