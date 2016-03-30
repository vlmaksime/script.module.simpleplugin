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

After exiting a :keyword:`with` block a Storage object is invalidated. To use the storage again you need to create a
new Storage instance. Storage contents are saved to disk only for a newly created storage or if the storage contents
have been changed. This reduces the number of write operations in cases when we need only to read stored data.

:meth:`get_storage<simpleplugin.Addon.get_storage>` method takes an optional parameter
which is the name of a storage file, so you can have several different storages in your plugin.
Storage files are stored in the plugin's profile folder which is :file:`special://profile/addon_data/{your.plugin.id}`.
