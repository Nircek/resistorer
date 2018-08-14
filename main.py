import code

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

class ANDgate(element):
  slots = -1
  def __str__(self):
    return 'ANDgate'
  def calc(self, ins):
    for e in ins:
      if not e:
        return False
    return True
  def update(self, ins):
    self.power = self.calc(ins)

class ORgate(element):
  slots = -1
  def __str__(self):
    return 'ORgate'
  def calc(self, ins):
    for e in ins:
      if e:
        return True
    return False
  def update(self, ins):
    self.power = self.calc(ins)

class NOTgate(element):
  slots = 1
  def __str__(self):
    return 'NOTgate'
  def calc(self, ins):
    return not ins[0]
  def update(self, ins):
    self.power = self.calc(ins)

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

UUIDS = UUIDs()
in1 = UUIDS.new(element('in1'))
in2 = UUIDS.new(element('in2'))
not1 = UUIDS.new(NOTgate('not1', [in1]))
not2 = UUIDS.new(NOTgate('not2', [in2]))
orc1 = UUIDS.new(ORgate('orc1', [not1, not2]))
or1 = UUIDS.new(ORgate('or1', [not1, orc1]))
or2 = UUIDS.new(ORgate('or2', [not2, orc1]))
no1 = UUIDS.new(NOTgate('no1', [or1]))
no2 = UUIDS.new(NOTgate('no2', [or2]))
orc2 = UUIDS.new(ORgate('orc2', [no1, no2]))
UUIDS.get(in1).power = False
UUIDS.get(in2).power = False
for i in range(5):
  UUIDS.update()
print(UUIDS.get(in1).power, UUIDS.get(in2).power, UUIDS.get(orc2).power)
UUIDS.get(in1).power = False
UUIDS.get(in2).power = True
for i in range(5):
  UUIDS.update()
print(UUIDS.get(in1).power, UUIDS.get(in2).power, UUIDS.get(orc2).power)
UUIDS.get(in1).power = True
UUIDS.get(in2).power = False
for i in range(5):
  UUIDS.update()
print(UUIDS.get(in1).power, UUIDS.get(in2).power, UUIDS.get(orc2).power)
UUIDS.get(in1).power = True
UUIDS.get(in2).power = True
for i in range(5):
  UUIDS.update()
print(UUIDS.get(in1).power, UUIDS.get(in2).power, UUIDS.get(orc2).power)

from tkinter import *
def arc(x,y,r,s,e):
  global w, tk
  if e > 360:
    w.create_arc(x-r,y-r,x+r,y+r,start=0,extent=180,style=ARC)
    w.create_arc(x-r,y-r,x+r,y+r,start=180,extent=180,style=ARC)
  else:
    w.create_arc(x-r,y-r,x+r,y+r,start=s,extent=e,style=ARC)
  tk.update()
tk = Tk()
w = Canvas(tk, width=1280, height=720)
w.pack()
w.create_line(0,0,1280,720)
w.create_rectangle(100,100,200,200, fill='red')
while 1:
  code.InteractiveConsole(vars()).interact()
  tk.update()
