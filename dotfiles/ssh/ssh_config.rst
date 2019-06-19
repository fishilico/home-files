$HOME/.ssh/config configuration
===============================

Here is an example of .ssh/config file::

    # Mitigate CVE-2016-0778
    # https://lists.archlinux.org/pipermail/arch-security/2016-January/000512.html
    Host *
        UseRoaming no

    # Configure a server with a specific SSH key and SSHFP DNS records
    # (to generate these records, use "ssh-keygen -r $(hostname)" on the server)
    Host myserver
        HostName myserver.example.org
        User myuser
        IdentityFile ~/.ssh/id_ed25519_mykey
        PasswordAuthentication no
        VerifyHostKeyDNS yes
        ForwardX11 no


Using a single connection
-------------------------

When opening several connections to a SSH server (e.g. for remote shell, file
copy, tunneling, etc.), it is possible to speed up the start-up time by using
several channels of a single connection. A quick way to perform with is by adding
the following lines in the Host session::

    ControlMaster auto
    ControlPath ~/.ssh/control:%h:%p:%r
