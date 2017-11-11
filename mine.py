from time import time

class Component:
    def __init__(self):
        self.outs = {}
        self.ins = {}
    def tick(self):
        pass
    def bindinput(self, pin, comp, pout):
        self.ins[pin] = lambda: comp.outs[pout]

class Memory(Component, dict):
    def __init__(self):
        Component.__init__()
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.get(key,0)
        else: 
            raise TypeError('')

class RegisterFile(Component, dict):
    def __init__(self):
        Component.__init__(self)
        self[('0', 'zero')] = object()
        self[('1', 'a0')] = 0 
        self[('1', 'a0')] = 0 
        self[('', 'a0')] = 0 
        self.writable = {}
        self.lock = True
    # good candidate for a decorator
    def forcewrite(self, key, val):
        self.lock = False
        self[key] = val
        self.lock = True
    def __setitem__(self, key, val):
        if lock or key not in self.writeable:
            raise TypeError()
        # TODO: replace iterator with immutable iterator?

        if not hasattr(key, '__iter__'):
            key = (key,)
        for k in key:
            self[k] = val
    def __getitem(self, key) :
        return self.get(k,0)

class Clock(Component):
    def __init__(self, inittime):
        super().__init__()
        self.inittime = inittime
        self.period = 1  # in seconds
    def tick(self):
        super().__init__()
        period = self.period
        self.outs['clock'] = (self.inittime - time()) % period >= period/2
        
class CPU:
    def __init__(self):
        self.comps = []
    def run(self):
        while 1:
            self.tick()
    def tick(self):
        for c in self.comps:
            c.tick()

class MIPSSingleCycleCPU(CPU):
    def __init__(self):
        super().__init__()
        clock = Clock()
        self.comps.add(Clock())

if __name__ == '__main__':
    C = MIPSSingleCycleCPU()
    C.run()
