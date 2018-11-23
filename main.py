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
    self.e = pos(-1, -1)
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
    self.e = pos(self.xy())
  def onclick1(self):
    if self.st == 'black':
      self.st = 'orange'
    else:
      self.st = 'black'
  def onclick2(self):
      self.st = 'green'
  def motion(self, p):
      self.p.x = p.x - self.s.w // 2
      self.p.y = p.y - self.s.h // 2
      self.e = pos(self.xy())
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
    self.rmc = pos(-1,-1)
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
  def update(self, inf=False, x=None):
    if x is None:
      tt = False
      for i in range(len(self.UUIDS)):
        tt = False
        for e in self.UUIDS:
          t = self.get(e.UUID).power
          self.update(x=e.UUID)
          if self.get(e.UUID).power != t:
            tt = True
        if not (tt and inf):
          break
      if tt and inf:
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
    if self.selected is not None and self.rmc.x != -1:
      t = self.get(self.selected)
      self.w.create_line(t.e.x, t.e.y, self.rmc.x, self.rmc.y)
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
      self.get(self.in_motion).motion(ev)
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
    self.rmc = pos(-1,-1)
  def motion2(self, ev):
    self.click_moved = True
    self.rmc.x = ev.x
    self.rmc.y = ev.y
  def onkey(self, ev):
    print(ev)
    if ev.keycode > 111 and ev.keycode < 111+13:
      gates = [None]
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
try:
  while 1:
    UUIDS.update()
    t = time()
    while t+0.2 > time():
      UUIDS.render()
except TclError:
  # window exit
  pass
# code.InteractiveConsole(vars()).interact()
