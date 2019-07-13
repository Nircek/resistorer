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
from primitives import Primitive, get_unit


class CancelledError(Exception):
    '''User cancelled the creating operation'''


class BoardEditor:
    '''The editor of board, it has a tk window and a Board.'''
    def __init__(self, WIDTH=1280, HEIGHT=720, s=40):
        self.size = Pos(WIDTH, HEIGHT)
        self.elsize = s  # size of one element
        self.board = Board()
        self.tkroot = tk.Tk()
        self.canvas = tk.Canvas(self.tkroot, width=WIDTH, height=HEIGHT,
                                bg='#ccc', bd=0, highlightthickness=0)
        self.auto = tk.BooleanVar()
        self.auto.set(True)
        self.stop = tk.BooleanVar()
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

    def set_power(self, is_voltage, value):
        '''Sets value of voltage or current for calculations between APin
        and BPin.

        param is_voltage (bool) - if True: sets voltage value
                                  if False: sets current value
        param value (int or float) - value in ampers or volts'''
        if value is None:
            return
        self.powerv = is_voltage
        self.power = value

    def configure(self, event):
        '''Handler of <Configure> event resizing the window'''
        self.size.x_coord = event.width
        self.size.y_coord = event.height
        self.canvas.config(width=event.width, height=event.height)

    def make_tk(self):
        '''Sets all the tk stuff'''
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
            return lambda: self.queue.append(
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
            command=lambda: self.queue.push(
                lambda p: self.delete(p[0], p[1])),
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
        debug_menu.add_checkbutton(label='Auto calculating', onvalue=True,
                                   offvalue=False, variable=self.auto)
        debug_menu.add_command(label='Calculate', command=self.calc,
                               accelerator='Enter')
        menu_bar.add_cascade(label='Debug', menu=debug_menu)
        # -----
        self.tkroot.config(menu=menu_bar)

    def calc(self):
        '''Translates the circuit into primitives and set it to self.crc'''
        try:
            self.crc = self.board.calc()
            self.board.nodes.calc_voltages(
                self.crc, 'V' if self.powerv else 'A', self.power)
        except NothingHappenedError:
            pass
        except NoPinsError:
            if not self.auto.get():
                messagebox.showerror('Error', 'NO PINS SPECIFIED')
            self.crc = Primitive(math.inf)

    def dump(self):
        '''Returns bytes intepretation of the sketch'''
        buffer = self.tkroot, self.canvas, self.auto, self.stop
        del self.tkroot, self.canvas
        self.auto, self.stop = self.auto.get(), self.stop.get()
        dumped = pickle.dumps(self)
        self.tkroot, self.canvas, self.auto, self.stop = buffer
        return dumped

    def load(self, data):
        '''Loads bytes interpretation of the sketch'''
        loaded = pickle.loads(data)
        loaded.tkroot, loaded.canvas = self.tkroot, self.canvas
        self.stop.set(loaded.stop)
        self.auto.set(loaded.auto)
        loaded.auto, loaded.stop = self.auto, self.stop
        loaded.make_tk()
        self.newself = loaded

    def point(self, pos):
        '''Makes a point at pos (Pos) on the canvas'''
        self.canvas.create_oval(pos.x_coord, pos.y_coord,
                                pos.x_coord, pos.y_coord,
                                width=1, fill='black')

    def render(self):
        '''Clears the canvas, draws the coord points, renders all elements,
        writes info about resistors and circuit and handles tk events.
        Returns self but this can be freshly loaded new self which should be
        treated as self and be updated so the best usage of this function is:

            while 1:
                board_editor = board_editor.render()
        '''
        if self.stop.get():
            sys.exit()
        self.canvas.delete('all')  # clear canvas
        for x_coord in range(self.x_coord // self.elsize,
                             (self.size.x_coord + self.x_coord)
                             // self.elsize + 1):
            for y_coord in range(self.y_coord // self.elsize,
                                 (self.size.y_coord + self.y_coord)
                                 // self.elsize + 1):
                self.point(Pos(x_coord * self.elsize - self.x_coord,
                               y_coord * self.elsize - self.y_coord))
        # add the coord points
        txt = ''
        for teli, tel in self.board.tels.items():
            if str(tel) == 'Resistor':
                txt += repr(tel)  # add the info about every resistor
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
            teli = Pos(teli)  # and render it
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
             else str(self.crc.ph_r))  # add the whole circuit info
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
        for oeli, oel in self.board.oels.items():  # render every oel
            oeli = Pos(oeli)
            oel.render(oeli.x_coord * self.elsize - self.x_coord,
                       oeli.y_coord * self.elsize - self.y_coord, self.elsize)
        self.tkroot.update_idletasks()
        self.tkroot.update()  # tk stuff
        if self.auto.get():
            self.calc()
        if self.newself:  # if new self is loaded, change self to newself
            return self.newself
        return self

    def onclick1(self, event):
        '''Handles onclick events with primary mouse button.
        Adds elements if some are in queue and moves elements on the board'''
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
        '''Handles onrelease event with primary mouse button.
        Finishes moving elements on the board'''
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
        '''Handles onmotion event with primary mouse button.
        Drawing the animation of moving elements on the board'''
        self.newpos = Pos(event.x, event.y)

    def interactive(self):
        '''Starts interactive console with self'''
        code.InteractiveConsole({'self': self}).interact()

    def onkey(self, event):
        '''Handles onkey events'''
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
            self.calc()
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
            self.delete(event.x, event.y)
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
        '''Makes the tk dialog asking about a float value'''
        buffer = simpledialog.askfloat('Input', msg,
                                       parent=self.tkroot, minvalue=0.0)
        self.canvas.focus_set()
        return buffer

    def input_resistance(self, uid):
        '''Makes the tk dialog asking about a float value of resistor's
        resistance'''
        new_value = self.input_float(
            'Value of R' + str(uid) + ' [' + get_unit('R') + ']')
        if new_value is None:
            raise CancelledError
        return new_value

    def open(self, file=None):
        '''Opens a file with sketch interpratation and loads it
        param file (str) - file's path
                           if None: it makes a dialog asking about the path'''
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

    def save(self, file=None):
        '''Saves a file with sketch interpretation
        param file (str or -1) - file's path
                                 if None: makes a dialog asking about the path
                                          or takes the last used if present
                                 if -1: forces making dialog (Save as...)'''
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
        '''Zooms in or zooms out the sketch by inc
        param inc (int or float) - the value of how much changes the size
                                   of one element on the board'''
        self.x_coord += self.x_coord // self.elsize
        self.y_coord += self.y_coord // self.elsize
        self.elsize += inc

    def new(self, _type, x_coord, y_coord):
        '''Adds to board a new _type element on the x_coord and y_coord
        param _type (TElement or OElement) - type of new element
        param x_coord, y_coord - coords of position where new element should be
                                 placed, relative to (0, 0) pixel of windw'''
        try:
            if issubclass(_type, TElement):
                self.board.new_tel(_type(self), pround(x_coord, y_coord,
                                                       self.elsize,
                                                       True).t_tuple)
            if issubclass(_type, OElement):
                self.board.new_oel(_type(self), pround(x_coord, y_coord,
                                                       self.elsize).o_tuple)
        except CancelledError:
            pass

    def delete(self, x_coord, y_coord):
        '''Deletes elements on x_coord and y_coord
        param x_coord, y_coord - coords of elements which element should be
                                 deleted, relative to (0, 0) pixel of window'''
        self.board.del_tel(pround(x_coord, y_coord, self.elsize, True).t_tuple)
        self.board.del_oel(pround(x_coord, y_coord, self.elsize).o_tuple)
