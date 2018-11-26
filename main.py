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
  def __repr__(self):
    return repr(self.r)


def pround(p, sh=(0,0)):
  x = lambda y,s : round(y/s)*s
  return pos(x(p.x+sh.x, s), x(p.y+sh.y, s))

class element:
  def __str__(self):
    return 'element'
  def __init__(self, parent):
    self.addr = super().__repr__().split('0x')[1][:-1]
    self.parent = parent
  def __repr__(self):
    return str(vars(self))
  def render(self, x, y, s):
    self.parent.w.create_rectangle(x, y, x+s, y+s)
'''
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
    self.in_motion = pos(-1,-1)
    self.click_moved = False
    self.first_click = None
    self.shift = pos(0, 0)
  def new(self, cl, p):
    print(p)
    self.els[p.r] = cl(self)
  def point(self, p):
    self.w.create_oval(p.x, p.y, p.x, p.y, width = 0, fill = 'black')
  def render(self):
    self.w.delete('all')
    for x in range(self.WIDTH//self.s):
      for y in range(self.HEIGHT//self.s):
        self.point(pos(x*self.s, y*self.s))
    for p, e in self.els.items():
      p = pos(p)
      print(p.r, self.in_motion.r)
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
        self.els[(ev.x//self.s, ev.y//self.s)] = self.els[self.in_motion.r]
        self.els.pop(self.in_motion.r)
    self.in_motion = pos(-1, -1)
    self.shift = pos(0,0)
  def motion1(self, ev):
    self.click_moved = True
    self.shift = pos(ev.x-self.first_click.x, ev.y-self.first_click.y)
  def onkey(self, ev):
    print(ev)
    if ev.keycode > 111 and ev.keycode < 111+13:
      gates = [None, element]#, verwire, horwire]
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
