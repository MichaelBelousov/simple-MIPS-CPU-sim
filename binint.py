# TODO: reimplement everything using bytes object or proper module
class Binint:
    """high-level binary integer type"""
    # TODO: add class method for getting a string without constructing object
    # TODO: add class method for constructing a binint from a list of binints
    # TODO: replace most constructor functionality with conversion functions
    # TODO: inherit from int?
    def __init__(self, n, pad=32):
        # TODO: rename pad to bits
        if isinstance(n, str):
            if n.count('1') + n.count('0') == len(n):
                pad = len(n)  # XXX
                if n.startswith('1'):  # XXX
                    a = ''.join( ('1' if c=='0' else '0' for c in n) )
                    a = eval('0b'+a)+1
                    self.val = -a
                else:
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
        if self.pad == 32:
            return self.hex()
        else:
            return str(self)
    def hex(self):
        h = '0x'+hex(eval('0b'+str(self)))[2:].zfill(self.pad//4).upper()
        return h
    def bin_nopre(self, p=None):
        return self.bin(p)[2:]
    def bin(self, p=None): 
        if p is None:
            p = self.pad
        return '0b'+str(self[-p:])
    def dec(self, signed=False): 
        b = Binint('0'+str(self))
        return str(b.val)
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
    def eq(self, other):
        """bit equivalence, do not interpret as twos complement int"""
        if not isinstance(other, Binint):
            other = Binint(other)
        return str(self) == str(other)
    def __mul__(self, other):
        if not isinstance(other, Binint):
            other = Binint(other)
        return Binint(self.val * other.val, self.pad)
    def __and__(self, other):
        return Binint(self.val & other.val)
    def __or__(self, other):
        return Binint(self.val | other.val)
    # TODO: don't preserve value during shift
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
        p = 1
        if isinstance(item, slice):
            start, stop = item.start, item.stop
            if item.start is None:
                start = 0
            if item.stop is None:
                stop = len(self)
            if start < 0:
                start = len(self)+start
            if stop < 0:
                stop = len(self)+stop
            p = stop - start
        return Binint(str(self)[item], pad=p)
    def __hash__(self):
        return hash(str(self))
    def append(self, other):
        if not isinstance(other, Binint):
            other = Binint(other)
        return Binint(str(self) + str(other), pad = self.pad+other.pad)
    def prepend(self, other):
        if not isinstance(other, Binint):
            other = Binint(other)
        return Binint(str(other) + str(self), pad = self.pad+other.pad)
