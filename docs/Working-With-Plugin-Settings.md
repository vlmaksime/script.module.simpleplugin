Plugin settings can be accessed using [get_setting()](http://romanvm.github.io/script.module.simpleplugin/docs/simpleplugin.Addon-class.html#get_setting) and [set_setting()](http://romanvm.github.io/script.module.simpleplugin/docs/simpleplugin.Addon-class.html#set_setting) instance methods.

`get_setting(id_)` method returns a Plugin setting with a given ID. By default `get_setting()` converts `'true'` and `'false'` strings to Python `True` and `False` respectively. Numeric strings are converted to Python `long` or `float` depending on their format, i.e. `'100'` will be converted to `100L` and `'3.14'` to `3.14`. This behavior can be disabled by passing `False` as the 2-nd positional argument to get a raw setting string.

`set_setting(id_, value)` stores a value in Plugin's setting under a given ID. `set_settings` accepts data of any type. Boolean `True` and `False` will be converted to `'true'` and `'false'` respectively. Other non-string/non-unicode data will be converted to strings using Python `str()` function.

Plugin's settings can also be retrieved via a Plugin instance properties, i.e. `plugin.setting` is equal to `plugin.get_setting('setting')`. Note that you cannot assign settings value to properties. To store a setting you need to use `set_setting()` method.

You can store any settings in Plugin's configuration, not only those that have visual controls in the Plugin's "Settings" panel.