Cached Decorator
================

SimplePlugin provides :meth:`cached<simpleplugin.Addon.cached>` function decorator that caches
return data of a function for a specified amount of time in minutes. Example::

  @plugin.cached(30)
  def foo():
      # Do some stuff
      return bar

This will cache ``bar`` value for 30 minutes.

By providing a negative duration value to the decorator you can store function's return data forever
(or, more exactly, as long as the cache file :file:`cache.pcl` exists the plugin's profile folder).
