import code
from tkinter import *
import math


class element:
  slots = 0
  W = 10
  H = 10
  def __str__(self):
    return 'element'
  def __init__(self, x, y, name=None, ins=[], s='black'):
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
    self.s = s
  def update(self, ins=[]):
    self.power = self.calc(ins)
    self.updates += 1
  def __repr__(self):
    return str(vars(self))
  def calc(self, ins=[]):
    return self.power
  def render(self, g):
    g.arc(self.x+self.W//2, self.y+self.H//2, min(self.W, self.H)//2, 0, 360, self.s)
  def xy(self):
    return (self.x+self.W//2, self.y+self.H//2)


class switch(element):
  slots = 0
  W = 40
  H = 40
  def __str__(self):
    return 'switch'

class ANDgate(element):
  W = 40
  H = 40
  slots = -1
  def __str__(self):
    return 'ANDgate'
  def calc(self, ins):
    for e in ins:
      if not e:
        return False
    return True
  def render(self, g):
    g.w.create_line(self.x, self.y, self.x+20, self.y, fill=self.s)
    g.w.create_line(self.x, self.y, self.x, self.y+40, fill=self.s)
    g.w.create_line(self.x, self.y+40, self.x+20, self.y+40, fill=self.s)
    g.arc(self.x+20, self.y+20, 20, 270, 180, self.s)
    for i in range(len(self.inputs)):
      j = 40*(i+1)/(len(self.inputs)+1)
      pc = g.getPowerColor(self.inputs[i], self.UUID)
      g.w.create_line(self.x, self.y+j, self.x-10, self.y+j, fill=pc)
      x, y = g.get(self.inputs[i]).xy()
      g.w.create_line(x, y, self.x-10, self.y+j, fill=pc)
  def xy(self):
    return (self.x+self.W, self.y+self.H//2)

class ORgate(element):
  slots = -1
  W = 40
  H = 40
  def __str__(self):
    return 'ORgate'
  def calc(self, ins):
    for e in ins:
      if e:
        return True
    return False
  def render(self, g):
    g.arc(self.x-20,self.y+20,math.sqrt(2*20**2),315,90,self.s)
    g.w.create_line(self.x, self.y, self.x+20, self.y, fill=self.s)
    g.w.create_line(self.x, self.y+40, self.x+20, self.y+40, fill=self.s)
    g.arc(self.x+20,self.y+20,20,270,180,self.s)
    for i in range(len(self.inputs)):
      j = 40*(i+1)/(len(self.inputs)+1)
      k = math.sqrt(20**2*2-(j-20)**2)-20
      pc = g.getPowerColor(self.inputs[i], self.UUID)
      g.w.create_line(self.x+k, self.y+j, self.x-10, self.y+j, fill=pc)
      x, y = g.get(self.inputs[i]).xy()
      g.w.create_line(x, y, self.x-10, self.y+j, fill=pc)
  def xy(self):
    return (self.x+self.W, self.y+self.H//2)

class NOTgate(element):
  slots = 1
  W = 40
  H = 40
  def __str__(self):
    return 'NOTgate'
  def calc(self, ins):
    return not ins[0]
  def render(self, g):
    g.w.create_line(self.x, self.y, self.x, self.y+40, fill=self.s)
    g.w.create_line(self.x, self.y, self.x+32, self.y+20, fill=self.s)
    g.w.create_line(self.x, self.y+40, self.x+32, self.y+20, fill=self.s)
    g.arc(self.x+36, self.y+20, 4, 0, 360, self.s)
    pc = g.getPowerColor(self.inputs[0], self.UUID)
    g.w.create_line(self.x, self.y+20, self.x-10, self.y+20, fill=pc)
    x, y = g.get(self.inputs[0]).xy()
    g.w.create_line(x, y, self.x-9, self.y+20, fill=pc)
  def xy(self):
    return (self.x+self.W, self.y+self.H//2)

class UUIDs:
  def getPowerColor(self, s, d):
    if self.get(s).power:
      return 'red'
    return 'black'
  def arc(self,x,y,r,s,e, outline='black'):
    if e >= 360:
      self.w.create_arc(x-r,y-r,x+r,y+r,start=0,extent=180,style=ARC,outline=outline)
      self.w.create_arc(x-r,y-r,x+r,y+r,start=180,extent=180,style=ARC,outline=outline)
    else:
      self.w.create_arc(x-r,y-r,x+r,y+r,start=s,extent=e,style=ARC, outline=outline)
    
  def __init__(self, WIDTH=1280, HEIGHT=720):
    self.UUIDS = []
    self.UUIDi = -1
    self.tk = Tk()
    self.w = Canvas(self.tk, width=WIDTH, height=HEIGHT)
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
  def update(self, upd=False, x=None):
    if x is None:
      for i in range(len(self.UUIDS)):
        tt = False
        for e in self.UUIDS:
          t = self.get(e.UUID).power
          self.update(upd, e.UUID)
          if self.get(e.UUID).power != t:
            tt = True
            if upd:
              UUIDS.render()
        if not tt:
          break
        print(i)
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
s = 70
in1 = UUIDS.new(switch(s,s,'in1'))
in2 = UUIDS.new(switch(s,2*s,'in2'))
not1 = UUIDS.new(NOTgate(2*s,s,'not1', [in1]))
not2 = UUIDS.new(NOTgate(2*s,2*s,'not2', [in2]))
orc1 = UUIDS.new(ORgate(3*s,1.5*s,'orc1', [not1, not2]))
or1 = UUIDS.new(ORgate(4*s,s,'or1', [not1, orc1]))
or2 = UUIDS.new(ORgate(4*s,2*s,'or2', [orc1, not2]))
no1 = UUIDS.new(NOTgate (5*s,s,'no1', [or1]))
no2 = UUIDS.new(NOTgate(5*s,2*s,'no2', [or2]))
orc2 = UUIDS.new(ORgate(6*s,1.5*s,'orc2', [no1, no2]))
i = 0
while 1:
  UUIDS.get(in1).power = (i//2)%2 != 0
  UUIDS.get(in2).power = i%2 != 0
  UUIDS.update()
  print(UUIDS.get(in1).power, UUIDS.get(in2).power, UUIDS.get(orc2).power)
  UUIDS.render()
  input()
  i += 1
code.InteractiveConsole(vars()).interact()
