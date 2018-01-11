#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2018 Nicolas Iooss
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
"""Handle Linux syscalls

@author: Nicolas Iooss
@license: MIT
"""
import gdb


# Syscall parameters and return values, depending on the architecture
# Order: syscall number, 6 parameters, return value
SYSCALL_REGS = {
    'arm': ('r7', 'r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r0'),
    'i386': ('eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp', 'eax'),
    'i386:x86-64': ('rax', 'rdi', 'rsi', 'rdx', 'r10', 'r8', 'r9', 'rax'),
}


class SyscallArg(gdb.Function):
    """Return the value of the given syscall argument

    * 1- 6 are the syscall arguments
    * 0 is the syscall number
    * -1 is the syscall return value

    This is intended to be used in a "catch syscall" handler
    """
    def __init__(self):
        super(SyscallArg, self).__init__('syscallarg')

    def invoke(self, num):
        num = int(num)
        if not -1 <= num <= 6:
            raise gdb.GdbError("Invalid syscall argument index")
        arch = gdb.newest_frame().architecture().name()
        if arch not in SYSCALL_REGS:
            raise gdb.GdbError("Unimplemented syscallarg for {}".format(arch))
        return gdb.parse_and_eval('$' + SYSCALL_REGS[arch][num])


class SetSyscallArg(gdb.Command):
    """Set the value of the given syscall argument

    * 1- 6 are the syscall arguments
    * 0 is the syscall number
    * -1 is the syscall return value

    This is intended to be used in a "catch syscall" handler
    """
    def __init__(self):
        super(SetSyscallArg, self).__init__(
            'set-syscallarg', gdb.COMMAND_DATA, gdb.COMPLETE_NONE)

    def invoke(self, args, from_tty):
        _args = args.split(None, 1)
        num = int(_args[0])
        if not -1 <= num <= 6:
            raise gdb.GdbError("Invalid syscall argument index")
        arch = gdb.newest_frame().architecture().name()
        if arch not in SYSCALL_REGS:
            raise gdb.GdbError("Unimplemented syscallarg for {}".format(arch))
        gdb.execute('set ${} = {}'.format(SYSCALL_REGS[arch][num], _args[1]))


SyscallArg()
SetSyscallArg()
