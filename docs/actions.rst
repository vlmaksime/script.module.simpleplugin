Actions
=======

In SimplePlugin **actions** are Python callable objects -- functions or methods -- that are called
when a SimplePlugin-based plugin is invoked in Kodi. "root" action is called when a user opens the plugin from Kodi UI,
e.g. from "Video Addons" or "Music Addons" section. Child actions are called via a plugin callback URL
containing "action" parameter in its paramstring, e.g. :file:`plugin://plugin.video.foo/?action=bar`
URL will call the action mapped to "bar" action string.

Actions are mapped to action strings via ``actions`` property of a Plugin class instance, e.g.::

  from simpleplugin import Plugin

  plugin = Plugin()

  def root(params):
      # Do some things
      ...
      return listing


  def foo(params):
      # Do some other things
      ...
      return listing


  plugin.actions['root'] = root  # Mandatory!
  plugin.actions['foo'] = foo
  plugin.run()

The "root" action is mandatory, i.e. a SimplePlugin based plugin **must** have at least a "root" action.

.. warning::  For mapping you need to use function objects without brackets ``()``!

``plugin.actions['foo'] = foo`` -- Correct :-)

``plugin.actions['foo'] = foo()`` -- **Wrong!!!** :-(

An action callable automatically receives ``params`` parameter which is a Python :class:`dict`
containing a parsed plugin callback URL paramstring, e.g. for URL
:file:`plugin://plugin.video.foo/?action=bar&param=baz` ``params`` parameter will be
``{'action': 'bar', 'param': 'baz'}``. For "root" action ``params`` will be an empty :class:`dict` ``{}``.

.. note:: An action always receives ``params`` parameter even it does not use it.
    If ``params`` is missing from an action signature, a plugin will raise an exception.

Kodi supports 3 types of actions:

.. toctree::

  _actions/vf
  _actions/playback
  _actions/misc
