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
from tkinter import *
import math
from time import time

class pos:
  def __init__(self, *a):
    if len(a) == 1:
      a = a[0]
    self.x = a[0]
    self.y = a[1]
    if len(a) > 2:
      self.p = a[2]
    else:
      self.p = -1
    self.r = (self.x, self.y, self.p)
  def __repr__(self):
    return repr(self.r)


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
    x = ((x+0.5)//s)
    y = ((y+0.5)//s)
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

resistor_i = 1

class resistor(element):
  xy = 2
  def __init__(self, parent, i=None):
    self.parent = parent
    if i is None:
      global resistor_i
      i = resistor_i
      resistor_i += 1
    self.i = i
  def __str__(self):
    return 'resistor'
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
    self.w.bind('<KeyPress>',self.onkey)
    self.w.pack()
    self.w.focus_set()
    self.in_motion = pos(-1,-1)
    self.click_moved = False
    self.first_click = None
    self.shift = pos(0, 0)
  def new(self, cl, x, y):
    if cl.xy == 2:
      p = pround(x, y, self.s, 2)
      self.tels[p.r] = cl(self)
    if cl.xy == 1:
      p = pround(x, y, self.s, 1)
      self.oels[p.r] = cl(self)
  def point(self, p):
    self.w.create_oval(p.x, p.y, p.x, p.y, width = 0, fill = 'black')
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
      if p.r != self.in_motion.r:
        e.render(p.x*self.s, p.y*self.s, self.s)
      else:
        e.render(p.x*self.s+self.shift.x, p.y*self.s+self.shift.y, self.s)
    self.tk.update()
  def onclick1(self, ev):
    self.click_moved = False
    self.in_motion = pos(ev.x//self.s, ev.y//self.s)
    print(self.in_motion)
    self.first_click = pos(ev.x, ev.y)
  def onrel1(self, ev):
    if self.click_moved:
      if self.in_motion.r in self.els.keys() and (ev.x//self.s, ev.y//self.s) != self.in_motion.r:
        self.els[pround(ev.x, ev.y, self.s)] = self.els[self.in_motion.r]
        self.els.pop(self.in_motion.r)
    self.in_motion = pos(-1, -1)
    self.shift = pos(0,0)
  def motion1(self, ev):
    self.click_moved = True
    self.shift = pos(ev.x-self.first_click.x, ev.y-self.first_click.y)
  def onkey(self, ev):
    print(ev)
    if ev.keycode > 111 and ev.keycode < 111+13:
      gates = [None, element, wire, resistor, apin, bpin]
      if len(gates) <= ev.keycode-111:
        print('NO F',ev.keycode-111,' ELEMENT', sep='')
      else:
        b = gates[ev.keycode-111]
        self.new(b, ev.x, ev.y)
    if ev.keycode == 220:
      code.InteractiveConsole(vars()).interact()
    if ev.keycode == 222:
      global resistor_i
      resistor_i = 1
      for e in self.tels.values():
        if str(e) is 'resistor':
          e.i = resistor_i
          resistor_i += 1
    if ev.state == 0x40001:  # shift + del
      self.tels = {}
      self.oels = {}
    if ev.keycode == 187:
      self.s += 1
    if ev.keycode == 189:
      self.s -= 1
    if pround(ev.x, ev.y, self.s, 2).r in self.tels.keys():
      if ev.keycode == 46:
        del self.tels[pround(ev.x, ev.y, self.s, 2).r]
      else:
        self.tels[pround(ev.x, ev.y, self.s, 2).r].onkey(ev)
    if pround(ev.x, ev.y, self.s, 1).r in self.oels.keys():
      if ev.keycode == 46:
        del self.oels[pround(ev.x, ev.y, self.s, 1).r]
      else:
        self.oels[pround(ev.x, ev.y, self.s, 1).r].onkey(ev)

board = Board()
if True:#try:
  while 1:
    t = time()
    while t+0.2 > time():
      board.render()
#except TclError:
  # window exit
  pass
# code.InteractiveConsole(vars()).interact()
