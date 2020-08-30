Cached Decorator
================

SimplePlugin provides :meth:`cached <simpleplugin.Addon.cached>` and
:meth:`mem_cached <simpleplugin.Addon.mem_cached>` function decorators that
cache return value of a function for a specified amount of time in minutes.
Example::

  @plugin.cached(30)
  def foo(param):
      # Do some stuff
      return bar

Here the ``bar`` value will be cached for 30 minutes.

The :meth:`mem_cached <simpleplugin.Addon.mem_cached>` decorator caches data
in memory so the cache lasts as long as Kodi runs,
while :meth:`cached <simpleplugin.Addon.cached>` caches data to disk.

The caching decorators can be used, for example, to cache data received from a remote web-site or API,
thus reducing the number of requests issued from your addon to that site or API.

.. note:: Caching is based on Python object :mod:`pickling<pickle>`
  so only only picklable return values can be cached.
  For example, generator functions (with :keyword:`yield` statement)
  are not picklable so they cannot be cached.
