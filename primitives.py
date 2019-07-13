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


UNITS = {'R': '\N{OHM SIGN}', 'U': 'V', 'I': 'A'}


def get_unit(what):
    '''get_unit() translates the name of the variable to the corresponding unit
    of it.'''
    if what in UNITS:
        return UNITS[what]
    return ''


class Primitive:
    def __init__(self, r=None):
        if r is not None:
            self.ph_r = r
        self._ph_i, self._ph_u = None, None
        self.node_a, self.node_b = None, None
        self.data = []

    def __repr__(self):
        return '[' + str(self.ph_r) + ']'

    def __str__(self):
        return self.__class__.__name__

    @property
    def components(self):
        return self.data

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
    def ph_r(self):
        return 1 / sum(map(lambda x: 1 / x.ph_r, self.data))

    def update_r(self):
        for ele in self.data:
            ele.ph_u = self.ph_u


class Delta(Primitive):
    def __init__(self, x, y, z, i):
        super().__init__()
        self.data = [x, y, z]
        self.wiring_type = i
        self.ph_u = None

    def __repr__(self):
        return '\N{GREEK CAPITAL LETTER DELTA}(' + \
               ', '.join(map(repr, self.components + [self.wiring_type])) + ')'

    @property
    def ph_r(self):
        return {
            1: self.components[0].ph_r * self.components[1].ph_r,
            2: self.components[0].ph_r * self.components[2].ph_r,
            3: self.components[1].ph_r * self.components[2].ph_r
        }[self.wiring_type] / sum(map(lambda x: x.ph_r, self.components))
