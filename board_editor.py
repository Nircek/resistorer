#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# file from https://github.com/Nircek/resistorer
# licensed under MIT license

'''
MIT License

Copyright (c) 2018-2019 Nircek

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


import math
import code
from tkinter import simpledialog, messagebox, filedialog
import tkinter as tk
import sys
import pickle

from elements import APin, BPin, Wire, Resistor, TElement, OElement
from coords import Pos, pround
from board import Board, NothingHappenedError, NoPinsError
from primitives import Primitive

UNITS = {'R': '\N{OHM SIGN}', 'U': 'V', 'I': 'A'}


def get_unit(what):
    '''get_unit translates the name of variable to corresponding unit of it'''
    if what in UNITS:
        return UNITS[what]
    return ''


class CanceledError(Exception):
    pass


class BoardEditor:
    def __init__(self, WIDTH=1280, HEIGHT=720, s=40):
        self.size = Pos(WIDTH, HEIGHT)
        self.elsize = s  # size of one element
        self.board = Board()
        self.tkroot = tk.Tk()
        self.canvas = tk.Canvas(self.tkroot, width=WIDTH, height=HEIGHT,
                                bg='#ccc', bd=0, highlightthickness=0)
        self.make_tk()
        self.canvas.pack(expand=True)
        self.canvas.focus_set()
        self.in_motion = Pos(-1, -1)
        self.shift = Pos(0, 0)
        self.newpos = Pos(0, 0)
        self.newself = False
        self.x_coord = 0
        self.y_coord = 0
        self.lastfile = None
        self.queue = []
        self.powerv = True  # power voltage
        self.power = 12
        self.crc = Primitive(math.inf)  # CiRCuit :D easy to remember
        # but is it necessary?
        self.stop = tk.BooleanVar()

    def set_power(self, is_voltage, value):
        if value is None:
            return
        self.powerv = is_voltage
        self.power = value

    def with_click(self, value):
        self.queue += [value]

    def configure(self, event):
        self.size.x_coord = event.width
        self.size.y_coord = event.height
        self.canvas.config(width=event.width, height=event.height)

    def make_tk(self):
        self.tkroot.title('Resistorer')
        self.canvas.bind('<Button 1>', self.onclick1)
        self.canvas.bind('<ButtonRelease-1>', self.onrel1)
        self.canvas.bind('<B1-Motion>', self.motion1)
        self.canvas.bind('<KeyPress>', self.onkey)
        self.tkroot.bind('<Configure>', self.configure)
        self.tkroot.protocol('WM_DELETE_WINDOW', lambda: self.stop.set(True))
        # -----
        menu_bar = tk.Menu(self.tkroot)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='New', command=self.board.new_sketch,
                              accelerator='Shift+Del')
        file_menu.add_command(label='Open', command=self.open,
                              accelerator='Ctrl+O')
        file_menu.add_command(label='Save', command=self.save,
                              accelerator='Ctrl+S')
        file_menu.add_command(label='Save as...',
                              command=lambda: self.save(-1),
                              accelerator='Ctrl+Shift+S')
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=lambda: self.stop.set(
            True), accelerator='Alt+F4')
        menu_bar.add_cascade(label='File', menu=file_menu)
        # -----
        edit_menu = tk.Menu(menu_bar, tearoff=0)

        def add_el(_type):
            return lambda: self.with_click(
                lambda p: self.new(_type, p[0], p[1]))  # add element
        edit_menu.add_command(label='Add a wire', command=add_el(Wire),
                              accelerator='F1')
        edit_menu.add_command(label='Add a resistor',
                              command=add_el(Resistor), accelerator='F2')
        edit_menu.add_command(label='Add a + power supply',
                              command=add_el(APin), accelerator='F3')
        edit_menu.add_command(label='Add a - power supply',
                              command=add_el(BPin), accelerator='F4')
        edit_menu.add_separator()
        edit_menu.add_command(
            label='Delete element',
            command=lambda: self.with_click(
                lambda p: self.board.delete(p[0], p[1])),
            accelerator='Del')
        edit_menu.add_command(label='Delete all',
                              command=self.board.new_sketch,
                              accelerator='Shift+Del')
        menu_bar.add_cascade(label='Edit', menu=edit_menu)
        # -----
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label='Zoom in',
                              command=lambda: self.zoom(+1), accelerator='+')
        view_menu.add_command(label='Zoom out',
                              command=lambda: self.zoom(-1), accelerator='-')
        view_menu.add_command(label='Count resistors',
                              command=self.board.count, accelerator='\'')
        menu_bar.add_cascade(label='View', menu=view_menu)
        # -----
        power_menu = tk.Menu(menu_bar, tearoff=0)
        power_menu.add_command(label='Voltage', command=lambda: self.set_power(
            True, self.input_float('Voltage [' + get_unit('U') + ']')))
        power_menu.add_command(label='Current', command=lambda: self.set_power(
            False, self.input_float('Current [' + get_unit('I') + ']')))
        menu_bar.add_cascade(label='Power supply', menu=power_menu)
        # -----
        debug_menu = tk.Menu(menu_bar, tearoff=0)
        debug_menu.add_command(label='Open a console',
                               command=self.interactive, accelerator='\\')
        self.auto = tk.BooleanVar()
        self.auto.set(True)
        debug_menu.add_checkbutton(label='Auto calculating', onvalue=True,
                                   offvalue=False, variable=self.auto)
        debug_menu.add_command(label='Calculate', command=self.calc,
                               accelerator='Enter')
        menu_bar.add_cascade(label='Debug', menu=debug_menu)
        # -----
        self.tkroot.config(menu=menu_bar)

    def calc(self):
        try:
            self.crc = self.board.calc()
        except NothingHappenedError:
            pass
        except NoPinsError:
            if not self.auto.get():
                messagebox.showerror('Error', 'NO PINS SPECIFIED')
            self.crc = Primitive(math.inf)

    def dump(self):
        buffer = self.tkroot, self.canvas
        del self.tkroot, self.canvas
        dumped = pickle.dumps(self)
        self.tkroot, self.canvas = buffer
        return dumped

    def load(self, data):
        buffer = self.tkroot, self.canvas
        loaded = pickle.loads(data)
        loaded.tk, loaded.w = buffer
        loaded.make_tk()
        self.newself = loaded

    def point(self, pos):
        self.canvas.create_oval(pos.x_coord, pos.y_coord,
                                pos.x_coord, pos.y_coord,
                                width=1, fill='black')

    def render(self):
        if self.stop.get():
            sys.exit()
        self.canvas.delete('all')
        for x_coord in range(self.x_coord // self.elsize,
                             (self.size.x_coord + self.x_coord)
                             // self.elsize + 1):
            for y_coord in range(self.y_coord // self.elsize,
                                 (self.size.y_coord + self.y_coord)
                                 // self.elsize + 1):
                self.point(Pos(x_coord * self.elsize - self.x_coord,
                               y_coord * self.elsize - self.y_coord))
        txt = ''
        for teli, tel in self.board.tels.items():
            if str(tel) == 'Resistor':
                txt += repr(tel)
                first = True
                for infoi, info in tel.info.items():
                    if first:
                        first = False
                    else:
                        txt += len(repr(tel)) * ' '
                    txt += ' ' + infoi + '=' + str(info) + ' ' + \
                           get_unit(infoi) + '\n'
                if txt[-1] != '\n':
                    txt += '\n'
            teli = Pos(teli)
            if teli.t_tuple != self.in_motion.t_tuple:
                tel.render(teli.x_coord * self.elsize - self.x_coord,
                           teli.y_coord * self.elsize - self.y_coord,
                           self.elsize, teli.orient)
            else:
                tel.render(self.newpos.x_coord - self.shift.x_coord,
                           self.newpos.y_coord - self.shift.y_coord,
                           self.elsize, teli.orient)
        txt += 'R\N{LATIN SMALL LETTER Z WITH STROKE}=' + \
            ('\N{INFINITY}' if self.crc.ph_r == math.inf
             else str(self.crc.ph_r))
        u_txt = str(self.power if self.powerv else (
            0 if math.isnan(self.crc.ph_r * self.power) else (
                self.crc.ph_r * self.power
                if self.crc.ph_r * self.power != math.inf
                else '\N{INFINITY}')))
        i_txt = str(self.power if (not self.powerv) else (
            '\N{INFINITY}' if (self.crc.ph_r == 0) else (
                self.power / self.crc.ph_r)))
        txt += ' U=' + u_txt + ' I=' + i_txt
        self.canvas.create_text(0, self.size.y_coord, font='TkFixedFont',
                                anchor='sw', text=txt)
        for oeli, oel in self.board.oels.items():
            oeli = Pos(oeli)
            oel.render(oeli.x_coord * self.elsize - self.x_coord,
                       oeli.y_coord * self.elsize - self.y_coord, self.elsize)
        self.tkroot.update_idletasks()
        self.tkroot.update()
        if self.auto.get():
            self.board.calc()
        if self.newself:
            return self.newself
        return self

    def onclick1(self, event):
        if self.queue:
            self.queue[0]((event.x, event.y))
            self.queue = self.queue[1:]
        self.in_motion = pround(event.x + self.x_coord,
                                event.y + self.y_coord,
                                self.elsize, True)
        self.shift = Pos(event.x + self.x_coord - self.in_motion.x_coord *
                         self.elsize, event.y + self.y_coord -
                         self.in_motion.y_coord * self.elsize)
        self.newpos = Pos(event.x, event.y)

    def onrel1(self, event):
        if self.in_motion.t_tuple in self.board.tels.keys() \
            and pround(event.x + self.x_coord, event.y + self.y_coord,
                       self.elsize, True).t_tuple != self.in_motion.t_tuple:
            self.board.tels[
                pround(event.x + self.x_coord,
                       event.y + self.y_coord,
                       self.elsize, True).t_tuple
                ] = self.board.tels[self.in_motion.t_tuple]
            self.board.tels.pop(self.in_motion.t_tuple)
        self.in_motion = Pos(-1, -1)
        self.shift = Pos(-1, -1)

    def motion1(self, event):
        self.newpos = Pos(event.x, event.y)

    def interactive(self):
        code.InteractiveConsole({'self': self}).interact()

    def onkey(self, event):
        event.x += self.x_coord
        event.y += self.y_coord
        if len(event.keysym) > 1 and event.keysym[:1] == 'F':
            i = int(event.keysym[1:]) - 1
            gates = [Wire, Resistor, APin, BPin]
            if len(gates) <= i:
                messagebox.showerror(
                    'Error', 'NO F' + str(i + 1) + ' ELEMENT')
            else:
                self.new(gates[i], event.x, event.y)
        if event.keysym == 'Enter' or event.keysym == 'Return':
            self.board.calc()
        if event.keysym == 'backslash':
            self.interactive()
        if event.keysym == 'apostrophe' or event.keysym == 'quoteright':
            self.board.count()
        if (event.state & 1) != 0 and event.keysym == 'Delete':  # shift + del
            self.board.new_sketch()
        if event.keysym == 'plus':
            self.zoom(+1)
        if event.keysym == 'minus':
            self.zoom(-1)
        if event.keysym == 'Left':
            self.x_coord -= 1
        if event.keysym == 'Right':
            self.x_coord += 1
        if event.keysym == 'Up':
            self.y_coord -= 1
        if event.keysym == 'Down':
            self.y_coord += 1
        if event.keysym == 'Delete':
            self.board.delete(event.x, event.y)
        if pround(event.x, event.y, self.elsize, True).t_tuple in \
                self.board.tels.keys():
            self.board.tels[
                pround(event.x, event.y, self.elsize, True).t_tuple
                ].onkey(event)
        if pround(event.x, event.y, self.elsize).o_tuple in \
                self.board.oels.keys():
            self.board.oels[pround(event.x, event.y, self.elsize).o_tuple] \
                .onkey(event)
        if event.keysym.upper() == 'S' and event.state == 0b100:  # Ctrl+S
            self.save()
        if event.keysym.upper() == 'S' and event.state == 0b101:  # Ctrl+Sh+S
            self.save(-1)
        if event.keysym.upper() == 'O' and event.state == 0b100:  # Ctrl+O
            self.open()

    def input_float(self, msg):
        buffer = simpledialog.askfloat('Input', msg,
                                       parent=self.tkroot, minvalue=0.0)
        self.canvas.focus_set()
        return buffer

    def input_resistance(self, uid):
        new_value = self.input_float(
            'Value of R' + str(uid) + ' [' + get_unit('R') + ']')
        if new_value is None:
            raise CanceledError
        return new_value

    def open(self, file=None):
        if file is None:
            file = filedialog.askopenfilename(filetypes=(
                ('sketch files', '*.sk'), ('all files', '*.*')))
        if not file:
            return False
        file_handle = open(file, mode='rb')
        self.load(file_handle.read())
        file_handle.close()
        self.newself.lastfile = file
        return True

    def save(self, file=None):  # file=-1 for force asking
        if (file is None) and (self.lastfile is not None):
            file = self.lastfile
        elif (file is None) or (file == -1):
            file = filedialog.asksaveasfilename(filetypes=(
                ('sketch files', '*.sk'), ('all files', '*.*')))
        if not file:
            return False
        file_handle = open(file, mode='wb')
        file_handle.write(self.dump())
        self.lastfile = file
        file_handle.close()
        return True

    def zoom(self, inc):
        self.x_coord += self.x_coord // self.elsize
        self.y_coord += self.y_coord // self.elsize
        self.elsize += inc

    def new(self, _type, x_coord, y_coord):
        try:
            if issubclass(_type, TElement):
                self.board.new_tel(_type(self), pround(x_coord, y_coord,
                                                       self.elsize,
                                                       True).t_tuple)
            if issubclass(_type, OElement):
                self.board.new_oel(_type(self), pround(x_coord, y_coord,
                                                       self.elsize).o_tuple)
        except CanceledError:
            pass
