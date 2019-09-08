WeeChat configuration
=====================

Official WeeChat documentation: https://weechat.org/doc

Base configuration
------------------

The configuration of WeeChat lies in ``~/.weechat``.

* Set IRC names and nicks by default::

      /set irc.server_default.username "My user name"
      /set irc.server_default.realname "My real name"
      /set irc.server_default.nicks "mynick,mynick2,mynick3,mynick4,mynick5"

* Add FreeNode IRC server::

      /server add freenode chat.freenode.net/7000
      /set irc.server.freenode.ssl on
      /set irc.server.freenode.autoconnect on
      /set irc.server.freenode.autojoin "#help"
      /connect freenode

      # To disconnect
      /disconnect freenode

      # In WeeChat core buffer, switch with server buffers
      Ctrl+x

* To remove an option: ``/unset irc.server.freenode.nicks``

* Basic IRC commands (from https://weechat.org/files/doc/stable/weechat_quickstart.en.html)::

      # Join an IRC channel
      /join #channel

      # /q is an alias for /query
      /q nick

      # Part an IRC channel
      /part [quit message]

      # /close is an alias for /buffer close
      /close

      # Emit /
      //

      # Bold text
      Ctrl+c b
      # Text color xx
      Ctrl+c c xx
      # Italic text
      Ctrl+c i
      # Underlined text
      Ctrl+c _

* Enable mouse::

      /set weechat.look.mouse on
      /mouse enable

* Log files in directories by date::

      # By default, the mask is "$plugin.$name.weechatlog"
      /set logger.file.mask "%Y/%m/$plugin.$name.weechatlog"

* Add a custom list of highlight patterns (cf. https://weechat.org/files/doc/stable/weechat_user.en.html#highlights)::

      /set weechat.look.highlight word1,word2,test*
      /set weechat.look.highlight_regex flashc[oö]de|flashy

      # It is also possible to highlight all messages matching a regular expression, in a buffer
      /buffer set highlight_regex needle.*

* After configuring WeeChat, run ``/save`` to save the configuration.


Security
--------

The official FAQ gives some settings for security-paranoid people: https://weechat.org/files/doc/stable/weechat_faq.en.html#security

::

    /set irc.server_default.msg_part ""
    /set irc.server_default.msg_quit ""
    /set irc.ctcp.clientinfo ""
    /set irc.ctcp.finger ""
    /set irc.ctcp.source ""
    /set irc.ctcp.time ""
    /set irc.ctcp.userinfo ""
    /set irc.ctcp.version ""
    /set irc.ctcp.ping ""
    /plugin unload xfer
    /set weechat.plugin.autoload "*,!xfer"

To change options related to IRC, ``/fset irc.*`` can help.

Then, it is possible to encrypt the credential for IRC servers using a master passphrase, using command ``/secure``::

    /secure passphrase xxxxxxxxxx
    /secure set freenode_username username
    /secure set freenode_password xxxxxxxx
    /set irc.server.freenode.sasl_username "${sec.data.freenode_username}"
    /set irc.server.freenode.sasl_password "${sec.data.freenode_password}"
    /set irc.server.freenode.sasl_mechanism PLAIN

    # Or, with NickServ (the connect commands can be separated by semi-colon)
    /set irc.server.freenode.command "/msg nickserv identify ${sec.data.freenode_password}"

The encrypted credentials will be kepts in ``~/.weechat/sec.conf``.

To display the encrypted data::

    /secure
    # ... this opens a new buffer
    Alt+v

Aliases
-------

Aliases are useful.
There are some examples on https://github.com/weechat/weechat/wiki/Alias-examples.
Here are others::

    # Messages to NickServ and ChanServ
    /alias add ns /query NickServ
    /alias add cs /query ChanServ

    # Add the current channel to the autojoin list
    /alias add addautojoin /eval /set irc.server.$server.autojoin ${irc.server.$server.autojoin},$channel

    # Manually join channels listed in server.autojoin
    /alias add mjoin /eval /join ${irc.server.${server}.autojoin}

    # Close window, focusing on the other one
    /alias add window_close /window swap; /window merge

Scripts
-------

WeeChat has a large library of scripts:

* https://weechat.org/scripts/
* https://github.com/weechat/scripts/

Here are some useful ones:

* ``highmon.pl`` (`WeeChat.org:highmon <https://weechat.org/scripts/source/highmon.pl.html/>`_, `GitHub:highmon <https://github.com/weechat/scripts/blob/master/perl/highmon.pl>`_):

  .. code-block:: sh

      wget -O ~/.weechat/perl/autoload/highmon.pl https://raw.githubusercontent.com/weechat/scripts/master/perl/highmon.pl
      # Then in WeeChat: /perl autoload

* ``buffer_autoset.py`` allows setting properties to buffer when they are opened, such as highlight (``/buffer_autoset add irc.freenode.#myinfra highlight_words_add CRIT``, instead of ``/buffer set ...``)
  (`WeeChat.org:buffer_autoset <https://weechat.org/scripts/source/stable/buffer_autoset.py/>`_, `GitHub:buffer_autoset <https://github.com/weechat/scripts/blob/master/python/buffer_autoset.py>`_):

  .. code-block:: sh

      wget -O ~/.weechat/python/autoload/buffer_autoset.py https://raw.githubusercontent.com/weechat/scripts/master/python/buffer_autoset.py
      # Then in WeeChat: /python autoload

WeeChat Relay
-------------

In order to use WeeChat on a phone or in a browser, a relay needs to be configured.
This is documented on https://weechat.org/files/doc/stable/weechat_user.en.html#relay_plugin.

* Create an SSL certificate for the relay:

  .. code-block:: sh

      mkdir -p ~/.weechat/ssl
      cd ~/.weechat/ssl
      openssl req -nodes -newkey rsa:2048 -keyout relay.pem -x509 -days 365 -out relay.pem

      # In WeeChat: /relay sslcertkey

* Configure which client is allowed to connect to the relay (here, for localhost or SSH port forwarding only)::

      /set relay.network.allowed_ips 127.0.0.1
      /set relay.network.bind_address 127.0.0.1
      /set relay.network.ipv6 off

* Configure a relay password and start it!

  ::

      /set relay.network.password "mypassword"
      /relay add ssl.weechat 9000
      # To remove a relay: /relay del weechat

* List the relays::

      /relay listrelay
