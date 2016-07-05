get_url Method
==============

:meth:`get_url<simpleplugin.Plugin.get_url>` convenience method helps you create callback URLs
for your virtual folder items. It takes a base plugin URL with trailing ``/`` and a set of ``param='value'``
parameter pairs that are then passed to the child action.
If a plugin URL is omitted then the current plugin URL is used.
In this case ``action`` parameter needs to be provided to define the necessary child action.

To illustrate the principle let's assume that our plugin's ID is ``plugin.video.foo``. Then the call::

  plugin.get_url(action='bar', param1='ham', param2='spam')

will return :file:`plugin://plugin.video.foo/?action=bar&param1=ham&param2=spam` URL.

Parameter values must be ASCII strings (Python :class:`str` objects).
Unicode characters needs to be encoded with :mod:`base64` encoding and then decoded back to Unicode in a child action.

You can also provide lists as parameters. In this case the call::

  plugin.get_url(action='bar', param=['ham', 'spam'])

will return :file:`plugin://plugin.video.foo/?action=bar&param=ham&param=spam` URL.

.. note:: :meth:`get_url<simpleplugin.Plugin.get_url>` without any parameters returns the plugin's root action URL.
