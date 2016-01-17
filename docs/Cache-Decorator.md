SimplePlugin provides [cached](http://romanvm.github.io/script.module.simpleplugin/docs/simpleplugin.Addon-class.html#cached) function decorator which allows to cache function's return data for a specified amount of time in minutes. Example:
```python
@plugin.cached(30)
def foo()
    # Do some stuff
    return bar
````
This will cache `bar` value for 30 minutes.

By providing a negative duration value to the decorator you can store function's return data forever (or, more exactly, as long as the cache file `cache.pcl` exists the plugin's profile folder).