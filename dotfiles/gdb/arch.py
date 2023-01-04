#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2023 Nicolas Iooss
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
"""Add missing features to gdb.Architecture module

@author: Nicolas Iooss
@license: MIT
"""
import gdb
import re


class Architecture(gdb.Function):
    """Return the name of the architecture used by gdb"""

    def __init__(self):
        super(Architecture, self).__init__('architecture')

    def invoke(self):
        # Use gdb.Frame.architecture() if available
        if hasattr(gdb.Frame, 'architecture'):
            try:
                frame = gdb.newest_frame()
            except gdb.error:
                pass
            else:
                return frame.architecture().name()

        # Use "show architecture"
        show_arch = gdb.execute('show architecture', to_string=True)
        matches = re.search(r'\(currently (\S+)\)', show_arch)
        if matches is not None:
            return matches.group(1)
        raise gdb.GdbError("Unable to parse 'show architecture' output")


Architecture()
