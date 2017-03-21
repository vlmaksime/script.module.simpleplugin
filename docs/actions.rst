Actions
=======

In SimplePlugin **actions** are Python callable objects -- functions or methods -- that are called
when a SimplePlugin-based plugin is invoked in Kodi. "root" action is called when a user opens the plugin from Kodi UI,
e.g. from "Video Addons" or "Music Addons" section. Child actions are called via a plugin callback URL
containing "action" parameter in its paramstring, e.g. the :file:`plugin://plugin.video.foo/?action=bar`
URL will call the action mapped to "bar" action string.

Actions are defined using :meth:`action <simpleplugin.Plugin.action>` decorator.
The decorator takes an optional parameter which is the name of the action. If an explicit name
is not provided the action is named after the decorated function.

Example:

.. code-block:: python

  from simpleplugin import Plugin

  plugin = Plugin()

  @plugin.action()
  def root():
      # Do some things
      ...
      return listing

  @plugin.action()
  def foo(params):
      # Do other things
      ...
      return listing


  plugin.run()

The "root" action is mandatory, that is, a SimplePlugin-based plugin **must** have at least a "root" action.

.. warning::  Actions must have unique names!

An action callable may take an optional ``params`` parameter which is a :class:`Params <simpleplugin.Params>`
instance containing parsed plugin call parameters. Parameters can be accessed either by keys
as in a :class:`dict` or as instance properties, for example:

.. code-block:: python

  @plugin.action('foo')
  def action(params):
      foo = params['foo']  # Access by key
      bar = params.bar  # Access though property. Both variants are equal.

.. note:: Accessing a missing parameter by key will raise :exc:`KeyError`,
  but a property will return ``None`` if a parameter with such name is missing.

If an action does not use ``params`` parameter, it can be omitted.

Kodi supports 3 types of actions:

.. toctree::

  _actions/vf
  _actions/playback
  _actions/misc
