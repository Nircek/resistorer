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

from primitives import Primitive
from board_editor import input_resistance


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


class Resistor(Primitive, TElement):
    resistor_i = 1
    old_r = None

    def __init__(self, parent, uid=None):
        super().__init__(parent)
        self.parent = parent
        if uid is None:
            uid = Resistor.resistor_i
            Resistor.resistor_i += 1
        self.uid = uid
        self.ph_r = input_resistance(uid, self.parent.get_float)
        self.ph_u = None

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
