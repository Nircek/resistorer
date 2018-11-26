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
    self.r = (self.x, self.y)


def pround(p, sh=(0,0)):
  x = lambda y,s : round(y/s)*s
  return pos(x(p.x+sh.x, s), x(p.y+sh.y, s))
'''
class element:
  slots = 0
  sh = pos(0,0)
  def __str__(self):
    return 'element'
  def __init__(self, parent, p):
    # UUIDS, xy
    self.addr = super().__repr__().split('0x')[1][:-1]
    self.UUID = -1
    self.parent = parent
    self.e = pos(-1, -1)
    self.p = pround(p, self.sh)
  def getsize(self):
    return self.s
  def onclick1(self):
    pass
  def onclick2(self):
    pass
  def motion(self, p):
    self.p.x = p.x - self.s.w // 2
    self.p.y = p.y - self.s.h // 2
    self.p = pround(self.p)
  def onkey(self, ev):
    if  ev.x >= self.p.x and ev.x <= self.p.x+self.s.w \
    and ev.y >= self.p.y and ev.y <= self.p.y+self.s.h:
      print(self.UUID)
      if ev.keycode == 46:
        self.parent.rm(self.UUID)
  def __repr__(self):
    return str(vars(self))
  def render(self):
    self.parent.arc(self.p.x+self.s.w//2, self.p.y+self.s.h//2, min(self.s.w, self.s.h)//2, 0, 360)

class verwire(element):
  sh=pos(s//2,0)
  s = pos(40, 40)
  def __str__(self):
    return 'verwire'
  def render(self):
    self.parent.w.create_line(self.p.x, self.p.y, self.p.x, self.p.y+40, fill='black')

class horwire(element):
  sh=pos(0,s//2)
  s = pos(40, 40)
  def __str__(self):
    return 'horwire'
  def render(self):
    self.parent.w.create_line(self.p.x, self.p.y, self.p.x+40, self.p.y, fill='black')
'''
class Board:
  def __init__(self, WIDTH=1280, HEIGHT=720, s=40):
    self.WIDTH = WIDTH
    self.HEIGHT = HEIGHT
    self.s = s  # size of one element
    self.els = {}  # elements
    self.tk = Tk()
    self.w = Canvas(self.tk, width=WIDTH, height=HEIGHT)
    self.w.bind('<Button 1>', self.onclick1)
    self.w.bind('<ButtonRelease-1>', self.onrel1)
    self.w.bind('<B1-Motion>', self.motion1)
    self.w.bind('<KeyPress>',self.onkey)
    self.w.pack()
    self.w.focus_set()
    self.in_motion = None
    self.click_moved = False
    self.first_click = None
    self.shift = pos(0, 0)
  def point(self, p):
    self.w.create_oval(p.x, p.y, p.x, p.y, width = 0, fill = 'black')
  def render(self):
    self.w.delete('all')
    for x in range(self.WIDTH//self.s):
      for y in range(self.HEIGHT//self.s):
        self.point(pos(x*self.s, y*self.s))
    for e, p in self.els.items():
      p = pos(p)
      e.render(p.x*self.s, p.y*self.s, self.s)
    self.tk.update()
  def onclick1(self, ev):
    click_moved = False
    in_motion = pos(ev.x//self.s, ev.y//self.s)
    self.first_click = pos(ev.x, ev.y)
  def onrel1(self, ev):
    if not self.click_moved:
      if in_motion in self.els and (ev.x//self.s, ev.y//self.s) != in_motion:
        self.els[(ev.x//self.s, ev.y//self.s)] = self.els[in_motion]
        del self.els[in_motion]
  def motion1(self, ev):
    click_moved = True
    self.shift = pos(self.first_click.x-ev.x, self.first_click.y-ev.y)
  def onkey(self, ev):
    print(ev)
    if ev.keycode > 111 and ev.keycode < 111+13:
      gates = [None]#, element, verwire, horwire]
      if len(gates) <= ev.keycode-111:
        print('NO F',ev.keycode-111,' ELEMENT', sep='')
      else:
        b = gates[ev.keycode-111]
        self.new(b, pos(ev.x//self.s, ev.y//self.s))
    if ev.keycode == 220:
      code.InteractiveConsole(vars()).interact()
    if ev.state == 0x40001:
      pass

board = Board()
try:
  while 1:
    t = time()
    while t+0.2 > time():
      board.render()
except TclError:
  # window exit
  pass
# code.InteractiveConsole(vars()).interact()
