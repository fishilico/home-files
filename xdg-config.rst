Why is there no XDG automatic installation?
===========================================

Applications store their settings in ``$XDG_CONFIG_HOME`` directory (often
``$HOME/.config``). This directory contains really many settings.
``$HOME/.local/share`` is another directory often modified by applications.
Nevertheless both these directories depend on installed applications and are
populated with default settings even if the user didn't do anything, so it's
a bad idea to copy-paste these files in a smart backup (because almost nothing
is important).

If you wish to copy your configuration from a system to another, you may want
to issue the corresponding ``dconf`` commands (or ``xfconf-query`` with XFCE)
and put the result in a file. ``dconf`` has also an utility to dump and load
data. For example following command dumps your Gedit configuration::

    dconf dump /org/gnome/gedit/

For example to change the default GNOME monospace font (used by gedit), run::

    dconf write /org/gnome/desktop/interface/monospace-font-name "'Droid Sans Mono 10'"
