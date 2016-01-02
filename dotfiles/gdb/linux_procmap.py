#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015-2016 Nicolas Iooss
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""Define pmap command, like the shell command, but for gdb inferiors.

@author: Nicolas Iooss
@license: MIT
"""
import gdb


class ProcMap(gdb.Command):
    """Show the content of /proc/$PID/maps.

    Like "info proc mappings", but with the permissions too.
    Optional argument: inferior ID
    """
    def __init__(self):
        super(ProcMap, self).__init__(
            'pmap', gdb.COMMAND_STATUS, gdb.COMPLETE_NONE)

    @staticmethod
    def show(pid):
        path = '/proc/{}/maps'.format(pid)
        gdb.write("{}:\n".format(path))
        with open(path, 'r') as fmaps:
            for line in fmaps:
                gdb.write(line)

    def invoke(self, args, from_tty):
        if args:
            inferiors = gdb.inferiors()
            for inf_id_str in args:
                inf_id = to_int(inf_id_str)
                found = False
                for inf in inferiors:
                    if inf.num == inf_id:
                        self.show(inf.pid)
                        found = True
                        break
                if not found:
                    raise gdb.GdbError("Unknown inferior {}.".format(inf_id))
        else:
            pid = gdb.selected_inferior().pid
            if pid == 0:
                raise gdb.GdbError("No current inferior.")
            self.show(pid)

ProcMap()
