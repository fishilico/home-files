#!/usr/bin/env python
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2023 Nicolas Iooss
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
"""Apply some settings to an XFCE Desktop environment

* Keyboard shortcuts
* Panel configuration
"""
import argparse
import collections
import json
import logging
import re
import os
import os.path
import subprocess
import sys


SHORTCUTS = (
    # Use urxvt as Alt+F3 if it is available, otherwise a terminal
    ('<Alt>F3', ('urxvt', 'xfce4-terminal', 'exo-open --launch TerminalEmulator')),

    # Lock screen with Ctrl+Alt+L
    ('<Primary><Alt>l', ('xflock4', )),

    # Take a screenshot with the screenshooter
    ('Print', ('xfce4-screenshooter', )),
)


logger = logging.getLogger(__name__)


class ActionArguments(object):  # pylint: disable=too-few-public-methods
    """Arguments to the program"""
    def __init__(self, do_for_real, verbose, home_dir):
        self.do_for_real = do_for_real
        self.verbose = verbose
        self.home_dir = os.path.expanduser(home_dir or '~')


def silent_run(cmd):
    """Run the given command, dropping its output, and return False if it failed"""
    logger.debug("running %s", ' '.join(cmd))
    try:
        subprocess.check_output(cmd)
        return True
    except subprocess.CalledProcessError as exc:
        logger.error("%s", exc)
        return False
    except OSError as exc:
        logger.error("%s", exc)
        return False


def try_run(cmd):
    """Try running the command and return its output on success, None on failure"""
    logger.debug("running: %s", ' '.join(cmd))
    try:
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        return None


def find_prog_in_path(prog):
    """Find the given program in the default $PATH"""
    for path_dir in ('/usr/bin', '/usr/sbin', '/bin', '/sbin'):
        path_prog = '{0}/{1}'.format(path_dir, prog)
        if os.path.exists(path_prog):
            return path_prog
    return None


def get_xfce4_shortcut(key):
    """Get the shortcut associated with the given key"""
    result = try_run([
        'xfconf-query', '--channel', 'xfce4-keyboard-shortcuts',
        '--property', '/commands/custom/{0}'.format(key)])
    if result is None:
        result = try_run([
            'xfconf-query', '--channel', 'xfce4-keyboard-shortcuts',
            '--property', '/commands/default/{0}'.format(key)])

    return result if result is None else result.decode('utf-8').rstrip('\n')


def set_xfce4_shortcut(act_args, key, cmd):
    """Set the shortcut associated with the given key"""
    current_cmd = get_xfce4_shortcut(key)
    if current_cmd == cmd:
        if act_args.verbose:
            logger.info("shortcut %s is already %r", key, cmd)
        return True

    if not act_args.do_for_real:
        logger.info("[dry run] shortcut %s: %r -> %r", key, current_cmd, cmd)
        return True

    logger.info("shortcut %s: %r -> %r", key, current_cmd, cmd)
    return silent_run([
        'xfconf-query', '--channel', 'xfce4-keyboard-shortcuts',
        '--property', '/commands/custom/{0}'.format(key),
        '--type', 'string', '--create', '--set', cmd])


def set_xfce4_shortcut_avail(act_args, key, progs):
    """Set the shortcut associated with the given key to the first available program"""
    for cmdline in progs:
        # Split the command line to find the used program
        cmd_split = cmdline.split(None, 1)
        cmd_split[0] = find_prog_in_path(cmd_split[0])
        if cmd_split[0] is not None:
            return set_xfce4_shortcut(act_args, key, ' '.join(cmd_split))
    logger.warning("no program found for shortcut %s", key)
    return True


def configure_xfce4_shortcuts(act_args):
    for key, progs in SHORTCUTS:
        if not set_xfce4_shortcut_avail(act_args, key, progs):
            return False
    return True


class Xfce4Panels(object):
    """Represent the state of the panels

    c.f. xfconf-query --channel xfce4-panel --list --verbose
    """
    # Key => type, default value
    panel_properties = (
        ('autohide-behavior', int, 0),
        ('length', int, 0),
        ('plugin-ids', [int], []),
        ('position', str, ''),
        ('position-locked', bool, False),
        ('size', int, 0),
    )
    # Name, key => type
    plugin_properties = (
        ('clock', 'digital-format', str),
        ('directorymenu', 'base-directory', str),
        ('launcher', 'items', [str]),
        ('separator', 'style', int),
        ('separator', 'expand', bool),
        ('systray', 'names-visible', [str]),
    )

    def __init__(self, act_args):
        self.act_args = act_args
        self.panels = None
        self.panel_plugins = None
        self.available_plugins = None

    @staticmethod
    def read_prop(prop, prop_type, default):
        """Read a property of xfce4-panel channel of the given type"""
        is_list = isinstance(prop_type, list) and len(prop_type) == 1 and default in ([], None)
        assert is_list or default is None or isinstance(default, prop_type)
        result = try_run([
            'xfconf-query', '--channel', 'xfce4-panel',
            '--property', prop])
        if result is None:
            return [] if is_list and default is not None else default
        lines = result.decode('utf-8').splitlines()
        if is_list:
            if len(lines) <= 2 or not lines[0].endswith(':') or lines[1] != '':
                raise ValueError("unexpected xfce4-panel%s value: %r" % (prop, lines))
            return [prop_type[0](line) for line in lines[2:]]
        if prop_type is bool and len(lines) == 1:
            if lines[0] == 'true':
                return True
            if lines[0] == 'false':
                return False
        if prop_type is int and len(lines) == 1:
            return int(lines[0])
        if prop_type is str and len(lines) == 1:
            return lines[0]
        raise NotImplementedError("unable to convert result to %r: %r" % (prop_type, lines))

    def set_panel_prop(self, panel_id, prop_name, value):
        """Set a panel property"""
        for prop, prop_type, default in self.panel_properties:
            if prop == prop_name:
                is_list = isinstance(prop_type, list) and len(prop_type) == 1
                if is_list:
                    assert all(isinstance(v, prop_type[0]) for v in value), \
                        "Wrong value type for panel property %s" % prop_name
                else:
                    assert isinstance(value, prop_type), \
                        "Wrong value type for panel property %s" % prop_name

                # Prepare the arguments for xfconf-query
                if is_list:
                    text_type = 'list'
                    text_value = str(value)  # TODO: how to modify lists?
                elif prop_type is bool:
                    text_type = 'bool'
                    text_value = 'true' if value else 'false'
                elif prop_type is int or prop_type is str:
                    text_type = 'int'
                    text_value = str(value)
                elif prop_type is str:
                    text_type = 'string'
                    text_value = value
                else:
                    raise NotImplementedError("unable to write a property of type %r" % prop_type)

                # Get the current value
                prop_path = '/panels/panel-{0}/{1}'.format(panel_id, prop_name)
                current_val = self.panels[panel_id][prop_name]
                if current_val == value:
                    if self.act_args.verbose:
                        logger.info("%s is already %r", prop_path, value)
                    return True

                if not self.act_args.do_for_real:
                    logger.info("[dry run] %s: %r -> %r", prop_path, current_val, value)
                    return True

                logger.info("%s: %r -> %r", prop_path, current_val, value)
                result = silent_run([
                    'xfconf-query', '--channel', 'xfce4-panel',
                    '--property', prop_path,
                    '--create', '--type', text_type, '--set', text_value])
                if not result:
                    return result

                # Sanity check
                new_value = self.read_prop(prop_path, prop_type, default)
                if new_value == current_val:
                    logger.error("failed to set %s to %r (old value stayed)", prop_path, value)
                    return False
                if new_value != value:
                    logger.error("failed to set %s to %r (new value %r)", prop_path, value, new_value)
                    return False
                return True

        raise NotImplementedError("unknown panel property %s" % prop_name)

    def read_file(self, file_rel_path):
        """Read a configuration file"""
        abs_path = os.path.join(
            self.act_args.home_dir, '.config', 'xfce4', 'panel', file_rel_path)
        logger.debug("reading %s", abs_path)
        try:
            with open(abs_path, 'r') as stream:
                return stream.read().splitlines()
        except OSError:
            return None

    def read_panels(self):
        """Retrieve the currently configured panels"""
        panel_ids = self.read_prop('/panels', [int], [])
        if not panel_ids:
            logger.error("failed to retrieve xfce4-panel/panels enumeration")
            return False
        self.panels = collections.OrderedDict()
        self.panel_plugins = collections.OrderedDict()
        for panel_id in panel_ids:
            if panel_id in self.panels:
                logger.error("duplicated xfce4-panel/panels ID %d", panel_id)
                return False
            prop_prefix = '/panels/panel-{0}/'.format(panel_id)
            self.panels[panel_id] = {}
            for prop, prop_type, default in self.panel_properties:
                try:
                    self.panels[panel_id][prop] = self.read_prop(prop_prefix + prop, prop_type, default)
                except ValueError as exc:
                    logger.error("%s", exc)
                    return False

            self.panel_plugins[panel_id] = collections.OrderedDict()
            for plugin_id in self.panels[panel_id]['plugin-ids']:
                # Read the plugin config
                prop_prefix = '/plugins/plugin-{0}'.format(plugin_id)
                plugin_name = self.read_prop(prop_prefix, str, '')
                self.panel_plugins[panel_id][plugin_id] = collections.OrderedDict()
                self.panel_plugins[panel_id][plugin_id]['name'] = plugin_name
                for plname, prop, prop_type in self.plugin_properties:
                    if plname != plugin_name:
                        continue
                    val = self.read_prop(prop_prefix + '/' + prop, prop_type, None)
                    if val is not None:
                        self.panel_plugins[panel_id][plugin_id][prop] = val

                # Read the files associated with the plugin
                if plugin_name == 'launcher':
                    # Load the .desktop file associated with a launcher
                    items = self.panel_plugins[panel_id][plugin_id].get('items')
                    if items:
                        self.panel_plugins[panel_id][plugin_id]['item-files'] = collections.OrderedDict()
                        for item_name in items:
                            content = self.read_file('{0}-{1}/{2}'.format(plugin_name, plugin_id, item_name))
                            self.panel_plugins[panel_id][plugin_id]['item-files'][item_name] = content
                elif plugin_name in ('cpugraph', 'fsguard', 'netload', 'systemload'):
                    content = self.read_file('{0}-{1}.rc'.format(plugin_name, plugin_id))
                    if content is not None:
                        self.panel_plugins[panel_id][plugin_id]['rc-file'] = content
        return True

    def read_available_plugins(self):
        """Load the available panel plugins"""
        plugins_path = '/usr/share/xfce4/panel/plugins'
        logger.debug("loading files from %s", plugins_path)
        available_plugins = set()
        for filename in os.listdir(plugins_path):
            if filename.endswith('.desktop'):
                with open(os.path.join(plugins_path, filename), 'r') as fplugin:
                    for line in fplugin:
                        if re.match(r'^X-XFCE-Module\s*=\s*(\S+)', line):
                            # The .desktop file is a module. Let's add its name!
                            available_plugins.add(filename[:-8])
                            break
        self.available_plugins = available_plugins
        return True

    def read_config(self):
        """Load all configuration options related to the panels"""
        if not self.read_panels():
            return False
        if not self.read_available_plugins():
            return False
        return True

    def dump_config(self, stream):
        """Print the loaded configuration"""
        json.dump(
            collections.OrderedDict((('panels', self.panels), ('plugins', self.panel_plugins))),
            stream, indent=2)
        stream.write('\n')

    def configure(self):
        """Apply configuration of the panels"""
        for panel_id, panel_config in sorted(self.panels.items()):
            if panel_config['position'] == 'p=10;x=0;y=0':
                # Bottom panel
                logger.info("Found bottom panel with ID %d", panel_id)
                if not self.set_panel_prop(panel_id, 'position-locked', True):
                    return False
                if not self.set_panel_prop(panel_id, 'length', 0):
                    return False
                # "Automatically hide the panel" -> "Always"
                if not self.set_panel_prop(panel_id, 'autohide-behavior', 2):
                    return False
            elif panel_config['position'] == 'p=6;x=0;y=0':
                # Top panel
                logger.info("Found top panel with ID %d", panel_id)
                if not self.set_panel_prop(panel_id, 'position-locked', True):
                    return False
                if not self.set_panel_prop(panel_id, 'length', 100):
                    return False
                if not self.set_panel_prop(panel_id, 'autohide-behavior', 0):
                    return False
        return True


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Apply settings to an XFCE Desktop environment")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="show debug messages")
    parser.add_argument('-n', '--dry-run',
                        dest='real', action='store_false', default=False,
                        help="show what would change with --real (default)")
    parser.add_argument('-r', '--real', action='store_true',
                        help="really change the settings")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="show the settings which would not be modified")
    parser.add_argument('-H', '--home', type=str,
                        help="$HOME environment variable to use")
    parser.add_argument('-P', '--show-panels', action='store_true',
                        help="show panels configuration")
    args = parser.parse_args(argv)

    logging.basicConfig(
        format='[%(levelname)s] %(message)s',
        level=logging.DEBUG if args.debug else logging.INFO)

    # Try using xfconf-query --version
    if not silent_run(['xfconf-query', '--version']):
        logger.fatal("xfconf-query does not work")
        return False

    act_args = ActionArguments(args.real, args.verbose, args.home)
    if not configure_xfce4_shortcuts(act_args):
        return False

    panels = Xfce4Panels(act_args)
    if not panels.read_config():
        return False
    if args.show_panels:
        panels.dump_config(sys.stdout)
    if not panels.configure():
        return False

    return True


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
