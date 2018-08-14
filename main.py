class element:
  slots = 0
  def __str__(self):
    return 'element'
  def __init__(self, name=None, ins=[]):
    self.addr = super().__repr__().split('0x')[1][:-1]
    self.UUID = -1
    self.updates = 0
    if name is None:
      self.name = self.__str__()
    else:
      self.name = name
    self.inputs = ins
    self.power = False
  def update(self, ins):
    self.updates = 0
  def __repr__(self):
    return str(vars(self))
  def calc(self):
    return self.power

class UUIDs:
  def __init__(self):
    self.UUIDS = []
    self.UUIDi = -1
  def get(self, x):
    for e in self.UUIDS:
      if e.UUID == x:
        return e
    return None
  def new(self, x=None):
    if x is None:
      x = element()
    self.UUIDi += 1
    while self.get(self.UUIDi) is not None:
      self.UUIDi += 1
    x.UUID = int(self.UUIDi)
    self.UUIDS += [x]
    return self.UUIDi
  def update(self, x=None):
    if x is None:
      for e in self.UUIDS:
        self.update(e.UUID)
    else:
      s = self.get(x)
      i = []
      for j in s.inputs:
        i += [self.get(j).power]
      s.update(i)
 