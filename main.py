import code
from tkinter import *
import math

class pos:
  def __init__(self, *a):
    if len(a) == 1:
      a = a[0]
    self.x = a[0]
    self.y = a[1]
    self.w = a[0]
    self.h = a[1]
    
class element:
  slots = 0
  s = pos(10, 10)
  def __str__(self):
    return 'element'
  def __init__(self, parent, p, name=None, ins=None, st='black'):
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
    self.p = p
    self.st = st
    self.outs = []
  def getsize(self):
    return self.s
  def update(self, ins):
    self.power = self.calc(ins)
    self.updates += 1
  def onclick1(self):
    if self.s == 'black':
      self.s = 'orange'
    else:
      self.s = 'black'
  def onclick2(self):
      self.s = 'green'
  def motion(self, p):
      self.p.x = p.x - self.s.w // 2
      self.p.y = p.y - self.s.h // 2
  def onkey(self, ev):
    if  ev.x >= self.p.x and ev.x <= self.p.x+self.s.w \
    and ev.y >= self.p.y and ev.y <= self.p.y+self.s.h:
      print(self.UUID)
      if ev.keycode == ord('D'):
        self.inputs = []
      elif ev.keycode == ord('I'):
        self.parent.selected = self.UUID
      elif ev.keycode == ord('O') and self.parent.selected is not None:
        self.inputs += [self.parent.selected]
        self.parent.get(self.parent.selected).outs += [self]
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
    self.parent.arc(self.p.x+self.s.w//2, self.p.y+self.s.h//2, min(self.s.w, self.s.h)//2, 0, 360, self.st)
  def xy(self):
    return (self.p.x+self.s.w//2, self.p.y+self.s.h//2)


class switch(element):
  slots = 0
  s = pos(40, 40)
  def __str__(self):
    return 'switch'
  def onclick2(self):
    self.power = not self.power
  def render(self):
    st = self.st
    if st == 'black' and self.power:
      st = 'red'
    self.parent.arc(self.p.x+self.s.w//2, self.p.y+self.s.h//2, min(self.s.w, self.s.h)//2, 0, 360, st)

class light(element):
  slots = 1
  s = pos(40, 40)
  def __str__(self):
    return 'light'
  def calc(self, ins):
    if len(ins) < self.slots:
      return False
    else:
      return ins[0]
  def render(self):
    st = self.st
    if st == 'black' and self.power:
      st = 'red'
    self.parent.w.create_rectangle(self.p.x, self.p.y, self.p.x+self.s.w, self.p.y+self.s.h, outline=st)
    if len(self.inputs) >= self.slots:
      pc = self.parent.getPowerColor(self.inputs[0], self.UUID)
      x, y = self.parent.get(self.inputs[0]).xy()
      self.parent.w.create_line(x, y, self.p.x+self.s.w//2, self.p.y+self.s.h//2, fill=pc)

class ANDgate(element):
  s = pos(40, 40)
  slots = -1
  def __str__(self):
    return 'ANDgate'
  def calc(self, ins):
    for e in ins:
      if not e:
        return False
    return True
  def render(self):
    self.parent.w.create_line(self.p.x, self.p.y, self.p.x+20, self.p.y, fill=self.st)
    self.parent.w.create_line(self.p.x, self.p.y, self.p.x, self.p.y+40, fill=self.st)
    self.parent.w.create_line(self.p.x, self.p.y+40, self.p.x+20, self.p.y+40, fill=self.st)
    self.parent.arc(self.p.x+20, self.p.y+20, 20, 270, 180, self.st)
    for i in range(len(self.inputs)):
      j = 40*(i+1)/(len(self.inputs)+1)
      pc = self.parent.getPowerColor(self.inputs[i], self.UUID)
      self.parent.w.create_line(self.p.x, self.p.y+j, self.p.x-10, self.p.y+j, fill=pc)
      x, y = self.parent.get(self.inputs[i]).xy()
      self.parent.w.create_line(x, y, self.p.x-10, self.p.y+j, fill=pc)
  def xy(self):
    return (self.p.x+self.s.w, self.p.y+self.s.h//2)

class ORgate(element):
  slots = -1
  s = pos(40, 40)
  def __str__(self):
    return 'ORgate'
  def calc(self, ins):
    for e in ins:
      if e:
        return True
    return False
  def render(self):
    self.parent.arc(self.p.x-20,self.p.y+20,math.sqrt(2*20**2),315,90,self.st)
    self.parent.w.create_line(self.p.x, self.p.y, self.p.x+20, self.p.y, fill=self.st)
    self.parent.w.create_line(self.p.x, self.p.y+40, self.p.x+20, self.p.y+40, fill=self.st)
    self.parent.arc(self.p.x+20,self.p.y+20,20,270,180,self.st)
    for i in range(len(self.inputs)):
      j = 40*(i+1)/(len(self.inputs)+1)
      k = math.sqrt(20**2*2-(j-20)**2)-20
      pc = self.parent.getPowerColor(self.inputs[i], self.UUID)
      self.parent.w.create_line(self.p.x+k, self.p.y+j, self.p.x-10, self.p.y+j, fill=pc)
      x, y = self.parent.get(self.inputs[i]).xy()
      self.parent.w.create_line(x, y, self.p.x-10, self.p.y+j, fill=pc)
  def xy(self):
    return (self.p.x+self.s.w, self.p.y+self.s.h//2)

class NOTgate(element):
  slots = 1
  s = pos(40, 40)
  def __str__(self):
    return 'NOTgate'
  def calc(self, ins):
    if len(ins) < self.slots:
      return not False
    else:
      return not ins[0]
  def render(self):
    self.parent.w.create_line(self.p.x, self.p.y, self.p.x, self.p.y+40, fill=self.st)
    self.parent.w.create_line(self.p.x, self.p.y, self.p.x+32, self.p.y+20, fill=self.st)
    self.parent.w.create_line(self.p.x, self.p.y+40, self.p.x+32, self.p.y+20, fill=self.st)
    self.parent.arc(self.p.x+36, self.p.y+20, 4, 0, 360, self.st)
    if len(self.inputs) >= self.slots:
      pc = self.parent.getPowerColor(self.inputs[0], self.UUID)
      self.parent.w.create_line(self.p.x, self.p.y+20, self.p.x-10, self.p.y+20, fill=pc)
      x, y = self.parent.get(self.inputs[0]).xy()
      self.parent.w.create_line(x, y, self.p.x-9, self.p.y+20, fill=pc)
  def xy(self):
    return (self.p.x+self.s.w, self.p.y+self.s.h//2)

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
    self.w.bind('<ButtonRelease-1>', self.onrel1)
    self.w.bind('<B1-Motion>', self.motion1)
    self.w.bind('<Button 3>',self.onclick2)
    self.w.bind('<ButtonRelease-3>', self.onrel2)
    self.w.bind('<B3-Motion>', self.motion2)
    self.w.bind('<KeyPress>',self.onkey)
    self.w.pack()
    self.w.focus_set()
    self.in_motion = None
    self.click_moved = False
    self.selected = None
    self.rmx = -1
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
  def new(self, c, p, ins=None):
    e = c(self, p, ins=ins)
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
    if self.selected is not None and self.rmx != -1:
      t = self.get(self.selected)
      self.w.create_line(t.p.x+t.s.w//2, t.p.y+t.s.h//2, self.rmx, self.rmy)
    self.tk.update()
  def onclick1(self, ev):
    self.click_moved = False
    self.in_motion = None
    for e in self.UUIDS:
      if  ev.x >= e.p.x and ev.x <= e.p.x+e.s.w \
      and ev.y >= e.p.y and ev.y <= e.p.y+e.s.h:
        self.in_motion = e.UUID
  def onrel1(self,ev):
    if not self.click_moved:
      for e in self.UUIDS:
        if  ev.x >= e.p.x and ev.x <= e.p.x+e.s.w \
        and ev.y >= e.p.y and ev.y <= e.p.y+e.s.h:
          e.onclick1()
  def motion1(self, ev):
    self.click_moved = True
    if self.in_motion is not None:
      self.get(self.in_motion).motion(ev.x, ev.y)
  def onclick2(self, ev):
    self.click_moved = False
    self.selected = None
    for e in self.UUIDS:
      if  ev.x >= e.p.x and ev.x <= e.p.x+e.s.w \
      and ev.y >= e.p.y and ev.y <= e.p.y+e.s.h:
        self.selected = e.UUID
  def onrel2(self,ev):
    if not self.click_moved:
      for e in self.UUIDS:
        if  ev.x >= e.p.x and ev.x <= e.p.x+e.s.w \
        and ev.y >= e.p.y and ev.y <= e.p.y+e.s.h:
          e.onclick2()
    elif self.selected is not None:
      for e in self.UUIDS:
        if  ev.x >= e.p.x and ev.x <= e.p.x+e.s.w \
        and ev.y >= e.p.y and ev.y <= e.p.y+e.s.h:
          e.inputs += [self.selected]
          self.get(self.selected).outs += [e]
    self.rmx = -1
  def motion2(self, ev):
    self.click_moved = True
    self.rmx = ev.x
    self.rmy = ev.y
  def onkey(self, ev):
    print(ev)
    if ev.keycode > 111 and ev.keycode < 111+13:
      gates = [None, switch, light, NOTgate, ORgate, ANDgate]
      b = gates[ev.keycode-111]
      self.new(b, pos(ev.x-b.s.w//2, ev.y-b.s.h//2))
    if ev.keycode == 220:
      code.InteractiveConsole(vars()).interact()
    if ev.state == 0x40001:
      self.UUIDS = []
      self.UUIDi = 0
    for e in self.UUIDS:
      e.onkey(ev)

UUIDS = UUIDs()
s = 70
in1 = UUIDS.new(switch,pos(s,s))
in2 = UUIDS.new(switch,pos(s,2*s))
not1 = UUIDS.new(NOTgate,pos(2*s,s),[in1])
not2 = UUIDS.new(NOTgate,pos(2*s,2*s),[in2])
orc1 = UUIDS.new(ORgate,pos(3*s,1.5*s),[not1, not2])
or1 = UUIDS.new(ORgate,pos(4*s,s),[not1, orc1])
or2 = UUIDS.new(ORgate,pos(4*s,2*s),[orc1, not2])
no1 = UUIDS.new(NOTgate,pos(5*s,s),[or1])
no2 = UUIDS.new(NOTgate,pos(5*s,2*s),[or2])
orc2 = UUIDS.new(ORgate,pos(6*s,1.5*s),[no1, no2])
out = UUIDS.new(light, pos(7*s, 1.5*s), [orc2])
while 1:
  UUIDS.update()
  UUIDS.render()
code.InteractiveConsole(vars()).interact()
