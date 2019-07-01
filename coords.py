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
