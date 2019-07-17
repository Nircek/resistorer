#!/usr/bin/env python3
'''
str_holder helper
'''


class DuplicationError(RuntimeError):
    pass


class StrHolder:  # pylint: disable=R0903
    '''Database to find duplicates.'''
    def __init__(self):
        self.strs = []

    def add(self, string):
        '''Adds string to the database.'''
        if string in self.strs:
            raise DuplicationError(string + ' already in database')
        self.strs += [string]
