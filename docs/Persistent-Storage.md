SimplePlugin provides persistent [Storage](http://romanvm.github.io/script.module.simpleplugin/docs/simpleplugin.Storage-class.html) with dictionary-like interface to store arbitrary data between plugin calls. A Storage instance supports most of Python `dict` methods and can hold any Python picklable objects. It also can be used as a context manager along with `with` statement. To create a Storage instance for the current plugin you need to call [get_storage()](http://romanvm.github.io/script.module.simpleplugin/docs/simpleplugin.Addon-class.html#get_storage) method for your Plugin instance, e.g.:
```python
with plugin.get_storage() as storage:  # Create a storage object
    storage['key1'] = value1  # Store data
    value2 = storage['key2']  # Retrieve data
...
```
After exiting the `with` block storage contents are saved to disk and the storage object is invalidated. To use the storage again you need to create a new Storage instance.

`get_storage()` methods takes an optional parameter which is the name of a storage file, so you can have several different storages in your plugin. Storage files are stored in the plugin's profile folder which is `special://profile/addon_data/<your.plugin.id>`.