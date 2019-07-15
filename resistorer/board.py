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

from .elements import Resistor
from .circuit_solver import Nodes
from .coordinates import Pos, ttoposa, ttoposb


class NoPinsError(Exception):
    '''There are no pins specified and no calculation can be made.'''


class NothingHappenedError(Exception):
    '''Since the last calculation, input data hasn't changed
    so the calculations are the same as the last time.'''


class Board:
    '''The object containing all data about the board and Elements on it.'''
    def __init__(self):
        self.tels = {}  # elements with (x, y, p)
        self.oels = {}  # elements with (x, y)
        self.nodes = Nodes()
        self.last_calc = None, None

    def new_tel(self, element, pos):
        '''Adds new TElement.'''
        self.tels[pos] = element

    def new_oel(self, element, pos):
        '''Adds new OElement.'''
        self.oels[pos] = element

    def update_node(self):
        '''Updates self.nodes object with the current state.'''
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
        '''Exports all Resistors with simplified connections between them.
        Connections can be accessed by .node_a and .node_b properties.'''
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

    def calc_res_bis(self, data=None):
        '''Exports all Resistors with simplified connections between them.
        Connections are represented in 0. and 2. items of tuple.'''
        if data is None:
            data = self.calc_res()
        return [(x.node_a, x, x.node_b) for x in data]

    def calc(self, force=False):
        '''Translates into the circuit (made from Primitives).'''
        if self.last_calc == repr((self.tels, self.oels)) and not force:
            raise NothingHappenedError
        self.last_calc = repr((self.tels, self.oels))
        self.calc_res()
        start = end = -1
        for tel in self.tels.values():
            tel.ph_u = None
        for oeli, oel in self.oels.items():
            if str(oel) == 'APin':
                start = self.nodes.search_node(oeli[0], oeli[1])
            if str(oel) == 'BPin':
                end = self.nodes.search_node(oeli[0], oeli[1])
        if -1 in (start, end):
            raise NoPinsError
        crc = self.calc_res()
        crc = self.nodes.interpret(crc, start, end)
        print(repr(crc), crc.ph_r)
        return crc

    def new_sketch(self):
        '''Deletes all Elements.'''
        self.tels = {}
        self.oels = {}

    def count(self):
        '''Recounts all indexes of all Resistors.'''
        Resistor.resistor_i = 1
        for tel in self.tels.values():
            if str(tel) == 'Resistor':
                tel.uid = Resistor.resistor_i
                Resistor.resistor_i += 1

    def del_tel(self, pos):
        '''Deletes the TElement.'''
        if pos in self.tels.keys():
            del self.tels[pos]

    def del_oel(self, pos):
        '''Deletes the OElement.'''
        if pos in self.oels.keys():
            del self.oels[pos]
