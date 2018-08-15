import code
from tkinter import *
import math


class element:
  slots = 0
  W = 20
  H = 20
  def __str__(self):
    return 'element'
  def __init__(self, x, y, name=None, ins=[]):
    self.addr = super().__repr__().split('0x')[1][:-1]
    self.UUID = -1
    self.updates = 0
    if name is None:
      self.name = self.__str__()
    else:
      self.name = name
    self.inputs = ins
    self.power = False
    self.x = x
    self.y = y
  def update(self, ins):
    self.updates = 0
  def __repr__(self):
    return str(vars(self))
  def calc(self):
    return self.power
  def render(self, g, s='black'):
    g.arc(self.x+self.W//2, self.y+self.H//2, min(self.W, self.H)//2, 0, 360, s)

class ANDgate(element):
  W = 20
  H = 20
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
  def render(self, g, s='black'):
    g.w.create_line(self.x, self.y, self.x+10, self.y, fill=s)
    g.w.create_line(self.x, self.y, self.x, self.y+20, fill=s)
    g.w.create_line(self.x, self.y+20, self.x+10, self.y+20, fill=s)
    g.arc(self.x+10, self.y+10, 10, 270, 180, s)

class ORgate(element):
  slots = -1
  W = 20
  H = 20
  def __str__(self):
    return 'ORgate'
  def calc(self, ins):
    for e in ins:
      if e:
        return True
    return False
  def update(self, ins):
    self.power = self.calc(ins)
  def render(self, g, s='black'):
    g.arc(self.x-10,self.y+10,math.sqrt(200),315,90,s)
    g.w.create_line(self.x, self.y, self.x+10, self.y, fill=s)
    g.w.create_line(self.x, self.y+20, self.x+10, self.y+20, fill=s)
    g.arc(self.x+10,self.y+10,10,270,180,s)

class NOTgate(element):
  slots = 1
  def __str__(self):
    return 'NOTgate'
  def calc(self, ins):
    return not ins[0]
  def update(self, ins):
    self.power = self.calc(ins)

class UUIDs:
  def arc(self,x,y,r,s,e, outline='black'):
    if e >= 360:
      self.w.create_arc(x-r,y-r,x+r,y+r,start=0,extent=180,style=ARC,outline=outline)
      self.w.create_arc(x-r,y-r,x+r,y+r,start=180,extent=180,style=ARC,outline=outline)
    else:
      self.w.create_arc(x-r,y-r,x+r,y+r,start=s,extent=e,style=ARC)
    
  def __init__(self, WIDTH=1280, HEIGHT=720):
    self.UUIDS = []
    self.UUIDi = -1
    self.tk = Tk()
    self.w = Canvas(self.tk)
    self.w.pack()
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
  def render(self):
    for e in self.UUIDS:
      e.render(self)
    self.tk.update()

UUIDS = UUIDs()
in1 = UUIDS.new(element(20,50,'in1'))
in2 = UUIDS.new(element(20,70,'in2'))
not1 = UUIDS.new(NOTgate(50,50,'not1', [in1]))
not2 = UUIDS.new(NOTgate(50,70,'not2', [in2]))
orc1 = UUIDS.new(ANDgate(80,60,'orc1', [not1, not2]))
or1 = UUIDS.new(ORgate(110,50,'or1', [not1, orc1]))
or2 = UUIDS.new(ORgate(110,70,'or2', [not2, orc1]))
no1 = UUIDS.new(NOTgate (140,50,'no1', [or1]))
no2 = UUIDS.new(NOTgate(140,70,'no2', [or2]))
orc2 = UUIDS.new(ORgate(170,60,'orc2', [no1, no2]))
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
UUIDS.render()
code.InteractiveConsole(vars()).interact()
