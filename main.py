import code
from tkinter import *
import math


class element:
  slots = 0
  W = 10
  H = 10
  def __str__(self):
    return 'element'
  def __init__(self, x=0, y=0, name=None, ins=[], s='black'):
    self.addr = super().__repr__().split('0x')[1][:-1]
    self.UUID = -1
    self.updates = 0
    self.parent = None
    if name is None:
      self.name = self.__str__()
    else:
      self.name = name
    self.inputs = ins
    self.power = False
    self.x = x
    self.y = y
    self.s = s
  def getsize(self):
    return self.W, self.H
  def update(self, ins=[]):
    self.power = self.calc(ins)
    self.updates += 1
  def onclick1(self, x, y):
    if  x >= self.x and x <= self.x+self.W \
    and y >= self.y and y <= self.y+self.H:
      if self.s == 'black':
        self.s = 'orange'
      else:
        self.s = 'black'
  def onclick2(self, x, y):
    if  x >= self.x and x <= self.x+self.W \
    and y >= self.y and y <= self.y+self.H:
      self.s = 'green'
  def onkey(self, ev):
    if  ev.x >= self.x and ev.x <= self.x+self.W \
    and ev.y >= self.y and ev.y <= self.y+self.H:
      if ev.keycode == ord('D'):
        self.inputs = []
      elif ev.keycode == ord('I'):
        self.parent.g_input = self.UUID
      elif ev.keycode == ord('O') and hasattr(self.parent, 'g_input'):
        self.inputs += [self.parent.g_input]
  def __repr__(self):
    return str(vars(self))
  def calc(self, ins=[]):
    return self.power
  def render(self):
    self.parent.arc(self.x+self.W//2, self.y+self.H//2, min(self.W, self.H)//2, 0, 360, self.s)
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
  def render(self):
    self.parent.w.create_line(self.x, self.y, self.x+20, self.y, fill=self.s)
    self.parent.w.create_line(self.x, self.y, self.x, self.y+40, fill=self.s)
    self.parent.w.create_line(self.x, self.y+40, self.x+20, self.y+40, fill=self.s)
    self.parent.arc(self.x+20, self.y+20, 20, 270, 180, self.s)
    for i in range(len(self.inputs)):
      j = 40*(i+1)/(len(self.inputs)+1)
      pc = self.parent.getPowerColor(self.inputs[i], self.UUID)
      self.parent.w.create_line(self.x, self.y+j, self.x-10, self.y+j, fill=pc)
      x, y = self.parent.get(self.inputs[i]).xy()
      self.parent.w.create_line(x, y, self.x-10, self.y+j, fill=pc)
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
  def render(self):
    self.parent.arc(self.x-20,self.y+20,math.sqrt(2*20**2),315,90,self.s)
    self.parent.w.create_line(self.x, self.y, self.x+20, self.y, fill=self.s)
    self.parent.w.create_line(self.x, self.y+40, self.x+20, self.y+40, fill=self.s)
    self.parent.arc(self.x+20,self.y+20,20,270,180,self.s)
    for i in range(len(self.inputs)):
      j = 40*(i+1)/(len(self.inputs)+1)
      k = math.sqrt(20**2*2-(j-20)**2)-20
      pc = self.parent.getPowerColor(self.inputs[i], self.UUID)
      self.parent.w.create_line(self.x+k, self.y+j, self.x-10, self.y+j, fill=pc)
      x, y = self.parent.get(self.inputs[i]).xy()
      self.parent.w.create_line(x, y, self.x-10, self.y+j, fill=pc)
  def xy(self):
    return (self.x+self.W, self.y+self.H//2)

class NOTgate(element):
  slots = 1
  W = 40
  H = 40
  def __str__(self):
    return 'NOTgate'
  def calc(self, ins):
    if len(ins) < self.slots:
      return not False
    else:
      return not ins[0]
  def render(self):
    self.parent.w.create_line(self.x, self.y, self.x, self.y+40, fill=self.s)
    self.parent.w.create_line(self.x, self.y, self.x+32, self.y+20, fill=self.s)
    self.parent.w.create_line(self.x, self.y+40, self.x+32, self.y+20, fill=self.s)
    self.parent.arc(self.x+36, self.y+20, 4, 0, 360, self.s)
    if len(self.inputs) >= self.slots:
      pc = self.parent.getPowerColor(self.inputs[0], self.UUID)
      self.parent.w.create_line(self.x, self.y+20, self.x-10, self.y+20, fill=pc)
      x, y = self.parent.get(self.inputs[0]).xy()
      self.parent.w.create_line(x, y, self.x-9, self.y+20, fill=pc)
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
    self.w.bind('<Button 1>',self.onclick1)
    self.w.bind('<Button 3>',self.onclick2)
    self.w.bind('<KeyPress>',self.onkey)
    self.w.pack()
    self.w.focus_set()
  def get(self, x):
    for e in self.UUIDS:
      if e.UUID == x:
        return e
    return None
  def new(self, x=None):
    if x is None:
      x = element()
    x.parent = self
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
      if tt:
        print('inf')
    else:
      s = self.get(x)
      i = []
      for j in s.inputs:
        i += [self.get(j).power]
      s.update(i)
  def render(self):
    self.w.delete('all')
    for e in self.UUIDS:
      e.render()
    self.tk.update()
  def onclick1(self, ev):
    for e in self.UUIDS:
      e.onclick1(ev.x, ev.y)
  def onclick2(self, ev):
    for e in self.UUIDS:
      e.onclick2(ev.x, ev.y)
  def onkey(self, ev):
    print(ev)
    if ev.keycode > 111 and ev.keycode < 111+13:
      gates = {1:NOTgate, 2:ORgate, 3:ANDgate}
      b = gates[ev.keycode-111]
      self.new(b(ev.x-b.W//2, ev.y-b.H//2))
    for e in self.UUIDS:
      e.onkey(ev)

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
  i += 1
  for j in range(2**20):
    pass
code.InteractiveConsole(vars()).interact()
