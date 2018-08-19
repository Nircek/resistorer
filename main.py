import code
from tkinter import *
import math


class element:
  slots = 0
  W = 10
  H = 10
  def __str__(self):
    return 'element'
  def __init__(self, parent, x, y, name=None, ins=None, s='black'):
    self.addr = super().__repr__().split('0x')[1][:-1]
    self.UUID = -1
    self.updates = 0
    self.parent = parent
    if name is None:
      self.name = self.__str__()
    else:
      self.name = name
    if ins is None:
      self.inputs = []
    else:
      self.inputs = ins
    for e in self.inputs:
      self.parent.get(e).outs += [self]
    self.power = False
    self.x = x
    self.y = y
    self.s = s
    self.outs = []
  def getsize(self):
    return self.W, self.H
  def update(self, ins):
    self.power = self.calc(ins)
    self.updates += 1
  def onclick2(self):
      self.s = 'green'
  def motion(self, x, y):
      self.x = x - self.W // 2
      self.y = y - self.H // 2
  def onkey(self, ev):
    if  ev.x >= self.x and ev.x <= self.x+self.W \
    and ev.y >= self.y and ev.y <= self.y+self.H:
      print(self.UUID)
      if ev.keycode == ord('D'):
        self.inputs = []
      elif ev.keycode == ord('I'):
        self.parent.g_input = self.UUID
      elif ev.keycode == ord('O') and hasattr(self.parent, 'g_input'):
        self.inputs += [self.parent.g_input]
        self.parent.get(self.parent.g_input).outs += [self]
      elif ev.keycode == 46:
        for e in self.outs:
          i=0
          while i < len(e.inputs):
            if e.inputs[i] == self.UUID:
              del e.inputs[i]
            else:
              i += 1
        self.parent.rm(self.UUID)
  def __repr__(self):
    return str(vars(self))
  def calc(self, ins):
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
  def onclick2(self):
    self.power = not self.power
  def render(self):
    s = self.s
    if s == 'black' and self.power:
      s = 'red'
    self.parent.arc(self.x+self.W//2, self.y+self.H//2, min(self.W, self.H)//2, 0, 360, s)

class light(element):
  slots = 1
  H = 40
  W = 40
  def __str__(self):
    return 'light'
  def calc(self, ins):
    if len(ins) < self.slots:
      return False
    else:
      return ins[0]
  def render(self):
    s = self.s
    if s == 'black' and self.power:
      s = 'red'
    self.parent.w.create_rectangle(self.x, self.y, self.x+self.W, self.y+self.H, outline=s)
    if len(self.inputs) >= self.slots:
      pc = self.parent.getPowerColor(self.inputs[0], self.UUID)
      x, y = self.parent.get(self.inputs[0]).xy()
      self.parent.w.create_line(x, y, self.x+self.W//2, self.y+self.H//2, fill=pc)

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
    self.w.bind('<B1-Motion>', self.motion)
    self.w.pack()
    self.w.focus_set()
    self.in_motion = None
  def get(self, x):
    for e in self.UUIDS:
      if e.UUID == x:
        return e
    return None
  def rm(self, x):
    i = 0
    while i < len(self.UUIDS):
      if self.UUIDS[i].UUID == x:
        del self.UUIDS[i]
      else:
        i += 1
  def new(self, c, x, y, ins=None):
    e = c(self, x, y, ins=ins)
    self.UUIDi += 1
    while self.get(self.UUIDi) is not None:
      self.UUIDi += 1
    e.UUID = int(self.UUIDi)
    self.UUIDS += [e]
    return self.UUIDi
  def add(self, x=None): # deprecated because x must have parent
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
      tt = False
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
    self.in_motion = None
    for e in self.UUIDS:
      if  ev.x >= e.x and ev.x <= e.x+e.W \
      and ev.y >= e.y and ev.y <= e.y+e.H:
        self.in_motion = e.UUID
  def onclick2(self, ev):
    for e in self.UUIDS:
      if  ev.x >= e.x and ev.x <= e.x+e.W \
      and ev.y >= e.y and ev.y <= e.y+e.H:
        e.onclick2()
  def motion(self, ev):
    if self.in_motion is not None:
      self.get(self.in_motion).motion(ev.x, ev.y)
  def onkey(self, ev):
    print(ev)
    if ev.keycode > 111 and ev.keycode < 111+13:
      gates = [None, switch, light, NOTgate, ORgate, ANDgate]
      b = gates[ev.keycode-111]
      self.new(b, ev.x-b.W//2, ev.y-b.H//2)
    if ev.keycode == 220:
      code.InteractiveConsole(vars()).interact()
    if ev.state == 0x40001:
      self.UUIDS = []
      self.UUIDi = 0
    for e in self.UUIDS:
      e.onkey(ev)

UUIDS = UUIDs()
s = 70
in1 = UUIDS.new(switch,s,s)
in2 = UUIDS.new(switch,s,2*s)
not1 = UUIDS.new(NOTgate,2*s,s,[in1])
not2 = UUIDS.new(NOTgate,2*s,2*s,[in2])
orc1 = UUIDS.new(ORgate,3*s,1.5*s,[not1, not2])
or1 = UUIDS.new(ORgate,4*s,s,[not1, orc1])
or2 = UUIDS.new(ORgate,4*s,2*s,[orc1, not2])
no1 = UUIDS.new(NOTgate,5*s,s,[or1])
no2 = UUIDS.new(NOTgate,5*s,2*s,[or2])
orc2 = UUIDS.new(ORgate,6*s,1.5*s,[no1, no2])
out = UUIDS.new(light, 7*s, 1.5*s, [orc2])
i = 0
while 1:
  UUIDS.update()
  UUIDS.render()
  i += 1
code.InteractiveConsole(vars()).interact()
