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
from tkinter import simpledialog, messagebox
from tkinter import *
import math
from time import time, sleep
import copy
import pickle

class Primitive:
  def __init__(self, R):
    self.R = R
  def __repr__(self):
    return '['+str(self.R)+']'

class Series(Primitive):
  def __init__(self, *args):
    self.data = args
  def __repr__(self):
    r = '+('
    for e in self.data:
      r += repr(e) + ', '
    r = r[:-2] + ')'
    return r
  @property
  def R(self):
    r = 0
    for e in self.data:
      r += e.R
    return r

class Parallel(Primitive):
  def __init__(self, *args):
    self.data = args
  def __repr__(self):
    r = ':('
    for e in self.data:
      r += repr(e) + ', '
    r = r[:-2] + ')'
    return r
  @property
  def R(self):
    r = 0
    for e in self.data:
      r += 1/e.R
    return 1/r

class Delta(Primitive):
  def __init__(self, a, b, c, i):
    self.a = a
    self.b = b
    self.c = c
    self.i = i
  def __repr__(self):
    r = '\N{GREEK CAPITAL LETTER DELTA}('
    r += repr(self.a) + ', '
    r += repr(self.b) + ', '
    r += repr(self.c) + ', '
    r += repr(self.i) + ')'
    return r
  @property
  def R(self):
    r = {
      1: self.a.R*self.b.R,
      2: self.a.R*self.c.R,
      3: self.b.R*self.c.R
    }[self.i]
    r /= self.a.R+self.b.R+self.c.R
    return r

def interpret(data, start, end):
  ns = nodes[:]
  l = len(ns)
  # -----
  def datasearch(a, b=-1): # search for all resistors connecting a and b
    r = []
    for i in range(len(data)):
      if data[i][0] == a:
        if data[i][2] == b or b == -1:
          r += [i]
      elif data[i][2] == a:
        if data[i][0] == b or b == -1:
          r += [i]
    return r
  n = lambda i, l: data[i][0]+data[i][2]-l # i. resistor connects l and ... nodes
  def without(arr):
    r = []
    for e in range(len(data)):
      if not e in arr:
        r += [data[e]]
    return r
  def processDelta():
    for i in range(l):
      for a in datasearch(i):
        an = n(a, i)
        for b in datasearch(an):
          bn = n(b, an)
          for c in datasearch(bn):
            cn = n(c,bn)
            if cn == i:
              #print(i,an,bn,cn,data[a],data[b],data[c])
              ndata = without((an,bn,cn))
              ndata += [[an, Delta(data[a][1], data[b][1], data[c][1], 1), l]]
              ndata += [[cn, Delta(data[a][1], data[b][1], data[c][1], 2), l]]
              ndata += [[bn, Delta(data[a][1], data[b][1], data[c][1], 3), l]]
              return ndata
    return None
  def processSeries():
    for i in range(l):
      if i != start and i != end:
        d = datasearch(i)
        if len(d) == 2:
          a, b = n(d[0], i), n(d[1], i)
          print(a,b)
          ndata = without(d)
          ndata += [[a, Series(data[d[0]][1], data[d[1]][1]), b]]
          return ndata
    return None
  # -----
  r = processDelta()
  if not r is None:
    ns += [[]]
    data = r
  r = processSeries()
  data = r if (not r is None) else data
  r = processSeries()
  data = r if (not r is None) else data
  print(data)
  return Series(data[0][1],Parallel(data[1][1],data[2][1]))

nodes = []
def resetNode():
  global nodes
  nodes = []

def searchNode(x,y):
  global nodes
  for i in range(len(nodes)):
    if (x,y) in nodes[i]:
      return i
  return -1

def addNode(x,y,x2=-1,y2=-1):
  global nodes
  a = searchNode(x,y)
  b = searchNode(x2,y2)
  i = -1
  if a == -1 and b == -1:
    i = len(nodes)
    nodes += [[]]
  elif (a == -1) + (b == -1) == 1:
    i = a + b + 1 # a or b
  elif a != b:
    c = min(a,b)
    d = max(a,b)
    nodes[c] += nodes[d]
    del nodes[d]
    return
  if not (((x,y) in nodes[i]) or x == -1 or y == -1):
    nodes[i] += [(x,y)]
  if not ((x2,y2) in nodes[i] or x2 == -1 or y2 == -1):
    nodes[i] += [(x2,y2)]

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
    return 'element'
  def __init__(self, parent):
    self.addr = super().__repr__().split('0x')[1][:-1]
    self.parent = parent
  def __repr__(self):
    return str(vars(self))
  def render(self, x, y, s):
    self.parent.w.create_rectangle(x, y, x+s, y+s)
  def onkey(self, ev):
    pass

class apin(element):
  xy = 1
  def __str__(self):
    return 'apin'
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
    self.parent.w.create_arc(x-r,y-r,x+r,y+r,start=0,extent=180,outline='green',fill='green')
    self.parent.w.create_arc(x-r,y-r,x+r,y+r,start=180,extent=180,outline='green',fill='green')
    r *= 2
    self.parent.w.create_arc(x-r,y-r,x+r,y+r,start=0,extent=180,outline='green',style=ARC)
    self.parent.w.create_arc(x-r,y-r,x+r,y+r,start=180,extent=180,outline='green',style=ARC)
    
class bpin(element):
  xy = 1
  def __str__(self):
    return 'bpin'
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
  def __str__(self):
    return 'wire'
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
      a = self.parent.getFloat("Type R" + str(self.i))
    resistor.oR = a
    self.R = a
  def __str__(self):
    return 'resistor'
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
    self.WIDTH = WIDTH
    self.HEIGHT = HEIGHT
    self.s = s  # size of one element
    self.tels = {}  # elements with (x, y, p)
    self.oels = {}  # elements with (x, y)
    self.tk = Tk()
    self.w = Canvas(self.tk, width=WIDTH, height=HEIGHT)
    self.w.bind('<Button 1>', self.onclick1)
    self.w.bind('<ButtonRelease-1>', self.onrel1)
    self.w.bind('<B1-Motion>', self.motion1)
    self.w.bind('<KeyPress>', self.onkey)
    self.w.pack()
    self.w.focus_set()
    self.in_motion = pos(-1,-1)
    self.click_moved = False
    self.first_click = None
    self.shift = pos(0, 0)
    self.newself = False
  def dump(self):
    a, b = self.tk, self.w
    self.tk, self.w = 0, 0
    r = pickle.dumps(self)
    self.tk, self.w = a, b
    return r
  def load(self, data):
    a, b = self.tk, self.w
    r = pickle.loads(data)
    r.tk, r.w = a, b
    r.w.bind('<Button 1>', r.onclick1)
    r.w.bind('<ButtonRelease-1>', r.onrel1)
    r.w.bind('<B1-Motion>', r.motion1)
    r.w.bind('<KeyPress>', r.onkey)
    self.newself = r
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
    for x in range(self.WIDTH//self.s):
      for y in range(self.HEIGHT//self.s):
        self.point(pos(x*self.s, y*self.s))
    for p, e in self.tels.items():
      p = pos(p)
      if p.r != self.in_motion.r:
        e.render(p.x*self.s, p.y*self.s, self.s, p.p)
      else:
        e.render(p.x*self.s+self.shift.x, p.y*self.s+self.shift.y, self.s, p.p)
    for p, e in self.oels.items():
      p = pos(p)
      e.render(p.x*self.s, p.y*self.s, self.s)
    self.tk.update()
    if self.newself:
      return self.newself
    return self
  def onclick1(self, ev):
    self.click_moved = False
    self.in_motion = pround(ev.x, ev.y, self.s, 2)
    #print(self.in_motion)
    self.first_click = pos(ev.x, ev.y)
  def onrel1(self, ev):
    if self.click_moved:
      if self.in_motion.r in self.tels.keys() and pround(ev.x, ev.y, self.s, 2).r != self.in_motion.r:
        self.tels[pround(ev.x, ev.y, self.s, 2).r] = self.tels[self.in_motion.r]
        self.tels.pop(self.in_motion.r)
    self.in_motion = pos(-1, -1)
    self.shift = pos(0,0)
  def motion1(self, ev):
    self.click_moved = True
    self.shift = pos(ev.x-self.first_click.x, ev.y-self.first_click.y)
  def updateNode(self):
    resetNode()
    for e in self.oels:
      addNode(e[0], e[1])
    for e in self.tels:
      if str(self.tels[e]) == 'wire':
        a = ttoposa(pos(e))
        b = ttoposb(pos(e))
        addNode(a.x,a.y,b.x,b.y)
      else:
        a = ttoposa(pos(e))
        b = ttoposb(pos(e))
        addNode(a.x,a.y)
        addNode(b.x,b.y)
    return nodes
  def calc_res(self): # calc resistorers
    self.updateNode()
    r = []
    for e in self.tels:
      if str(self.tels[e]) == 'resistor':
        a=ttoposa(pos(e))
        b=ttoposb(pos(e))
        a=searchNode(a.x, a.y)
        b=searchNode(b.x, b.y)
        r += [[a, self.tels[e], b]]
    return r
  def calc(self):
    b = self.calc_res()
    start = end = -1
    for e in self.oels.keys():
      if str(self.oels[e]) == 'apin':
        start = searchNode(e[0],e[1])
      if str(self.oels[e]) == 'bpin':
        end = searchNode(e[0],e[1])
    if start == -1 or end == -1:
      messagebox.showerror('Error', 'NO PINS SPECIFIED')
      return
    a = self.calc_res()
    a = interpret(a, start, end)
    messagebox.showinfo('Result', repr(a))
    messagebox.showinfo('Result', repr(a.R))

  def onkey(self, ev):
    print(ev)
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
      code.InteractiveConsole(vars()).interact()
    if ev.keysym == 'apostrophe' or ev.keysym == 'quoteright':
      global resistor_i
      resistor_i = 1
      for e in self.tels.values():
        if str(e) is 'resistor':
          e.i = resistor_i
          resistor_i += 1
    if (ev.state&1)!=0 and ev.keysym == 'Delete':  # shift + del
      self.tels = {}
      self.oels = {}
    if ev.keysym == 'plus':
      self.s += 1
    if ev.keysym == 'minus':
      self.s -= 1
    if pround(ev.x, ev.y, self.s, 2).r in self.tels.keys():
      if ev.keysym == 'Delete':
        del self.tels[pround(ev.x, ev.y, self.s, 2).r]
      else:
        self.tels[pround(ev.x, ev.y, self.s, 2).r].onkey(ev)
    if pround(ev.x, ev.y, self.s, 1).q in self.oels.keys():
      if ev.keysym == 'Delete':
        del self.oels[pround(ev.x, ev.y, self.s, 1).q]
      else:
        self.oels[pround(ev.x, ev.y, self.s, 1).q].onkey(ev)
  def getFloat(self, msg):
    a = simpledialog.askfloat("Input", msg, parent=self.tk, minvalue=0.0)
    self.w.focus_set()
    return a

if __name__ == '__main__':
  board = Board()
  board.load(b'\x80\x03c__main__\nBoard\nq\x00)\x81q\x01}q\x02(X\x05\x00\x00\x00WIDTHq\x03M\x00\x05X\x06\x00\x00\x00HEIGHTq\x04M\xd0\x02X\x01\x00\x00\x00sq\x05K(X\x04\x00\x00\x00telsq\x06}q\x07(K\x04K\x07K\x00\x87q\x08c__main__\nresistor\nq\t)\x81q\n}q\x0b(X\x06\x00\x00\x00parentq\x0ch\x01X\x01\x00\x00\x00iq\rK\x01X\x01\x00\x00\x00Rq\x0eG@$\x00\x00\x00\x00\x00\x00ubK\x05K\x07K\x00\x87q\x0fh\t)\x81q\x10}q\x11(h\x0ch\x01h\rK\x02h\x0eG@4\x00\x00\x00\x00\x00\x00ubK\x05K\x07K\x01\x87q\x12h\t)\x81q\x13}q\x14(h\x0ch\x01h\rK\x03h\x0eG@$\x00\x00\x00\x00\x00\x00ubK\x04K\x08K\x00\x87q\x15h\t)\x81q\x16}q\x17(h\x0ch\x01h\rK\x04h\x0eG@$\x00\x00\x00\x00\x00\x00ubK\x05K\x08K\x00\x87q\x18h\t)\x81q\x19}q\x1a(h\x0ch\x01h\rK\x05h\x0eG@>\x00\x00\x00\x00\x00\x00ubK\x04K\x07K\x01\x87q\x1bc__main__\nwire\nq\x1c)\x81q\x1d}q\x1e(X\x04\x00\x00\x00addrq\x1fX\x0c\x00\x00\x007f10933b85c0q h\x0ch\x01ubK\x06K\x07K\x01\x87q!h\x1c)\x81q"}q#(h\x1fX\x0c\x00\x00\x007f10933b8470q$h\x0ch\x01ubuX\x04\x00\x00\x00oelsq%}q&(K\x04K\x08\x86q\'c__main__\napin\nq()\x81q)}q*h\x0ch\x01sbK\x06K\x08\x86q+c__main__\nbpin\nq,)\x81q-}q.h\x0ch\x01sbuX\x02\x00\x00\x00tkq/K\x00X\x01\x00\x00\x00wq0K\x00X\t\x00\x00\x00in_motionq1c__main__\npos\nq2)\x81q3}q4(X\x01\x00\x00\x00xq5J\xff\xff\xff\xffX\x01\x00\x00\x00yq6J\xff\xff\xff\xffX\x01\x00\x00\x00pq7J\xff\xff\xff\xffubX\x0b\x00\x00\x00click_movedq8\x88X\x0b\x00\x00\x00first_clickq9h2)\x81q:}q;(h5M\xc2\x01h6M{\x01h7J\xff\xff\xff\xffubX\x05\x00\x00\x00shiftq<h2)\x81q=}q>(h5K\x00h6K\x00h7J\xff\xff\xff\xffubX\x07\x00\x00\x00newselfq?\x89ub.')
  if True:#try:
    while 1:
      t = time()
      while t+0.2 > time():
        board = board.render()
  #except TclError:
    # window exit
    pass
  # code.InteractiveConsole(vars()).interact()
