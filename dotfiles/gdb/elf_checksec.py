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
"""Display various security settings for the currently debugged ELF file

See also checksec script:
http://www.trapkit.de/tools/checksec.html (.sh to download the script)

@author: Nicolas Iooss
@license: MIT
"""
import gdb
import re
import subprocess


class ElfCheckSec(gdb.Command):
    """Display various security settings for the current ELF file"""
    def __init__(self):
        super(ElfCheckSec, self).__init__(
            'checksec', gdb.COMMAND_STATUS, gdb.COMPLETE_NONE)

    @staticmethod
    def get_filename():
        """Get the filename of the currently debugging program"""
        lines = gdb.execute('info files', to_string=True).splitlines()
        for line in lines:
            matches = re.match(r"\t`(.*)', ", line)
            if matches is not None:
                return matches.group(1)
        raise gdb.GdbError("Unable to find the current file")

    @staticmethod
    def checksec(filename):
        def red(msg):
            return '\033[1;31m' + msg + '\033[m'

        def yellow(msg):
            return '\033[1;33m' + msg + '\033[m'

        def green(msg):
            return '\033[32m' + msg + '\033[m'

        description_relro = {
            0: red('none'),
            1: yellow('partial (relro without bind_now)'),
            2: red('bind_now without relro'),
            3: green('full (relro + bind_now)'),
        }
        description_nx = {
            -1: yellow('unknown'),
            0: red('disabled'),
            1: green('enabled'),
        }
        description_pie = {
            -1: yellow('unknown'),
            0: red('disabled (executable file)'),
            1: green('enabled (dynamic shared object)'),
            2: green('enabled (position-independant executable)'),
        }

        status_relro = 0
        status_nx = -1
        status_pie = -1
        has_canary = False
        has_fortify = False

        output = subprocess.check_output(['readelf', '-a', '-W', filename])
        for line in output.decode('utf8', errors='ignore').splitlines():
            if line.startswith('  GNU_RELRO '):
                # GNU_RELRO in program header
                status_relro = status_relro | 1
            elif re.match(r' *0x[0-9a-f]+ \(BIND_NOW\)', line):
                # BIND_NOW in the dynamic section
                status_relro = status_relro | 2
            elif re.match(r' *0x[0-9a-f]+ \(FLAGS\) +BIND_NOW', line):
                # BIND_NOW in the FLAGS of dynamic section
                status_relro = status_relro | 2
            elif re.match(r' *0x[0-9a-f]+ \(FLAGS_1\) +Flags:.* NOW', line):
                # BIND_NOW in the FLAGS_1 of dynamic section
                status_relro = status_relro | 2
            elif line.startswith('  GNU_STACK '):
                # GNU_STACK in program header
                # Retrieve "RWE" permissions in the 7th column
                perms = line.split(None, 6)[6][:3]
                if perms == 'RWX':
                    status_nx = 0
                elif perms == 'RW ':
                    status_nx = 1
                else:
                    gdb.write("Warning: unknown GNU_STACK {}\n".format(perms))
            elif line.startswith('  Type: ') and status_pie == -1:
                # Type field in file header
                elf_type = line.split(None, 1)[1]
                if elf_type == 'EXEC (Executable file)':
                    status_pie = 0
                elif elf_type == 'DYN (Shared object file)':
                    status_pie = 1
                else:
                    gdb.write("Warning: unknown type {}\n".format(elf_type))
            elif re.match(r' *0x[0-9a-f]+ \(DEBUG\) ', line):
                # DEBUG in dynamic section
                if status_pie == 1:
                    status_pie = 2
            elif ' __stack_chk_fail' in line:
                # __stack_chk_fail dynamic symbols table
                has_canary = True
            elif '_chk@' in line:
                # Heuristic with fortify symbols
                has_fortify = True

        gdb.write("{}:\n".format(filename))
        gdb.write("  RELRO: {}\n".format(description_relro[status_relro]))
        gdb.write("  NX: {}\n".format(description_nx[status_nx]))
        gdb.write("  PIE: {}\n".format(description_pie[status_pie]))
        gdb.write("  Stack canary: {}\n".format(
            green('found') if has_canary else red('not found')))
        gdb.write("  Fortify: {}\n".format(
            green('enabled') if has_fortify else yellow("not found")))

    def invoke(self, args, from_tty):
        if args:
            for filename in args.split():
                self.checksec(filename)
        else:
            self.checksec(self.get_filename())

ElfCheckSec()
