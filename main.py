#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# file from https://github.com/Nircek/resistorer
# licensed under MIT license

# MIT License

# Copyright (c) 2018 Nircek

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import code
from tkinter import simpledialog, messagebox, filedialog
from tkinter import *
import math
from time import time, sleep
import copy
import pickle
from sys import argv

units = {'R': '\N{OHM SIGN}', 'U': 'V', 'I': 'A'}
def getUnit(what):
  if what in units:
    return units[what]
  return ''

class Primitive:
  def __init__(self, R):
    self.R = R
    self.U = None
  def __repr__(self):
    return '['+str(self.R)+']'
  def __str__(self):
    return self.__class__.__name__
  @property
  def cs(self): # components
    return []
  @property
  def I(self):
    return self._I
  @property
  def U(self):
    return self._U
  def updateR(self):
    pass
  def clearIU(self):
    self._I = None
    self._U = None
  @I.setter
  def I(self, x):
    if x is None:
      self.clearIU()
      return
    self._I = x
    self._U = self.R * x
    self.updateR()
  @U.setter
  def U(self, x):
    if x is None:
      self.clearIU()
      return
    self._U = x
    self._I = x / self.R
    self.updateR()

class Series(Primitive):
  def __init__(self, *args):
    self.data = args
  def __repr__(self):
    r = '+('
    for e in self.data:
      r += repr(e) + ', '
    if r != '+(':
      r = r[:-2]
    r += ')'
    return r
  @property
  def cs(self): # components
    return self.data
  @property
  def R(self):
    r = 0
    for e in self.data:
      r += e.R
    return r
  def updateR(self):
    for e in self.data:
      e.I = self.I

class Parallel(Primitive):
  def __init__(self, *args):
    self.data = args
  def __repr__(self):
    r = ':('
    for e in self.data:
      r += repr(e) + ', '
    if r != ':(':
      r = r[:-2]
    r += ')'
    return r
  @property
  def cs(self): # components
    return self.data
  @property
  def R(self):
    r = 0
    for e in self.data:
      r += 1/e.R
    return 1/r
  def updateR(self):
    for e in self.data:
      e.U = self.U

class Delta(Primitive):
  def __init__(self, x, y, z, i):
    self.x = x
    self.y = y
    self.z = z
    self.i = i
  def __repr__(self):
    r = '\N{GREEK CAPITAL LETTER DELTA}('
    r += repr(self.x) + ', '
    r += repr(self.y) + ', '
    r += repr(self.z) + ', '
    r += repr(self.i) + ')'
    return r
  @property
  def cs(self): # components
    return [self.x,self.y,self.z]
  @property
  def R(self):
    r = {
      1: self.x.R*self.y.R,
      2: self.x.R*self.z.R,
      3: self.y.R*self.z.R
    }[self.i]
    r /= self.x.R+self.y.R+self.z.R
    return r

class Nodes:
  def __init__(self):
    self.nodes = []
    self.nv = []
  def resetNode(self):
    self.nodes = []
  def searchNode(self,x,y):
    for i in range(len(self.nodes)):
      if (x,y) in self.nodes[i]:
        return i
    return -1
  def addNode(self,x,y,x2=-1,y2=-1):
    a = self.searchNode(x,y)
    b = self.searchNode(x2,y2)
    i = -1
    if a == -1 and b == -1:
      i = len(self.nodes)
      self.nodes += [[]]
    elif (a == -1) + (b == -1) == 1:
      i = a + b + 1 # a or b
    elif a != b:
      c = min(a,b)
      d = max(a,b)
      self.nodes[c] += self.nodes[d]
      del self.nodes[d]
      return
    if not (((x,y) in self.nodes[i]) or x == -1 or y == -1):
      self.nodes[i] += [(x,y)]
    if not ((x2,y2) in self.nodes[i] or x2 == -1 or y2 == -1):
      self.nodes[i] += [(x2,y2)]
  def interpret(self, data, start, end):
    # -----
    def datasearch(a, b=-1): # search for all resistors connecting a and b
      r = []
      for i in range(len(data)):
        if data[i].a == a:
          if data[i].b == b or b == -1:
            r += [i]
        elif data[i].b == a:
          if data[i].a == b or b == -1:
            r += [i]
      return r
    n = lambda i, l: data[i].a+data[i].b-l # i. resistor connects l and ... nodes
    def without(arr):
      r = []
      for e in range(len(data)):
        if not e in arr:
          r += [data[e]]
      return r
    def processDelta():
      for i in range(len(self.nodes)):
        for a in datasearch(i):
          an = n(a, i)
          for b in datasearch(an):
            bn = n(b, an)
            for c in datasearch(bn):
              cn = n(c,bn)
              if cn == i:
                #print(i,an,bn,cn,data[a],data[b],data[c])
                ndata = without((a,b,c))
                da = Delta(data[a], data[b], data[c], 1)
                db = Delta(data[a], data[b], data[c], 2)
                dc = Delta(data[a], data[b], data[c], 3)
                da.a, db.a, dc.a = an, cn, bn
                da.b, db.b, dc.b = len(self.nodes), len(self.nodes), len(self.nodes)
                ndata += [da, db, dc]
                return ndata
      return None
    def processSeries():
      for i in range(len(self.nodes)):
        if i != start and i != end:
          d = datasearch(i)
          if len(d) == 2:
            ndata = without(d)
            nn = Series(data[d[0]], data[d[1]])
            nn.a, nn.b = n(d[0], i), n(d[1], i)
            ndata += [nn]
            return ndata
      return None
    def processParallel():
      for e in range(len(data)):
        for f in range(len(data)):
          if e != f and (data[e].a == data[f].a and data[e].b == data[f].b) or (data[e].a == data[f].b and data[e].b == data[f].a):
            ndata = without((e,f))
            nn = Parallel(data[e], data[f])
            nn.a, nn.b = data[e].a, data[e].b
            ndata += [nn]
            return ndata
      return None
    def processUnnecessary():
      rmvd = []
      for i in range(len(self.nodes)):
        if i != start and i != end:
          a = datasearch(i)
          if len(a) == 1:
            rmvd += a
      for i in range(len(data)):
        if data[i].a == data[i].b:
          rmvd += [i]
      return without(rmvd) if rmvd else None
    # -----
    toProcess = [processUnnecessary, processSeries, processParallel, processDelta]
    odata = []
    q = lambda x: x if (not x is None) else data
    while odata != data:
      odata = data[:]
      #print(odata)
      for i in range(len(toProcess)):
        r = toProcess[i]()
        if not r is None:
          data = r
          if toProcess[i] == processDelta:
            self.nodes += [[]]
          break
    if not data:
      if start == end:
        return Primitive(0)
      return Primitive(math.inf)
    if len(data) == 1:
      return data[0]
    raise Error()
  def calc_voltages(self, c, v, x): # calced
    if str(c) == 'Primitive':
      return
    def cv(p, d): # calc voltage(parent, data)
      if str(d) == 'Primitive':
        return
      r = False
      for e in d.cs:
        r = cv(p,e)
      if (not d.U is None) and ((p.nv[d.a] is None) != (p.nv[d.b] is None)) and d.a != c.b and d.b != c.b: # '!=' = 'xor'
        if p.nv[d.a] is None:
          p.nv[d.a] = p.nv[d.b] + d.U
        else:
          p.nv[d.b] = p.nv[d.a] + d.U
        return True
      elif d.U is None and (not ((p.nv[d.a] is None) or (p.nv[d.b] is None))):
        d.U = abs(p.nv[d.a]-p.nv[d.b])
        return True
      return r
    self.nv = []
    for e in range(len(self.nodes)):
      self.nv += [None]
    self.nv[c.a] = 0
    #nv[c.b] = u
    if v:
      c.U = x
    else:
      c.I = x
    while cv(self, c):
      pass

class pos:
  def __init__(self, *a):
    while len(a) == 1:
      a = a[0]
    self.x = int(a[0])
    self.y = int(a[1])
    if len(a) > 2:
      self.p = int(a[2])
    else:
      self.p = -1
  @property
  def r(self):
    return (self.x, self.y, self.p)
  @property
  def q(self):
    return (self.x, self.y)
  @r.setter
  def r(self, r):
    self.x, self.y, self.p = r
  @q.setter
  def q(self, q):
    self.x, self.y = q
  def __repr__(self):
    if self.p == -1:
      return 'pos'+repr(self.q)
    else:
      return 'pos'+repr(self.r)

def ttoposa(t):  # tel (two element) to pos A
  return pos(t.x, t.y)

def ttoposb(t):
  if t.p == 0:
    return pos(t.x+1, t.y)
  else:
    return pos(t.x, t.y+1)

def pround(x, y, s, xy):
  if xy == 2:
    x /= s
    y /= s
    sx = x%1-0.5
    sy = y%1-0.5
    x //= 1
    y //= 1
    if abs(sx) > abs(sy):
      if sx < 0:
        return pos(x, y, 1)
      else:
        return pos(x+1, y, 1)
    else:
      if sy < 0:
        return pos(x, y, 0)
      else:
        return pos(x, y+1, 0)
  else:
    x = ((x+0.5*s)//s)
    y = ((y+0.5*s)//s)
    return pos(x, y)

class element:
  xy = 1
  def __str__(self):
    return self.__class__.__name__
  def __init__(self, parent):
    self.addr = super().__repr__().split('0x')[1][:-1]
    self.parent = parent
  @property
  def info(self):
    return {}
  def __repr__(self):
    return str(vars(self))
  def render(self, x, y, s):
    self.parent.w.create_rectangle(x, y, x+s, y+s)
  def onkey(self, ev):
    pass

class apin(element):
  xy = 1
  def __init__(self, parent):
    self.parent = parent
    d = []
    for e in self.parent.oels.keys():
      if str(self.parent.oels[e]) == 'apin':
        d += [e]
    for e in d:
      del self.parent.oels[e]
  def render(self, x, y, s):
    r = s*0.1
    self.parent.w.create_arc(x-r,y-r,x+r,y+r,start=0,extent=180,outline='blue',fill='green')
    self.parent.w.create_arc(x-r,y-r,x+r,y+r,start=180,extent=180,outline='blue',fill='green')
    r *= 2
    self.parent.w.create_arc(x-r,y-r,x+r,y+r,start=0,extent=180,outline='blue',style=ARC)
    self.parent.w.create_arc(x-r,y-r,x+r,y+r,start=180,extent=180,outline='blue',style=ARC)
    
class bpin(element):
  xy = 1
  def __init__(self, parent):
    self.parent = parent
    d = []
    for e in self.parent.oels.keys():
      if str(self.parent.oels[e]) == 'bpin':
        d += [e]
    for e in d:
      del self.parent.oels[e]
  def render(self, x, y, s):
    r = s*0.1
    self.parent.w.create_arc(x-r,y-r,x+r,y+r,start=0,extent=180,outline='red',fill='red')
    self.parent.w.create_arc(x-r,y-r,x+r,y+r,start=180,extent=180,outline='red',fill='red')
    r *= 2
    self.parent.w.create_arc(x-r,y-r,x+r,y+r,start=0,extent=180,outline='red',style=ARC)
    self.parent.w.create_arc(x-r,y-r,x+r,y+r,start=180,extent=180,outline='red',style=ARC)

class wire(element):
  xy = 2
  def render(self, x, y, s, p):
    self.parent.w.create_line(x, y, x if p == 1 else (x + s), y if p == 0 else (y + s))
  @property
  def R(self):
    return 0

resistor_i = 1

class resistor(element, Primitive):
  xy = 2
  oR = None
  def __init__(self, parent, i=None):
    self.parent = parent
    if i is None:
      global resistor_i
      i = resistor_i
      resistor_i += 1
    self.i = i
    self.getR()
  def getR(self):
    a = None
    while a is None:
      a = resistor.oR
      a = self.parent.getFloat("Value of R" + str(self.i) + " [" + getUnit('R') + "]")
    resistor.oR = a
    self.R = a
  @property
  def info(self):
    if (not self.I is None) and (not self.U is None):
      return {'R': self.R, 'U': self.U, 'I': self.I}
    else:
      return {'R': self.R}
  def __repr__(self):
    return '{'+str(self.i)+'}'
  def render(self, x, y, s, p):
    if p == 0:
      self.parent.w.create_line(x,y,x+0.25*s,y)
      self.parent.w.create_line(x+0.75*s,y,x+s,y)
      self.parent.w.create_line(x+0.25*s,y+0.2*s,x+0.75*s,y+0.2*s)
      self.parent.w.create_line(x+0.25*s,y-0.2*s,x+0.75*s,y-0.2*s)
      self.parent.w.create_line(x+0.25*s,y+0.2*s,x+0.25*s,y-0.2*s)
      self.parent.w.create_line(x+0.75*s,y+0.2*s,x+0.75*s,y-0.2*s)
      self.parent.w.create_text(x+0.5*s,y,text=str(self.i))
    if p == 1:
      self.parent.w.create_line(x,y,x,y+0.25*s)
      self.parent.w.create_line(x,y+0.75*s,x,y+s)
      self.parent.w.create_line(x+0.2*s,y+0.25*s,x+0.2*s,y+0.75*s)
      self.parent.w.create_line(x-0.2*s,y+0.25*s,x-0.2*s,y+0.75*s)
      self.parent.w.create_line(x+0.2*s,y+0.25*s,x-0.2*s,y+0.25*s)
      self.parent.w.create_line(x+0.2*s,y+0.75*s,x-0.2*s,y+0.75*s)
      self.parent.w.create_text(x,y+0.5*s,text=str(self.i), angle=270)

class Board:
  def __init__(self, WIDTH=1280, HEIGHT=720, s=40):
    self.SIZE = pos(WIDTH, HEIGHT)
    self.s = s  # size of one element
    self.tels = {}  # elements with (x, y, p)
    self.oels = {}  # elements with (x, y)
    self.tk = Tk()
    self.w = Canvas(self.tk, width=WIDTH, height=HEIGHT, bd=0, highlightthickness=0)
    self.me = [self]
    self.makeTk()
    self.w.pack(expand=True)
    self.w.focus_set()
    self.in_motion = pos(-1,-1)
    self.shift = pos(0, 0)
    self.newpos = pos(0, 0)
    self.newself = False
    self.x = 0
    self.y = 0
    self.nodes = Nodes()
    self.lastfile = None
    self.queue = []
    self.powerv = True # power voltage
    self.power = 12
    self.crc = Primitive(math.inf) # CiRCuit :D easy to remember
  def setPower(self, v, x):
    self.powerv = v
    self.power = x
  def withClick(self, x):
    self.queue += [x]
  def configure(self, ev):
    self.SIZE.x = ev.width
    self.SIZE.y = ev.height
    self.w.config(width=ev.width, height=ev.height)
  def dump(self):
    a, b = self.tk, self.w
    self.tk, self.w = 0, 0
    r = pickle.dumps(self)
    self.tk, self.w = a, b
    return r
  def makeTk(self):
    self.w.bind('<Button 1>', self.onclick1)
    self.w.bind('<ButtonRelease-1>', self.onrel1)
    self.w.bind('<B1-Motion>', self.motion1)
    self.w.bind('<KeyPress>', self.onkey)
    self.tk.bind('<Configure>', self.configure)
    #-----
    mb = Menu(self.tk)
    fm = Menu(mb, tearoff=0)
    fm.add_command(label='New', command=self.newSketch)
    fm.add_command(label='Open', command=self.open)
    fm.add_command(label='Save', command=self.save)
    fm.add_command(label='Save as...', command=lambda:self.save(-1))
    fm.add_separator()
    fm.add_command(label='Exit', command=self.tk.destroy)
    mb.add_cascade(label='File', menu=fm)
    #-----
    em = Menu(mb, tearoff=0)
    ae = lambda t: lambda:self.withClick(lambda p:self.new(t,p[0],p[1])) # add element
    em.add_command(label='Add a wire', command=ae(wire))
    em.add_command(label='Add a resistor', command=ae(resistor))
    em.add_command(label='Add a apin', command=ae(apin))
    em.add_command(label='Add a bpin', command=ae(bpin))
    em.add_separator()
    em.add_command(label='Delete element', command=lambda:self.withClick(lambda p:self.delete(p[0],p[1])))
    em.add_command(label='Delete all', command=self.newSketch)
    mb.add_cascade(label='Edit', menu=em)
    #-----
    vm = Menu(mb, tearoff=0)
    vm.add_command(label='Zoom in', command=lambda:self.zoom(+1))
    vm.add_command(label='Zoom out', command=lambda:self.zoom(-1))
    vm.add_command(label='Count resistors', command=self.count)
    mb.add_cascade(label='View', menu=vm)
    #-----
    pm = Menu(mb, tearoff=0)
    pm.add_command(label='Voltage', command=lambda:self.setPower(True, self.getFloat('Voltage ['+getUnit('U')+']')))
    pm.add_command(label='Current', command=lambda:self.setPower(False, self.getFloat('Current ['+getUnit('I')+']')))
    mb.add_cascade(label='Power supply', menu=pm)
    #-----
    dm = Menu(mb, tearoff=0)
    dm.add_command(label='Open a console', command=self.interactive)
    self.auto = BooleanVar()
    self.auto.set(True)
    dm.add_checkbutton(label="Auto calculating", onvalue=True, offvalue=False, variable=self.auto)
    mb.add_cascade(label='Debug', menu=dm)
    #-----
    self.tk.config(menu=mb)
  def load(self, data):
    a, b = self.tk, self.w
    r = pickle.loads(data)
    r.tk, r.w = a, b
    r.makeTk()
    self.newself = r
  def open(self, file=None):
    if file is None:
      file = filedialog.askopenfilename(filetypes=(('sketch files','*.sk'),('all files','*.*')))
    if not file:
      return False
    f = open(file, mode='rb')
    self.load(f.read())
    f.close()
    self.newself.lastfile = file
    return True
  def save(self, file=None): # file=-1 for force asking
    if (file is None) and (not self.lastfile is None):
      file = self.lastfile
    elif (file is None) or (file == -1):
      file = filedialog.asksaveasfilename(filetypes=(('sketch files','*.sk'),('all files','*.*')))
    if not file:
      return False
    f = open(file, mode='wb')
    f.write(self.dump())
    self.lastfile = file
    f.close()
    return True
  def new(self, cl, x, y):
    if cl.xy == 2:
      p = pround(x, y, self.s, 2)
      self.tels[p.r] = cl(self)
    if cl.xy == 1:
      p = pround(x, y, self.s, 1)
      self.oels[p.q] = cl(self)
  def point(self, p):
    self.w.create_oval(p.x, p.y, p.x, p.y, width = 1, fill = 'black')
  def render(self):
    self.w.delete('all')
    for x in range(self.x//self.s, (self.SIZE.x+self.x)//self.s+1):
      for y in range(self.y//self.s, (self.SIZE.y+self.y)//self.s+1):
        self.point(pos(x*self.s-self.x, y*self.s-self.y))
    txt = ''
    for p, e in self.tels.items():
      if str(e) == 'resistor':
        txt += repr(e)
        first = True
        for f, g in e.info.items():
          if first:
            first = False
          else:
            txt += len(repr(e))*' '
          txt += ' ' + f + '=' + str(g) + ' ' + getUnit(f) + '\n'
        if txt[-1] != '\n':
          txt += '\n'
      p = pos(p)
      if p.r != self.in_motion.r:
        e.render(p.x*self.s-self.x, p.y*self.s-self.y, self.s, p.p)
      else:
        e.render(self.newpos.x-self.shift.x, self.newpos.y-self.shift.y, self.s, p.p)
    self.w.create_text(0,self.SIZE.y,font='TkFixedFont',anchor='sw',text=txt)
    for p, e in self.oels.items():
      p = pos(p)
      e.render(p.x*self.s-self.x, p.y*self.s-self.y, self.s)
    self.tk.update_idletasks()
    self.tk.update()
    if self.auto.get():
      self.calc()
    if self.newself:
      return self.newself
    return self
  def onclick1(self, ev):
    if self.queue:
      self.queue[0]((ev.x, ev.y))
      self.queue = self.queue[1:]
    self.in_motion = pround(ev.x+self.x, ev.y+self.y, self.s, 2)
    self.shift = pos(ev.x+self.x-self.in_motion.x*self.s, ev.y+self.y-self.in_motion.y*self.s)
    self.newpos = pos(ev.x, ev.y)
  def onrel1(self, ev):
    if self.in_motion.r in self.tels.keys() and pround(ev.x+self.x, ev.y+self.y, self.s, 2).r != self.in_motion.r:
      self.tels[pround(ev.x+self.x, ev.y+self.y, self.s, 2).r] = self.tels[self.in_motion.r]
      self.tels.pop(self.in_motion.r)
    self.in_motion = pos(-1, -1)
    self.shift = pos(-1,-1)
  def motion1(self, ev):
    self.newpos = pos(ev.x, ev.y)
  def updateNode(self):
    self.nodes.resetNode()
    for e in self.oels:
      self.nodes.addNode(e[0], e[1])
    for e in self.tels:
      if str(self.tels[e]) == 'wire':
        a = ttoposa(pos(e))
        b = ttoposb(pos(e))
        self.nodes.addNode(a.x,a.y,b.x,b.y)
      else:
        a = ttoposa(pos(e))
        b = ttoposb(pos(e))
        self.nodes.addNode(a.x,a.y)
        self.nodes.addNode(b.x,b.y)
  def calc_res(self): # calc resistorers
    self.updateNode()
    r = []
    for e in self.tels:
      if str(self.tels[e]) == 'resistor':
        a=ttoposa(pos(e))
        b=ttoposb(pos(e))
        a=self.nodes.searchNode(a.x, a.y)
        b=self.nodes.searchNode(b.x, b.y)
        self.tels[e].a = a
        self.tels[e].b = b
        r += [self.tels[e]]
    return r
  def calc(self):
    b = self.calc_res()
    start = end = -1
    for e in self.tels.values():
      e.U = None
    for e in self.oels.keys():
      if str(self.oels[e]) == 'apin':
        start = self.nodes.searchNode(e[0],e[1])
      if str(self.oels[e]) == 'bpin':
        end = self.nodes.searchNode(e[0],e[1])
    if start == -1 or end == -1:
      if not self.auto.get():
        messagebox.showerror('Error', 'NO PINS SPECIFIED')
      self.crc = Primitive(math.inf)
      return
    a = self.calc_res()
    a = self.nodes.interpret(a, start, end)
    if not self.auto.get():
      messagebox.showinfo('Result', repr(a))
      messagebox.showinfo('Result', repr(a.R))
    self.crc = a
    self.nodes.calc_voltages(a, self.powerv, self.power)
  def newSketch(self):
      self.tels = {}
      self.oels = {}
  def count(self):
    global resistor_i
    resistor_i = 1
    for e in self.tels.values():
      if str(e) is 'resistor':
        e.i = resistor_i
        resistor_i += 1
  def zoom(self, x):
    s = self.s
    self.s += x
    self.x += self.x//s
    self.y += self.y//s
  def interactive(self):
      code.InteractiveConsole(vars()).interact()
  def delete(self, x, y):
    if pround(x, y, self.s, 2).r in self.tels.keys():
      del self.tels[pround(x, y, self.s, 2).r]
    if pround(x, y, self.s, 1).q in self.oels.keys():
      del self.oels[pround(x, y, self.s, 1).q]
  def onkey(self, ev):
    #print(ev, ev.state)
    ev.x += self.x
    ev.y += self.y
    if len(ev.keysym)>1 and ev.keysym[:1] == 'F':
      nr = int(ev.keysym[1:])-1
      gates = [element, wire, resistor, apin, bpin]
      if len(gates) <= nr:
        messagebox.showerror('Error', 'NO F'+str(nr+1)+' ELEMENT')
      else:
        b = gates[nr]
        self.new(b, ev.x, ev.y)
    if ev.keysym == 'slash':
      self.calc()
    if ev.keysym == 'backslash':
      self.interactive()
    if ev.keysym == 'apostrophe' or ev.keysym == 'quoteright':
      self.count()
    if (ev.state&1)!=0 and ev.keysym == 'Delete':  # shift + del
      self.newSketch()
    if ev.keysym == 'plus':
      self.zoom(+1)
    if ev.keysym == 'minus':
      self.zoom(-1)
    if ev.keysym == 'Left':
      self.x -= 1
    if ev.keysym == 'Right':
      self.x += 1
    if ev.keysym == 'Up':
      self.y -= 1
    if ev.keysym == 'Down':
      self.y += 1
    if ev.keysym == 'Delete':
      self.delete(ev.x, ev.y)
    if pround(ev.x, ev.y, self.s, 2).r in self.tels.keys():
        self.tels[pround(ev.x, ev.y, self.s, 2).r].onkey(ev)
    if pround(ev.x, ev.y, self.s, 1).q in self.oels.keys():
        self.oels[pround(ev.x, ev.y, self.s, 1).q].onkey(ev)
  def getFloat(self, msg):
    a = simpledialog.askfloat("Input", msg, parent=self.tk, minvalue=0.0)
    self.w.focus_set()
    return a

if __name__ == '__main__':
  board = Board()
  if len(argv) > 1:
    board.open(argv[1])
  if True:#try:
    while 1:
      t = time()
      while t+0.2 > time():
        board = board.render()
  #except TclError:
    # window exit
    pass
  # code.InteractiveConsole(vars()).interact()
