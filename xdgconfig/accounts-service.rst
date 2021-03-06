Accounts Service files
======================

Accounts Service provides account-specific data to be used by other systems.
For example when a session manager (GDM, LightDM, ...) uses a profile picture
to identify users, it may use ``$HOME/.face`` file, which is a PNG image.

Another location to provide such image is ``/var/lib/AccountsService/icons/``.
This directory may contain user-named files which are PNG profile pictures.

Moreover ``/var/lib/AccountsService/users/`` directory contains user-named files
in ``.desktop`` format which specifies some preferences. For example, a French
user named ``toto`` using XFCE has file ``/var/lib/AccountsService/users/toto``
containing::

    [User]
    Language=fr_FR
    XSession=xfce
    Icon=/var/lib/AccountsService/icons/toto
    SystemAccount=false
