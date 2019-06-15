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

import code
from tkinter import simpledialog, messagebox, filedialog
import tkinter as tk
import math
import pickle
import sys

UNITS = {'R': '\N{OHM SIGN}', 'U': 'V', 'I': 'A'}


def get_unit(what):
    '''get_unit translates the name of variable to corresponding unit of it'''
    if what in UNITS:
        return UNITS[what]
    return ''


class Primitive:
    def __init__(self, r=None):
        if r is not None:
            self.ph_r = r
        self._ph_i, self._ph_u = None, None
        self.node_a, self.node_b = None, None

    def __repr__(self):
        return '[' + str(self.ph_r) + ']'

    def __str__(self):
        return self.__class__.__name__

    @property
    def components(self):
        return []

    @property
    def ph_i(self):
        return self._ph_i

    @property
    def ph_u(self):
        return self._ph_u

    def update_r(self):
        pass

    def clear_iu(self):
        self._ph_i = None
        self._ph_u = None

    @ph_i.setter
    def ph_i(self, new):
        if new is None:
            self.clear_iu()
            return
        self._ph_i = new
        self._ph_u = self.ph_r * new
        self.update_r()

    @ph_u.setter
    def ph_u(self, new):
        if new is None:
            self.clear_iu()
            return
        self._ph_u = new
        self._ph_i = new / self.ph_r
        self.update_r()


class Series(Primitive):
    def __init__(self, *args):
        super().__init__()
        self.data = args
        self.ph_u = None

    def __repr__(self):
        return '+(' + ', '.join(map(repr, self.data)) + ')'

    @property
    def components(self):
        return self.data

    @property
    def ph_r(self):
        return sum(map(lambda x: x.ph_r, self.data))

    def update_r(self):
        for ele in self.data:
            ele.ph_i = self.ph_i


class Parallel(Primitive):
    def __init__(self, *args):
        super().__init__()
        self.data = args
        self.ph_u = None

    def __repr__(self):
        return ':(' + ', '.join(map(repr, self.data)) + ')'

    @property
    def components(self):
        return self.data

    @property
    def ph_r(self):
        return 1 / sum(map(lambda x: 1 / x.ph_r, self.data))

    def update_r(self):
        for ele in self.data:
            ele.ph_u = self.ph_u


class Delta(Primitive):
    def __init__(self, x, y, z, i):
        super().__init__()
        self.components = [x, y, z]
        self.wiring_type = i
        self.ph_u = None

    def __repr__(self):
        return '\N{GREEK CAPITAL LETTER DELTA}(' + \
               ', '.join(map(repr, self.components + self.wiring_type)) + ')'

    @property
    def ph_r(self):
        return {
            1: self.components[0].ph_r * self.components[1].ph_r,
            2: self.components[0].ph_r * self.components[2].ph_r,
            3: self.components[1].ph_r * self.components[2].ph_r
        }[self.wiring_type] / sum(map(lambda x: x.ph_r, self.components))


class Nodes:
    def __init__(self):
        self.nodes = {}
        self.node_voltages = []

    def reset_nodes(self):
        self.nodes = []

    def search_node(self, x_coord, y_coord):
        for i, ele in enumerate(self.nodes):
            if (x_coord, y_coord) in ele:
                return i
        return -1

    def add_node(self, x_coord, y_coord, x2_coord=-1, y2_coord=-1):
        print(self.nodes)
        node_index = self.search_node(x_coord, y_coord)
        node2_index = self.search_node(x2_coord, y2_coord)
        print(node_index, node2_index)
        new_index = -1
        if node_index == -1 and node2_index == -1:
            new_index = len(self.nodes)
            self.nodes += [[]]
        elif (node_index == -1) != (node2_index == -1):
            new_index = node_index + node2_index + 1  # a or b
        elif node_index != node2_index:
            self.nodes[node_index] += self.nodes[node2_index]
            del self.nodes[node2_index]
            return
        print(new_index)
        if (x_coord, y_coord) not in self.nodes[new_index] and \
                -1 not in (x_coord, y_coord):
            self.nodes[new_index] += [(x_coord, y_coord)]
        if (x2_coord, y2_coord) not in self.nodes[new_index] and \
                -1 not in (x2_coord, y2_coord):
            self.nodes[new_index] += [(x2_coord, y2_coord)]

    def interpret(self, data, start, end):
        # -----
        def datasearch(node_a, node_b=-1):
            '''look for all resistors connecting node_a and node_b'''
            results = []
            for i, connection in enumerate(data):
                if connection.node_a == node_a:
                    if node_b in (connection.node_b, -1):
                        results += [i]
                elif connection.node_b == node_a:
                    if node_b in (connection.node_a, -1):
                        results += [i]
            return results

        def other_side(index, known):
            '''index of element connects known node and returned node'''
            return data[index].node_a + data[index].node_b - known

        def without(arr):
            return list(map(lambda x: x[1],
                            filter(lambda x: x[0] not in arr,
                                   enumerate(arr))))

        def process_delta():
            for first_node in range(len(self.nodes)):
                for first in datasearch(first_node):
                    second_node = other_side(first, first_node)
                    for second in datasearch(second_node):
                        third_node = other_side(second, second_node)
                        for third in datasearch(third_node):
                            fourth_node = other_side(third, third_node)
                            if fourth_node == first_node:
                                ndata = without((first, second, third))
                                delta_a = Delta(data[first], data[second],
                                                data[third], 1)
                                delta_b = Delta(data[first], data[second],
                                                data[third], 2)
                                delta_c = Delta(data[first], data[second],
                                                data[third], 3)
                                delta_a.node_a, delta_b.node_a, \
                                    delta_c.node_a = first_node, third_node, \
                                    second_node
                                delta_a.node_b, delta_b.node_b, \
                                    delta_c.node_b = [len(self.nodes)] * 3
                                ndata += [delta_a, delta_b, delta_c]
                                return ndata
            return None

        def process_series():
            for node in range(len(self.nodes)):
                if node not in (start, end):
                    connections = datasearch(node)
                    if len(connections) == 2:
                        ndata = without(connections)
                        series = Series(data[connections[0]],
                                        data[connections[1]])
                        series.node_a, series.node_b = \
                            other_side(connections[0], node), \
                            other_side(connections[1], node)
                        ndata += [series]
                        return ndata
            return None

        def process_parallel():
            for index, connection in enumerate(data):
                for index2, connection2 in enumerate(data):
                    nodes_of_conn = connection.node_a, connection.node_b
                    nodes_of_conn2 = connection2.node_a, connection2.node_b
                    if index != index2 and nodes_of_conn in \
                            (nodes_of_conn2, nodes_of_conn2[::-1]):
                        ndata = without((index, index2))
                        parallel = Parallel(connection, connection2)
                        parallel.node_a, parallel.node_b = \
                            connection.node_a, connection.node_b
                        ndata += [parallel]
                        return ndata
            return None

        def process_unnecessary():
            removed = []
            for node in range(len(self.nodes)):
                if node not in (start, end):
                    connections = datasearch(node)
                    if len(connections) == 1:
                        removed += connections
            for connection_i, connection in enumerate(data):
                if connection.node_a == connection.node_b:
                    removed += [connection_i]
            return without(removed) if removed else None
        # -----
        processors = [process_unnecessary, process_series,
                      process_parallel, process_delta]
        old_data = []
        while old_data != data:
            old_data = data[:]
            # print(odata)
            for processor in processors:
                ndata = processor()
                if ndata is not None:
                    data = ndata
                    if processor == process_delta:  # pylint: disable=W0143
                        self.nodes += [[]]
                    break
        if not data:
            if start == end:
                return Primitive(0)
            return Primitive(math.inf)
        if len(data) == 1:
            return data[0]
        raise RuntimeError('Can\'t find a processor to simplify the circuit')

    def calc_voltages(self, circuit, unit, amount):  # calced
        if str(circuit) == 'Primitive':
            return

        def cv(whole, part):  # calc voltage(parent, data)
            if str(part) == 'Primitive':
                return None
            buffer = False
            for component in part.components:
                buffer = cv(whole, component)
            if (part.ph_u is not None) and \
                    ((whole.node_voltages[part.node_a] is None)
                     != (whole.node_voltages[part.node_b] is None)) and \
                    part.node_a != circuit.node_b and \
                    part.node_b != circuit.node_b:  # '!=' = 'xor'
                if whole.node_voltages[part.node_a] is None:
                    whole.node_voltages[part.node_a] = \
                        whole.node_voltages[part.node_b] + part.ph_u
                else:
                    whole.node_voltages[part.node_b] = \
                        whole.node_voltages[part.node_a] + part.ph_u
                return True
            if part.ph_u is None and \
                None not in (whole.node_voltages[part.node_a],
                             whole.node_voltages[part.node_b]):
                part.ph_u = abs(whole.node_voltages[part.node_a]
                                - whole.node_voltages[part.node_b])
                return True
            return buffer
        self.node_voltages = [None] * len(self.nodes)
        self.node_voltages[circuit.node_a] = 0
        # nv[c.node_b] = u
        if unit == 'V':
            circuit.ph_u = amount
        elif unit == 'A':
            circuit.ph_i = amount
        else:
            raise RuntimeError(f'Not known unit "{unit}"" to calc.')
        while cv(self, circuit):
            pass


class Pos:
    def __init__(self, *a):
        while len(a) == 1:
            a = a[0]
        self.x_coord = int(a[0])
        self.y_coord = int(a[1])
        if len(a) > 2:
            self.orient = int(a[2])
        else:
            self.orient = -1

    @property
    def t_tuple(self):
        return (self.x_coord, self.y_coord, self.orient)

    @property
    def o_tuple(self):
        return (self.x_coord, self.y_coord)

    @t_tuple.setter
    def t_tuple(self, t_tuple):
        self.x_coord, self.y_coord, self.orient = t_tuple

    @o_tuple.setter
    def o_tuple(self, o_tuple):
        self.x_coord, self.y_coord = o_tuple

    def __repr__(self):
        return 'pos' + \
                repr(self.o_tuple if self.orient == -1 else self.t_tuple)


def ttoposa(tel):  # tel (two element) to pos A
    return Pos(tel.x_coord, tel.y_coord)


def ttoposb(tel):
    return Pos(tel.x_coord + 1, tel.y_coord) if tel.orient == 0 else \
           Pos(tel.x_coord, tel.y_coord + 1)


def pround(x_coord, y_coord, size, is_tel=False):
    if is_tel:
        x_coord /= size
        y_coord /= size
        x_shift = x_coord % 1 - 0.5
        y_shift = y_coord % 1 - 0.5
        x_coord //= 1
        y_coord //= 1
        if abs(x_shift) > abs(y_shift):
            return Pos(x_coord, y_coord, 1) if x_shift < 0 else \
                Pos(x_coord + 1, y_coord, 1)
        return Pos(x_coord, y_coord, 0) if y_shift < 0 else \
            Pos(x_coord, y_coord + 1, 0)
    x_coord = ((x_coord + 0.5 * size) // size)
    y_coord = ((y_coord + 0.5 * size) // size)
    return Pos(x_coord, y_coord)


class Element:
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

    def onkey(self, event):
        pass


class OElement(Element):
    def render(self, x_coord, y_coord, size):
        pass


class TElement(Element):
    def render(self, x_coord, y_coord, size, position):
        pass


class Pin(OElement):
    def __init__(self, parent, color='black'):
        super().__init__(parent)
        self.color = color
        deleted = []
        for oel in self.parent.oels:
            if str(self.parent.oels[oel]) == str(self):
                deleted += [oel]
        for oel in deleted:
            del self.parent.oels[oel]

    def render(self, x_coord, y_coord, size):
        radius = size * 0.1
        self.parent.w.create_arc(
            x_coord - radius, y_coord - radius,
            x_coord + radius, y_coord + radius,
            start=0, extent=180,
            outline=self.color, fill=self.color)
        self.parent.w.create_arc(x_coord - radius, y_coord - radius,
                                 x_coord + radius, y_coord + radius,
                                 start=180, extent=180,
                                 outline=self.color, fill=self.color)
        radius *= 2
        self.parent.w.create_arc(x_coord - radius, y_coord - radius,
                                 x_coord + radius, y_coord + radius,
                                 start=0, extent=180,
                                 outline=self.color, style='arc')
        self.parent.w.create_arc(x_coord - radius, y_coord - radius,
                                 x_coord + radius, y_coord + radius,
                                 start=180, extent=180,
                                 outline=self.color, style='arc')


class APin(Pin):
    def __init__(self, parent):
        super().__init__(parent, 'blue')


class BPin(Pin):
    def __init__(self, parent):
        super().__init__(parent, 'red')


class Wire(TElement):
    def render(self, x_coord, y_coord, size, position):
        self.parent.w.create_line(x_coord, y_coord, x_coord if position == 1
                                  else (x_coord + size),
                                  y_coord if position == 0
                                  else (y_coord + size))


class CanceledError(Exception):
    pass


class Resistor(Primitive, TElement):
    resistor_i = 1
    oR = None

    def __init__(self, parent, uid=None):
        super().__init__(parent)
        self.parent = parent
        if uid is None:
            uid = Resistor.resistor_i
            Resistor.resistor_i += 1
        self.uid = uid
        self.get_r()
        self.ph_u = None

    def get_r(self):
        new_value = None
        new_value = Resistor.oR
        new_value = self.parent.getFloat(
            'Value of R' + str(self.uid) + ' [' + get_unit('R') + ']')
        if new_value is None:
            raise CanceledError
        Resistor.oR = new_value
        self.ph_r = new_value

    @property
    def info(self):
        return {'R': self.ph_r, 'U': self.ph_u, 'I': self.ph_i} \
            if (self.ph_i is not None) and (self.ph_u is not None) \
            else {'R': self.ph_r}

    def __repr__(self):
        return '{' + str(self.uid) + '}'

    def render(self, x_coord, y_coord, size, position):
        if position == 0:
            self.parent.w.create_line(x_coord, y_coord,
                                      x_coord + 0.25 * size, y_coord)
            self.parent.w.create_line(x_coord + 0.75 * size, y_coord,
                                      x_coord + size, y_coord)
            self.parent.w.create_line(
                x_coord + 0.25 * size, y_coord + 0.2 * size,
                x_coord + 0.75 * size, y_coord + 0.2 * size)
            self.parent.w.create_line(
                x_coord + 0.25 * size, y_coord - 0.2 * size,
                x_coord + 0.75 * size, y_coord - 0.2 * size)
            self.parent.w.create_line(
                x_coord + 0.25 * size, y_coord + 0.2 * size,
                x_coord + 0.25 * size, y_coord - 0.2 * size)
            self.parent.w.create_line(
                x_coord + 0.75 * size, y_coord + 0.2 * size,
                x_coord + 0.75 * size, y_coord - 0.2 * size)
            self.parent.w.create_text(x_coord + 0.5 * size, y_coord,
                                      text=str(self.uid))
        if position == 1:
            self.parent.w.create_line(x_coord, y_coord,
                                      x_coord, y_coord + 0.25 * size)
            self.parent.w.create_line(x_coord, y_coord + 0.75 * size,
                                      x_coord, y_coord + size)
            self.parent.w.create_line(
                x_coord + 0.2 * size, y_coord + 0.25 * size,
                x_coord + 0.2 * size, y_coord + 0.75 * size)
            self.parent.w.create_line(
                x_coord - 0.2 * size, y_coord + 0.25 * size,
                x_coord - 0.2 * size, y_coord + 0.75 * size)
            self.parent.w.create_line(
                x_coord + 0.2 * size, y_coord + 0.25 * size,
                x_coord - 0.2 * size, y_coord + 0.25 * size)
            self.parent.w.create_line(
                x_coord + 0.2 * size, y_coord + 0.75 * size,
                x_coord - 0.2 * size, y_coord + 0.75 * size)
            self.parent.w.create_text(
                x_coord, y_coord + 0.5 * size, text=str(self.uid), angle=270)


class Board:
    def __init__(self, WIDTH=1280, HEIGHT=720, s=40):
        self.size = Pos(WIDTH, HEIGHT)
        self.elsize = s  # size of one element
        self.tels = {}  # elements with (x, y, p)
        self.oels = {}  # elements with (x, y)
        self.tkroot = tk.Tk()
        self.canvas = tk.Canvas(self.tkroot, width=WIDTH,
                                height=HEIGHT, bd=0, highlightthickness=0)
        self.aself = [self]
        self.make_tk()
        self.canvas.pack(expand=True)
        self.canvas.focus_set()
        self.in_motion = Pos(-1, -1)
        self.shift = Pos(0, 0)
        self.newpos = Pos(0, 0)
        self.newself = False
        self.x_coord = 0
        self.y_coord = 0
        self.nodes = Nodes()
        self.lastfile = None
        self.queue = []
        self.powerv = True  # power voltage
        self.power = 12
        self.crc = Primitive(math.inf)  # CiRCuit :D easy to remember
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

    def dump(self):
        buffer = self.tkroot, self.canvas
        del self.tkroot, self.canvas
        dumped = pickle.dumps(self)
        self.tkroot, self.canvas = buffer
        return dumped

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
        file_menu.add_command(label='New', command=self.new_sketch,
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
            command=lambda: self.with_click(lambda p: self.delete(p[0], p[1])),
            accelerator='Del')
        edit_menu.add_command(label='Delete all', command=self.new_sketch,
                              accelerator='Shift+Del')
        menu_bar.add_cascade(label='Edit', menu=edit_menu)
        # -----
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label='Zoom in',
                              command=lambda: self.zoom(+1), accelerator='+')
        view_menu.add_command(label='Zoom out',
                              command=lambda: self.zoom(-1), accelerator='-')
        view_menu.add_command(label='Count resistors',
                              command=self.count, accelerator='\'')
        menu_bar.add_cascade(label='View', menu=view_menu)
        # -----
        power_menu = tk.Menu(menu_bar, tearoff=0)
        power_menu.add_command(label='Voltage', command=lambda: self.set_power(
            True, self.get_float('Voltage [' + get_unit('U') + ']')))
        power_menu.add_command(label='Current', command=lambda: self.set_power(
            False, self.get_float('Current [' + get_unit('I') + ']')))
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

    def load(self, data):
        buffer = self.tkroot, self.canvas
        loaded = pickle.loads(data)
        loaded.tk, loaded.w = buffer
        loaded.make_tk()
        self.newself = loaded

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

    def new(self, _type, x_coord, y_coord):
        try:
            if issubclass(_type, TElement):
                self.tels[pround(x_coord, y_coord,
                                 self.elsize, True).t_tuple] = _type(self)
            if issubclass(_type, OElement):
                self.oels[pround(x_coord, y_coord,
                                 self.elsize).o_tuple] = _type(self)
        except CanceledError:
            pass

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
        for teli, tel in self.tels.items():
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
        for oeli, oel in self.oels.items():
            oeli = Pos(oeli)
            oel.render(oeli.x_coord * self.elsize - self.x_coord,
                       oeli.y_coord * self.elsize - self.y_coord, self.elsize)
        self.tkroot.update_idletasks()
        self.tkroot.update()
        if self.auto.get():
            self.calc()
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
        if self.in_motion.t_tuple in self.tels.keys() \
            and pround(event.x + self.x_coord, event.y + self.y_coord,
                       self.elsize, True).t_tuple != self.in_motion.t_tuple:
            self.tels[pround(event.x + self.x_coord, event.y + self.y_coord,
                             self.elsize, True).t_tuple] = \
                self.tels[self.in_motion.t_tuple]
            self.tels.pop(self.in_motion.t_tuple)
        self.in_motion = Pos(-1, -1)
        self.shift = Pos(-1, -1)

    def motion1(self, event):
        self.newpos = Pos(event.x, event.y)

    def update_node(self):
        self.nodes.reset_nodes()
        for oel in self.oels:
            self.nodes.add_node(oel[0], oel[1])
        for tel in self.tels:
            if str(self.tels[tel]) == 'Wire':
                pos_a = ttoposa(Pos(tel))
                pos_b = ttoposb(Pos(tel))
                self.nodes.add_node(pos_a.x_coord, pos_a.y_coord,
                                    pos_b.x_coord, pos_b.y_coord)
            else:
                pos_a = ttoposa(Pos(tel))
                pos_b = ttoposb(Pos(tel))
                self.nodes.add_node(pos_a.x_coord, pos_a.y_coord)
                self.nodes.add_node(pos_b.x_coord, pos_b.y_coord)

    def calc_res(self):  # calc resistorers
        self.update_node()
        buffer = []
        for tel in self.tels:
            if str(self.tels[tel]) == 'Resistor':
                pos_a = ttoposa(Pos(tel))
                pos_b = ttoposb(Pos(tel))
                pos_a = self.nodes.search_node(pos_a.x_coord, pos_a.y_coord)
                pos_b = self.nodes.search_node(pos_b.x_coord, pos_b.y_coord)
                self.tels[tel].node_a = pos_a
                self.tels[tel].node_b = pos_b
                buffer += [self.tels[tel]]
        return buffer

    def calc(self):
        self.calc_res()
        start = end = -1
        for tel in self.tels.values():
            tel.ph_u = None
        for oel in self.oels:
            if str(self.oels[oel]) == 'APin':
                start = self.nodes.search_node(oel[0], oel[1])
            if str(self.oels[oel]) == 'BPin':
                end = self.nodes.search_node(oel[0], oel[1])
        if start == -1 or end == -1:
            if not self.auto.get():
                messagebox.showerror('Error', 'NO PINS SPECIFIED')
            self.crc = Primitive(math.inf)
            return
        crc = self.calc_res()
        crc = self.nodes.interpret(crc, start, end)
        if not self.auto.get():
            messagebox.showinfo('Result', repr(crc))
            messagebox.showinfo('Result', repr(crc.ph_r))
        self.crc = crc
        self.nodes.calc_voltages(crc, 'V' if self.powerv else 'A', self.power)

    def new_sketch(self):
        self.tels = {}
        self.oels = {}

    def count(self):
        Resistor.resistor_i = 1
        for tel in self.tels.values():
            if str(tel) == 'Resistor':
                tel.uid = Resistor.resistor_i
                Resistor.resistor_i += 1

    def zoom(self, inc):
        self.x_coord += self.x_coord // self.elsize
        self.y_coord += self.y_coord // self.elsize
        self.elsize += inc

    def interactive(self):
        code.InteractiveConsole({'self': self}).interact()

    def delete(self, x_coord, y_coord):
        if pround(x_coord, y_coord, self.elsize, True).t_tuple \
                in self.tels.keys():
            del self.tels[pround(x_coord, y_coord, self.elsize, True).t_tuple]
        if pround(x_coord, y_coord, self.elsize).o_tuple in self.oels.keys():
            del self.oels[pround(x_coord, y_coord, self.elsize).o_tuple]

    def onkey(self, event):
        # print(ev, ev.state)
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
            self.count()
        if (event.state & 1) != 0 and event.keysym == 'Delete':  # shift + del
            self.new_sketch()
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
                self.tels.keys():
            self.tels[pround(event.x, event.y, self.elsize, True).t_tuple] \
                .onkey(event)
        if pround(event.x, event.y, self.elsize).o_tuple in self.oels.keys():
            self.oels[pround(event.x, event.y, self.elsize).o_tuple] \
                .onkey(event)
        if event.keysym.upper() == 'S' and event.state == 0b100:  # Ctrl+S
            self.save()
        if event.keysym.upper() == 'S' and event.state == 0b101:  # Ctrl+Sh+S
            self.save(-1)
        if event.keysym.upper() == 'O' and event.state == 0b100:  # Ctrl+O
            self.open()

    def get_float(self, msg):
        buffer = simpledialog.askfloat('Input', msg,
                                       parent=self.tkroot, minvalue=0.0)
        self.canvas.focus_set()
        return buffer


if __name__ == '__main__':
    board = Board()
    if len(sys.argv) > 1:
        board.open(sys.argv[1])
    while 1:
        board = board.render()
