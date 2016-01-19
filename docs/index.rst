Welcome to SimplePlugin documentation!
======================================

SimplePlugin micro-framework simplifies creating content plugins for `Kodi mediacenter`_.
It was inspired by `xbmcswift2 micro-framework`_ for the same purpose
and has similar features like item lists containing dictionaries with item properties, persistent storage
and cache decorator for functions.

But unlike xbmcswift2 which uses decorator-based callback routing mechanism similar to Bottle or Flask web-frameworks,
SimplePlugin uses :doc:`Actions<./actions>` that are Python callable objects mapped to plugin call parameters.
A plugin based on SimplePlugin must have at least a ``'root'`` action which displays the plugin root virtual folder.
Other actions are called via "action" call parameter, e.g. the URL :file:`plugin://plugin.foo.bar/?action=foo`
will call a function mapped to ``'foo'`` string.

In addition to simplifying creation of content lists in Kodi interface,
SimplePlugin provides :doc:`Persistent Storage<./storage>` with dictionary-like interface
to store arbitrary parameters.

SimplePlugin also provides function :doc:`Cached Decorator<./cached>` similar to that of xbmcswift2 which allows
to cache function return data for a specified amount of time.

.. _Kodi mediacenter: http://www.kodi.tv
.. _xbmcswift2 micro-framework: https://github.com/jbeluch/xbmcswift2

**Contents:**

.. toctree::
    :maxdepth: 2

    example
    actions
    get_url
    storage
    cached
    settings
    using
    api
    links

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
