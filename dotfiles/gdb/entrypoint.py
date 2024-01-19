#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2024 Nicolas Iooss
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
"""Program entry-point-related gdb extensions

@author: Nicolas Iooss
@license: MIT
"""
from __future__ import with_statement

import gdb
import sys

# Python3 uses int() where Python2 used long()
to_int = int if sys.version_info >= (3, ) else long  # noqa


class EntryPoint(gdb.Function):
    """Return the entry point as known by "info files".

    Parse the output of "info files", which source is at:
    https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;a=blob;f=gdb/exec.c;
    h=124074ff50b50ced65342b25a01cf89d180e5a62;hb=7b582627bc42922de3b75792472f5223f1910277#l780
    """

    def __init__(self):
        super(EntryPoint, self).__init__('entrypoint')

    @staticmethod
    def get():
        lines = gdb.execute('info files', to_string=True).splitlines()
        iline = 0
        # Find the first line which begins with tab+backquote
        while iline < len(lines) and not lines[iline].startswith('\t`'):
            iline += 1
        iline += 1
        # Here, lines[iline] is the translation of "\tEntry point: 0xabd"
        if iline >= len(lines):
            raise ValueError("Unable to find the entry point in `info files'")
        return int(lines[iline].rsplit('0x', 1)[1], 16)

    def invoke(self):
        return gdb.Value(self.get()).cast(gdb.lookup_type("void").pointer())


class RunBreakEntry(gdb.Command):
    """Start the debugged program, stopping at its entry point.

    This is like "process launch --stop-at-entry" from LLDB.
    """
    def __init__(self):
        super(RunBreakEntry, self).__init__(
            'run-break-entry', gdb.COMMAND_BREAKPOINTS, gdb.COMPLETE_NONE)

    def invoke(self, args, from_tty):
        self.dont_repeat()

        # Because of ASLR, we need to first break into the dynamic loader by
        # loading an invalid breakpoint
        invalid_bp = gdb.Breakpoint('*-1', internal=True)
        try:
            gdb.execute('run', to_string=True)
        except gdb.error:
            pass
        else:
            raise gdb.GdbError("gdb managed to insert an invalid breakpoint!")
        invalid_bp.delete()

        # Create a temporary breakpoint at the address of the entry point
        addr = EntryPoint.get()

        # When there is no dynamic loader, we are already at the entry point
        if to_int(gdb.parse_and_eval('$pc')) == addr:
            return

        # Continue the program until the temporary breakpoint
        gdb.Breakpoint('*0x{:x}'.format(addr), temporary=True, internal=True)
        gdb.execute('continue')


EntryPoint()
RunBreakEntry()
