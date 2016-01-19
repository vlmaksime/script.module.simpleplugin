Persistent Storage
==================

SimplePlugin provides persistent :class:`Storage<simpleplugin.Storage>` with :class:`dict`-like interface
to store arbitrary data between plugin calls. A Storage instance supports most of Python :class:`dict` methods
and can hold any Python picklable objects. It also can be used as a context manager along with
:keyword:`with` statement. To create a Storage instance for the current plugin you need to call
:meth:`get_storage<simpleplugin.Addon.get_storage>` method for your Plugin instance, e.g.::

  with plugin.get_storage() as storage:  # Create a storage object
      storage['key1'] = value1  # Store data
      value2 = storage['key2']  # Retrieve data

After exiting the :keyword:`with` block storage contents are saved to disk and the storage object is invalidated.
To use the storage again you need to create a new Storage instance.

:meth:`get_storage<simpleplugin.Addon.get_storage>` method takes an optional parameter
which is the name of a storage file, so you can have several different storages in your plugin.
Storage files are stored in the plugin's profile folder which is :file:`special://profile/addon_data/{your.plugin.id}`.
