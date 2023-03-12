home-files
==========

Files shared in all my home directories.

This project groups together the files which make life easier when using a
Linux-based system (desktop workstation, laptop, server, virtual machine...).
It contains the configuration settings of the software I use (shell, editors,
terminals...) and some scripts which are swiftly accessible from the command
line.


Directories
-----------

* ``bin/``: scripts which can make some tasks faster by being present in the
  ``$PATH``.  These scripts are installed as symlinks in ``$HOME/bin``.
* ``dotfiles/``: configuration files which are prefixed by a dot in ``$HOME``
  (to hide them in usual directory listings).  This includes settings for
  shells (bash, zsh...), git, vim, urxvt, python, etc.
* ``specific/``: configuration files which are really specific to some of my
  systems (for example there is a VLC addon to read YouTube playlists).
* ``tests/``: scripts which check the style of the files (PEP8-compliance of
  Python scripts, copyright information, etc.).
* ``xdgconfig/``: settings for Desktop Environments which do not use plain old
  text files.  These DE usually build a database and an provide an API which
  makes saving & restoring settings way harder than it has to be.  Nonetheless
  parts of such a task can be automated.


Some commands
-------------

* Install binary files in ``$HOME/bin`` and hidden files (in ``dotfiles``) in
  ``$HOME``, after validating the GnuPG signatures in the last git commits::

    ./install.sh

* Update the repository in a way more secure than ``git pull``, by verifying
  the GPG signature of incoming commits::

    ./update.sh

* Update MIME database after installation on a desktop system::

    cd ~/.local/share && update-mime-database mime

* Run various tests::

    ./run_tests


`Circle-CI`_ status
-------------------

.. _Circle-CI: https://circleci.com/

.. image:: https://circleci.com/gh/fishilico/home-files.png?style=shield
  :target: https://circleci.com/gh/fishilico/home-files
