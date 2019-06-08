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
        self.nodes = []
        self.node_voltages = []

    def reset_nodes(self):
        self.nodes = []

    def search_node(self, x_coord, y_coord):
        try:
            return self.nodes.index((x_coord, y_coord))
        except ValueError:
            return -1

    def add_node(self, x_coord, y_coord, x2_coord=-1, y2_coord=-1):
        node_index = self.search_node(x_coord, y_coord)
        node2_index = self.search_node(x2_coord, y2_coord)
        new_index = -1
        if node_index == -1 and node2_index == -1:
            new_index = len(self.nodes)
            self.nodes += [[]]
        elif (node_index == -1) + (node2_index == -1) == 1:
            new_index = node_index + node2_index + 1  # a or b
        elif node_index != node2_index:
            self.nodes[node_index] += self.nodes[node2_index]
            del self.nodes[node2_index]
            return
        if (x_coord, y_coord) not in self.nodes[new_index] or \
                -1 in (x_coord, y_coord):
            self.nodes[new_index] += [(x_coord, y_coord)]
        if (x2_coord, y2_coord) not in self.nodes[new_index] or \
                -1 in (x2_coord, y2_coord):
            self.nodes[new_index] += [(x2_coord, y2_coord)]

    def interpret(self, data, start, end):  # pylint: disable=R0915, R0914
        # TODO: make circuits solver class and enable above
        # -----
        def datasearch(node_a, node_b=-1):  # search for all resistors connecting node_a and node_b
            results = []
            for i, connection in enumerate(data):
                if connection.node_a == node_a:
                    if node_b in (connection.node_b, -1):
                        results += [i]
                elif connection.node_b == node_a:
                    if node_b in (connection.node_a, -1):
                        results += [i]
            return results

        def n(i, l):
            '''i. resistor connects l and ... nodes'''
            return data[i].node_a + data[i].node_b - l

        def without(arr):
            r = []
            for i, connection in enumerate(data):
                if i not in arr:
                    r += [connection]
            return r

        def process_delta():
            for i in range(len(self.nodes)):
                for a in datasearch(i):
                    an = n(a, i)
                    for b in datasearch(an):
                        bn = n(b, an)
                        for c in datasearch(bn):
                            cn = n(c, bn)
                            if cn == i:
                                # print(i,an,bn,cn,data[a],data[b],data[c])
                                ndata = without((a, b, c))
                                da = Delta(data[a], data[b], data[c], 1)
                                db = Delta(data[a], data[b], data[c], 2)
                                dc = Delta(data[a], data[b], data[c], 3)
                                da.node_a, db.node_a, dc.node_a = an, cn, bn
                                da.node_b, db.node_b, dc.node_b = [
                                    len(self.nodes)] * 3
                                ndata += [da, db, dc]
                                return ndata
            return None

        def process_series():
            for i in range(len(self.nodes)):
                if i not in (start, end):
                    d = datasearch(i)
                    if len(d) == 2:
                        ndata = without(d)
                        nn = Series(data[d[0]], data[d[1]])
                        nn.node_a, nn.node_b = n(d[0], i), n(d[1], i)
                        ndata += [nn]
                        return ndata
            return None

        def process_parallel():
            for i, connection in enumerate(data):
                for j, connection2 in enumerate(data):
                    if i != j and (connection.node_a == connection2.node_a and connection.node_b == connection2.node_b) \
                            or (connection.node_a == connection2.node_b and connection.node_b == connection2.node_a):
                        ndata = without((i, j))
                        nn = Parallel(connection, connection2)
                        nn.node_a, nn.node_b = connection.node_a, connection.node_b
                        ndata += [nn]
                        return ndata
            return None

        def process_unnecessary():
            rmvd = []
            for i in range(len(self.nodes)):
                if i not in (start, end):
                    a = datasearch(i)
                    if len(a) == 1:
                        rmvd += a
            for i, connection in enumerate(data):
                if connection.node_a == connection.node_b:
                    rmvd += [i]
            return without(rmvd) if rmvd else None
        # -----
        toProcess = [process_unnecessary, process_series,
                     process_parallel, process_delta]
        odata = []
        # q = lambda x: x if (not x is None) else data
        while odata != data:
            odata = data[:]
            # print(odata)
            for e in toProcess:
                r = e()
                if r is not None:
                    data = r
                    if e == process_delta:  # pylint: disable=W0143
                        self.nodes += [[]]
                    break
        if not data:
            if start == end:
                return Primitive(0)
            return Primitive(math.inf)
        if len(data) == 1:
            return data[0]
        raise RuntimeError()

    def calc_voltages(self, c, v, x):  # calced
        if str(c) == 'Primitive':
            return

        def cv(p, d):  # calc voltage(parent, data)
            if str(d) == 'Primitive':
                return None
            r = False
            for e in d.components:
                r = cv(p, e)
            if (d.ph_u is not None) and ((p.node_voltages[d.node_a] is None) != (p.node_voltages[d.node_b] is None)) and d.node_a != c.node_b and d.node_b != c.node_b:  # '!=' = 'xor'
                if p.node_voltages[d.node_a] is None:
                    p.node_voltages[d.node_a] = p.node_voltages[d.node_b] + d.ph_u
                else:
                    p.node_voltages[d.node_b] = p.node_voltages[d.node_a] + d.ph_u
                return True
            if d.ph_u is None and (not ((p.node_voltages[d.node_a] is None) or (p.node_voltages[d.node_b] is None))):
                d.ph_u = abs(
                    p.node_voltages[d.node_a] - p.node_voltages[d.node_b])
                return True
            return r
        self.node_voltages = [None] * len(self.nodes)
        self.node_voltages[c.node_a] = 0
        # nv[c.node_b] = u
        if v:
            c.ph_u = x
        else:
            c.ph_i = x
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
        return 'pos' + repr(self.q if self.p == -1 else self.r)


def ttoposa(t):  # tel (two element) to pos A
    return pos(t.x, t.y)


def ttoposb(t):
    return pos(t.x + 1, t.y) if t.p == 0 else pos(t.x, t.y + 1)


def pround(x, y, s, xy):
    if xy == 2:
        x /= s
        y /= s
        sx = x % 1 - 0.5
        sy = y % 1 - 0.5
        x //= 1
        y //= 1
        if abs(sx) > abs(sy):
            return pos(x, y, 1) if sx < 0 else pos(x + 1, y, 1)
        return pos(x, y, 0) if sy < 0 else pos(x, y + 1, 0)
    x = ((x + 0.5 * s) // s)
    y = ((y + 0.5 * s) // s)
    return pos(x, y)


class element:
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

    def onkey(self, ev):
        pass


class oelement(element):
    def render(self, x, y, s):
        pass


class telement(element):
    def render(self, x, y, s, p):
        pass


class apin(oelement):
    def __init__(self, parent):
        super().__init__(parent)
        d = []
        for e in self.parent.oels.keys():
            if str(self.parent.oels[e]) == 'apin':
                d += [e]
        for e in d:
            del self.parent.oels[e]

    def render(self, x, y, s):
        r = s * 0.1
        self.parent.w.create_arc(
            x - r, y - r, x + r, y + r,
            start=0, extent=180,
            outline='blue', fill='blue')
        self.parent.w.create_arc(x - r, y - r, x + r, y + r,
                                 start=180, extent=180,
                                 outline='blue', fill='blue')
        r *= 2
        self.parent.w.create_arc(x - r, y - r, x + r, y + r,
                                 start=0, extent=180,
                                 outline='blue', style='arc')
        self.parent.w.create_arc(x - r, y - r, x + r, y + r,
                                 start=180, extent=180,
                                 outline='blue', style='arc')


class bpin(oelement):
    def __init__(self, parent):
        super().__init__(parent)
        d = []
        for e in self.parent.oels.keys():
            if str(self.parent.oels[e]) == 'bpin':
                d += [e]
        for e in d:
            del self.parent.oels[e]

    def render(self, x, y, s):
        r = s * 0.1
        self.parent.w.create_arc(x - r, y - r, x + r, y + r,
                                 start=0, extent=180,
                                 outline='red', fill='red')
        self.parent.w.create_arc(x - r, y - r, x + r, y + r,
                                 start=180, extent=180,
                                 outline='red', fill='red')
        r *= 2
        self.parent.w.create_arc(x - r, y - r, x + r, y + r,
                                 start=0, extent=180,
                                 outline='red', style='arc')
        self.parent.w.create_arc(x - r, y - r, x + r, y + r,
                                 start=180, extent=180,
                                 outline='red', style='arc')


class wire(telement):
    def render(self, x, y, s, p):
        self.parent.w.create_line(x, y, x if p == 1 else (
            x + s), y if p == 0 else (y + s))

    @property
    def r(self):
        return 0


class CanceledError(Exception):
    pass


class resistor(Primitive, telement):
    resistor_i = 1
    oR = None

    def __init__(self, parent, i=None):
        super().__init__(parent)
        self.parent = parent
        if i is None:
            i = resistor.resistor_i
            resistor.resistor_i += 1
        self.id = i
        self.getR()
        self.ph_u = None

    def getR(self):
        a = None
        a = resistor.oR
        a = self.parent.getFloat(
            'Value of R' + str(self.id) + ' [' + get_unit('R') + ']')
        if a is None:
            raise CanceledError
        resistor.oR = a
        self.ph_r = a

    @property
    def info(self):
        return {'R': self.ph_r, 'U': self.ph_u, 'I': self.ph_i} \
            if (self.ph_i is not None) and (self.ph_u is not None) \
            else {'R': self.ph_r}

    def __repr__(self):
        return '{' + str(self.id) + '}'

    def render(self, x, y, s, p):
        if p == 0:
            self.parent.w.create_line(x, y, x + 0.25 * s, y)
            self.parent.w.create_line(x + 0.75 * s, y, x + s, y)
            self.parent.w.create_line(
                x + 0.25 * s, y + 0.2 * s, x + 0.75 * s, y + 0.2 * s)
            self.parent.w.create_line(
                x + 0.25 * s, y - 0.2 * s, x + 0.75 * s, y - 0.2 * s)
            self.parent.w.create_line(
                x + 0.25 * s, y + 0.2 * s, x + 0.25 * s, y - 0.2 * s)
            self.parent.w.create_line(
                x + 0.75 * s, y + 0.2 * s, x + 0.75 * s, y - 0.2 * s)
            self.parent.w.create_text(x + 0.5 * s, y, text=str(self.id))
        if p == 1:
            self.parent.w.create_line(x, y, x, y + 0.25 * s)
            self.parent.w.create_line(x, y + 0.75 * s, x, y + s)
            self.parent.w.create_line(
                x + 0.2 * s, y + 0.25 * s, x + 0.2 * s, y + 0.75 * s)
            self.parent.w.create_line(
                x - 0.2 * s, y + 0.25 * s, x - 0.2 * s, y + 0.75 * s)
            self.parent.w.create_line(
                x + 0.2 * s, y + 0.25 * s, x - 0.2 * s, y + 0.25 * s)
            self.parent.w.create_line(
                x + 0.2 * s, y + 0.75 * s, x - 0.2 * s, y + 0.75 * s)
            self.parent.w.create_text(
                x, y + 0.5 * s, text=str(self.id), angle=270)


class Board:
    def __init__(self, WIDTH=1280, HEIGHT=720, s=40):
        self.SIZE = pos(WIDTH, HEIGHT)
        self.s = s  # size of one element
        self.tels = {}  # elements with (x, y, p)
        self.oels = {}  # elements with (x, y)
        self.tk = tk.Tk()
        self.w = tk.Canvas(self.tk, width=WIDTH,
                           height=HEIGHT, bd=0, highlightthickness=0)
        self.me = [self]
        self.makeTk()
        self.w.pack(expand=True)
        self.w.focus_set()
        self.in_motion = pos(-1, -1)
        self.shift = pos(0, 0)
        self.newpos = pos(0, 0)
        self.newself = False
        self.x = 0
        self.y = 0
        self.nodes = Nodes()
        self.lastfile = None
        self.queue = []
        self.powerv = True  # power voltage
        self.power = 12
        self.crc = Primitive(math.inf)  # CiRCuit :D easy to remember
        self.stop = tk.BooleanVar()

    def setPower(self, v, x):
        if x is None:
            return
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
        self.tk.title('Resistorer')
        self.w.bind('<Button 1>', self.onclick1)
        self.w.bind('<ButtonRelease-1>', self.onrel1)
        self.w.bind('<B1-Motion>', self.motion1)
        self.w.bind('<KeyPress>', self.onkey)
        self.tk.bind('<Configure>', self.configure)
        self.tk.protocol('WM_DELETE_WINDOW', lambda: self.stop.set(True))
        # -----
        mb = tk.Menu(self.tk)
        fm = tk.Menu(mb, tearoff=0)
        fm.add_command(label='New', command=self.newSketch,
                       accelerator='Shift+Del')
        fm.add_command(label='Open', command=self.open, accelerator='Ctrl+O')
        fm.add_command(label='Save', command=self.save, accelerator='Ctrl+S')
        fm.add_command(label='Save as...',
                       command=lambda: self.save(-1),
                       accelerator='Ctrl+Shift+S')
        fm.add_separator()
        fm.add_command(label='Exit', command=lambda: self.stop.set(
            True), accelerator='Alt+F4')
        mb.add_cascade(label='File', menu=fm)
        # -----
        em = tk.Menu(mb, tearoff=0)
        def ae(t): return lambda: self.withClick(
            lambda p: self.new(t, p[0], p[1]))  # add element
        em.add_command(label='Add a wire', command=ae(wire), accelerator='F2')
        em.add_command(label='Add a resistor',
                       command=ae(resistor), accelerator='F3')
        em.add_command(label='Add a + power supply',
                       command=ae(apin), accelerator='F4')
        em.add_command(label='Add a - power supply',
                       command=ae(bpin), accelerator='F5')
        em.add_separator()
        em.add_command(label='Delete element', command=lambda: self.withClick(
            lambda p: self.delete(p[0], p[1])), accelerator='Del')
        em.add_command(label='Delete all', command=self.newSketch,
                       accelerator='Shift+Del')
        mb.add_cascade(label='Edit', menu=em)
        # -----
        vm = tk.Menu(mb, tearoff=0)
        vm.add_command(label='Zoom in',
                       command=lambda: self.zoom(+1), accelerator='+')
        vm.add_command(label='Zoom out',
                       command=lambda: self.zoom(-1), accelerator='-')
        vm.add_command(label='Count resistors',
                       command=self.count, accelerator='\'')
        mb.add_cascade(label='View', menu=vm)
        # -----
        pm = tk.Menu(mb, tearoff=0)
        pm.add_command(label='Voltage', command=lambda: self.setPower(
            True, self.getFloat('Voltage [' + get_unit('U') + ']')))
        pm.add_command(label='Current', command=lambda: self.setPower(
            False, self.getFloat('Current [' + get_unit('I') + ']')))
        mb.add_cascade(label='Power supply', menu=pm)
        # -----
        dm = tk.Menu(mb, tearoff=0)
        dm.add_command(label='Open a console',
                       command=self.interactive, accelerator='\\')
        self.auto = tk.BooleanVar()
        self.auto.set(True)
        dm.add_checkbutton(label='Auto calculating',
                           onvalue=True, offvalue=False, variable=self.auto)
        dm.add_command(label='Calculate', command=self.calc,
                       accelerator='Enter')
        mb.add_cascade(label='Debug', menu=dm)
        # -----
        self.tk.config(menu=mb)

    def load(self, data):
        a, b = self.tk, self.w
        r = pickle.loads(data)
        r.tk, r.w = a, b
        r.makeTk()
        self.newself = r

    def open(self, file=None):
        if file is None:
            file = filedialog.askopenfilename(filetypes=(
                ('sketch files', '*.sk'), ('all files', '*.*')))
        if not file:
            return False
        f = open(file, mode='rb')
        self.load(f.read())
        f.close()
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
        f = open(file, mode='wb')
        f.write(self.dump())
        self.lastfile = file
        f.close()
        return True

    def new(self, cl, x, y):
        try:
            if issubclass(cl, telement):
                p = pround(x, y, self.s, 2)
                self.tels[p.r] = cl(self)
            if issubclass(cl, oelement):
                p = pround(x, y, self.s, 1)
                self.oels[p.q] = cl(self)
        except CanceledError:
            pass

    def point(self, p):
        self.w.create_oval(p.x, p.y, p.x, p.y, width=1, fill='black')

    def render(self):
        if self.stop.get():
            sys.exit()
        self.w.delete('all')
        for x in range(self.x // self.s, (self.SIZE.x + self.x) // self.s + 1):
            for y in range(self.y // self.s, (self.SIZE.y + self.y) // self.s + 1):
                self.point(pos(x * self.s - self.x, y * self.s - self.y))
        txt = ''
        for p, e in self.tels.items():
            if str(e) == 'resistor':
                txt += repr(e)
                first = True
                for f, g in e.info.items():
                    if first:
                        first = False
                    else:
                        txt += len(repr(e)) * ' '
                    txt += ' ' + f + '=' + str(g) + ' ' + get_unit(f) + '\n'
                if txt[-1] != '\n':
                    txt += '\n'
            p = pos(p)
            if p.r != self.in_motion.r:
                e.render(p.x * self.s - self.x, p.y *
                         self.s - self.y, self.s, p.p)
            else:
                e.render(self.newpos.x - self.shift.x,
                         self.newpos.y - self.shift.y, self.s, p.p)
        txt += 'R\N{LATIN SMALL LETTER Z WITH STROKE}=' + \
            ('\N{INFINITY}' if self.crc.ph_r ==
             math.inf else str(self.crc.ph_r))
        u = str(self.power if self.powerv else (
            0 if math.isnan(self.crc.ph_r * self.power) else (
                self.crc.ph_r * self.power if self.crc.ph_r * self.power != math.inf
                else '\N{INFINITY}')))
        i = str(self.power if (not self.powerv) else (
            '\N{INFINITY}' if (self.crc.ph_r == 0) else (
                self.power / self.crc.ph_r)))
        txt += ' U=' + u + ' I=' + i
        self.w.create_text(0, self.SIZE.y, font='TkFixedFont',
                           anchor='sw', text=txt)
        for p, e in self.oels.items():
            p = pos(p)
            e.render(p.x * self.s - self.x, p.y * self.s - self.y, self.s)
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
        self.in_motion = pround(ev.x + self.x, ev.y + self.y, self.s, 2)
        self.shift = pos(ev.x + self.x - self.in_motion.x *
                         self.s, ev.y + self.y - self.in_motion.y * self.s)
        self.newpos = pos(ev.x, ev.y)

    def onrel1(self, ev):
        if self.in_motion.r in self.tels.keys() \
            and pround(ev.x + self.x, ev.y + self.y, self.s, 2).r \
                != self.in_motion.r:
            self.tels[pround(ev.x + self.x, ev.y + self.y,
                             self.s, 2).r] = self.tels[self.in_motion.r]
            self.tels.pop(self.in_motion.r)
        self.in_motion = pos(-1, -1)
        self.shift = pos(-1, -1)

    def motion1(self, ev):
        self.newpos = pos(ev.x, ev.y)

    def updateNode(self):
        self.nodes.reset_nodes()
        for e in self.oels:
            self.nodes.add_node(e[0], e[1])
        for e in self.tels:
            if str(self.tels[e]) == 'wire':
                a = ttoposa(pos(e))
                b = ttoposb(pos(e))
                self.nodes.add_node(a.x, a.y, b.x, b.y)
            else:
                a = ttoposa(pos(e))
                b = ttoposb(pos(e))
                self.nodes.add_node(a.x, a.y)
                self.nodes.add_node(b.x, b.y)

    def calc_res(self):  # calc resistorers
        self.updateNode()
        r = []
        for e in self.tels:
            if str(self.tels[e]) == 'resistor':
                a = ttoposa(pos(e))
                b = ttoposb(pos(e))
                a = self.nodes.search_node(a.x, a.y)
                b = self.nodes.search_node(b.x, b.y)
                self.tels[e].node_a = a
                self.tels[e].node_b = b
                r += [self.tels[e]]
        return r

    def calc(self):
        self.calc_res()
        start = end = -1
        for e in self.tels.values():
            e.ph_u = None
        for e in self.oels.keys():
            if str(self.oels[e]) == 'apin':
                start = self.nodes.search_node(e[0], e[1])
            if str(self.oels[e]) == 'bpin':
                end = self.nodes.search_node(e[0], e[1])
        if start == -1 or end == -1:
            if not self.auto.get():
                messagebox.showerror('Error', 'NO PINS SPECIFIED')
            self.crc = Primitive(math.inf)
            return
        a = self.calc_res()
        a = self.nodes.interpret(a, start, end)
        if not self.auto.get():
            messagebox.showinfo('Result', repr(a))
            messagebox.showinfo('Result', repr(a.ph_r))
        self.crc = a
        self.nodes.calc_voltages(a, self.powerv, self.power)

    def newSketch(self):
        self.tels = {}
        self.oels = {}

    def count(self):
        resistor.resistor_i = 1
        for e in self.tels.values():
            if str(e) == 'resistor':
                e.i = resistor.resistor_i
                resistor.resistor_i += 1

    def zoom(self, x):
        s = self.s
        self.s += x
        self.x += self.x // s
        self.y += self.y // s

    def interactive(self):
        code.InteractiveConsole({'self': self}).interact()

    def delete(self, x, y):
        if pround(x, y, self.s, 2).r in self.tels.keys():
            del self.tels[pround(x, y, self.s, 2).r]
        if pround(x, y, self.s, 1).q in self.oels.keys():
            del self.oels[pround(x, y, self.s, 1).q]

    def onkey(self, ev):
        # print(ev, ev.state)
        ev.x += self.x
        ev.y += self.y
        if len(ev.keysym) > 1 and ev.keysym[:1] == 'F':
            nr = int(ev.keysym[1:]) - 1
            gates = [element, wire, resistor, apin, bpin]
            if len(gates) <= nr:
                messagebox.showerror(
                    'Error', 'NO F' + str(nr + 1) + ' ELEMENT')
            else:
                b = gates[nr]
                self.new(b, ev.x, ev.y)
        if ev.keysym == 'Enter' or ev.keysym == 'Return':
            self.calc()
        if ev.keysym == 'backslash':
            self.interactive()
        if ev.keysym == 'apostrophe' or ev.keysym == 'quoteright':
            self.count()
        if (ev.state & 1) != 0 and ev.keysym == 'Delete':  # shift + del
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
        if ev.keysym.upper() == 'S' and ev.state == 0b100:  # Ctrl+S
            self.save()
        if ev.keysym.upper() == 'S' and ev.state == 0b101:  # Ctrl+Shift+S
            self.save(-1)
        if ev.keysym.upper() == 'O' and ev.state == 0b100:  # Ctrl+O
            self.open()

    def getFloat(self, msg):
        a = simpledialog.askfloat('Input', msg, parent=self.tk, minvalue=0.0)
        self.w.focus_set()
        return a


if __name__ == '__main__':
    board = Board()
    if len(sys.argv) > 1:
        board.open(sys.argv[1])
    while 1:
        board = board.render()
