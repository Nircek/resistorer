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

from math import inf

from primitives import Primitive, Series, Parallel, Delta, get_unit


class Nodes:
    '''Object holding info about all nodes (points or coordinates on the Board
    which are connected with Wire). It is needed to translate and simplify
    the Board into a circuit made from Primitives.'''
    def __init__(self):
        self.nodes = {}
        self.node_voltages = []
        self.data = []
        self.start, self.end = (-1,) * 2

    def reset_nodes(self):
        '''Deletes all known nodes.'''
        self.nodes = []

    def search_node(self, x_coord, y_coord):
        '''Looks for the index of the node which contains x_coord, y_coord.'''
        for i, ele in enumerate(self.nodes):
            if (x_coord, y_coord) in ele:
                return i
        return -1

    def add_node(self, x_coord, y_coord, x2_coord=-1, y2_coord=-1):
        '''Adds new node with a position x_coord, y_coord. There can be
        specified x2_coord, y2_coord to connect the new (or existing) first
        node with the new (or existing) second node.'''
        node_index = self.search_node(x_coord, y_coord)
        node2_index = self.search_node(x2_coord, y2_coord)
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
        if (x_coord, y_coord) not in self.nodes[new_index] and \
                -1 not in (x_coord, y_coord):
            self.nodes[new_index] += [(x_coord, y_coord)]
        if (x2_coord, y2_coord) not in self.nodes[new_index] and \
                -1 not in (x2_coord, y2_coord):
            self.nodes[new_index] += [(x2_coord, y2_coord)]

    def datasearch(self, node_a, node_b=-1):
        '''Looks for all resistors connecting node_a and node_b.'''
        results = []
        for i, connection in enumerate(self.data):
            if connection.node_a == node_a:
                if node_b in (connection.node_b, -1):
                    results += [i]
            elif connection.node_b == node_a:
                if node_b in (connection.node_a, -1):
                    results += [i]
        return results

    def other_side(self, index, known):
        '''Gets another node of the element with the index.
        param index (int) - index of the element
        param known (int) - index of the known node which is connected
                            to the element
        '''
        return self.data[index].node_a + self.data[index].node_b - known

    def without(self, arr):
        '''Returns self.data without elements with indexes contained in arr.'''
        return list(map(lambda x: x[1],
                        filter(lambda x: x[0] not in arr,
                               enumerate(self.data))))

    def process_delta(self):
        '''Tries to find a Delta connection in the Board and process (simplify
        and remove old connections) it if present.'''
        for first_node in range(len(self.nodes)):
            for first in self.datasearch(first_node):
                second_node = self.other_side(first, first_node)
                for second in self.datasearch(second_node):
                    third_node = self.other_side(second, second_node)
                    for third in self.datasearch(third_node):
                        fourth_node = self.other_side(third, third_node)
                        if fourth_node == first_node:
                            ndata = self.without((first, second, third))
                            delta_a = Delta(self.data[first],
                                            self.data[second],
                                            self.data[third], 1)
                            delta_b = Delta(self.data[first],
                                            self.data[second],
                                            self.data[third], 2)
                            delta_c = Delta(self.data[first],
                                            self.data[second],
                                            self.data[third], 3)
                            delta_a.node_a, delta_b.node_a, \
                                delta_c.node_a = first_node, third_node, \
                                second_node
                            delta_a.node_b, delta_b.node_b, \
                                delta_c.node_b = [len(self.nodes)] * 3
                            ndata += [delta_a, delta_b, delta_c]
                            return ndata
        return None

    def process_series(self):
        '''Tries to find a Series connection in the Board and process (simplify
        and remove old connections) it if present.'''
        for node in range(len(self.nodes)):
            if node not in (self.start, self.end):
                connections = self.datasearch(node)
                if len(connections) == 2:
                    ndata = self.without(connections)
                    series = Series(self.data[connections[0]],
                                    self.data[connections[1]])
                    series.node_a, series.node_b = \
                        self.other_side(connections[0], node), \
                        self.other_side(connections[1], node)
                    ndata += [series]
                    return ndata
        return None

    def process_parallel(self):
        '''Tries to find a Parallel connection in the Board and process
        (simplify and remove old connections) it if present.'''
        for index, connection in enumerate(self.data):
            for index2, connection2 in enumerate(self.data):
                nodes_of_conn = connection.node_a, connection.node_b
                nodes_of_conn2 = connection2.node_a, connection2.node_b
                if index != index2 and nodes_of_conn in \
                        (nodes_of_conn2, nodes_of_conn2[::-1]):
                    ndata = self.without((index, index2))
                    parallel = Parallel(connection, connection2)
                    parallel.node_a, parallel.node_b = \
                        connection.node_a, connection.node_b
                    ndata += [parallel]
                    return ndata
        return None

    def process_unnecessary(self):
        '''Tries to find unnecessary connections in the Board and process
        (remove these connections) it if present.'''
        removed = []
        for node in range(len(self.nodes)):
            if node not in (self.start, self.end):
                connections = self.datasearch(node)
                if len(connections) == 1:
                    removed += connections
        for connection_i, connection in enumerate(self.data):
            if connection.node_a == connection.node_b:
                removed += [connection_i]
        return self.without(removed) if removed else None

    processors = [process_unnecessary, process_series,
                  process_parallel, process_delta]

    def interpret(self, data, start, end):
        '''Translates all data (Elements from the Board) to one circuit
        translation (made from Primitives), assuming that voltage or current
        is connected between start (int) and end (int) nodes.'''
        self.data, self.start, self.end = data, start, end
        old_data = []
        while repr(old_data) != repr(data):
            old_data = data[:]
            self.data = data
            for processor in self.processors:
                ndata = processor(self)
                if ndata is not None:
                    data = ndata
                    if repr(processor) == repr(Nodes.process_delta):
                        self.nodes += [[]]
                    break
        if not data:
            if start == end:
                return Primitive(0)
            return Primitive(inf)
        if len(data) == 1:
            return data[0]
        raise RuntimeError('Can\'t find a processor to simplify the circuit.')

    def recursive_figure_voltage(self, circuit, part):
        '''Tries to calculate and set all voltage drops to Primitives
        and Elements contained by the circuit.
        param circuit - the whole circuit
        param part - the currently analyzed part of the circuit'''
        if str(part) == 'Primitive':  # is Primitive has no voltage drop?
            return None
        buffer = False
        for component in part.components:
            buffer = self.recursive_figure_voltage(circuit, component)
        if (part.ph_u is not None) and \
                ((self.node_voltages[part.node_a] is None)
                 != (self.node_voltages[part.node_b] is None)) and \
                part.node_a != circuit.node_b and \
                part.node_b != circuit.node_b:  # '!=' = 'xor'
            if self.node_voltages[part.node_a] is None:
                self.node_voltages[part.node_a] = \
                    self.node_voltages[part.node_b] + part.ph_u
            else:
                self.node_voltages[part.node_b] = \
                    self.node_voltages[part.node_a] + part.ph_u
            return True
        if part.ph_u is None and \
            None not in (self.node_voltages[part.node_a],
                         self.node_voltages[part.node_b]):
            part.ph_u = abs(self.node_voltages[part.node_a]
                            - self.node_voltages[part.node_b])
            return True
        return buffer

    def calc_voltages(self, circuit, unit, amount):
        '''The launcher of recursive_figure_voltage which is calculating all
        voltage drops.
        param circuit - the calculated circuit (made from Primitives)
        param unit ('A' or 'V') - the unit of power
        param amount (int or float) - the value of power'''
        if str(circuit) == 'Primitive':
            return
        self.node_voltages = [None] * len(self.nodes)
        self.node_voltages[circuit.node_a] = 0
        if unit == get_unit('U'):
            circuit.ph_u = amount
        elif unit == get_unit('I'):
            circuit.ph_i = amount
        else:
            raise RuntimeError(f'Not known unit "{unit}"" to calc.')
        while self.recursive_figure_voltage(circuit, circuit):
            pass
