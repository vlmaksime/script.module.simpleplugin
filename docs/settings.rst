Working with Plugin Settings
============================

Plugin settings can be accessed using :meth:`get_setting<simpleplugin.Addon.get_setting>`
and :meth:`set_setting<simpleplugin.Addon.set_seting>` instance methods.

:meth:`get_setting<simpleplugin.Addon.get_setting>` method returns a :class:`Plugin<simpleplugin.Plugin>` setting
with a given ID. By default `get_setting()` converts ``'true'`` and `'false'` strings to Python ``True`` and ``False``
respectively.
Numeric strings are converted to Python :class:`long` or :class:`float` depending on their format,
i.e. ``'100'`` will be converted to ``100L`` and ``'3.14`'` to ``3.14``.
This behavior can be disabled by passing ``False`` as the 2-nd positional argument to get a raw setting string.

:meth:`set_setting<simpleplugin.Addon.set_seting>` stores a value in Plugin's setting under a given ID.
:meth:`set_setting<simpleplugin.Addon.set_seting>` accepts data of any type. Boolean ``True`` and ``False`` are
converted to ``'true'`` and ``'false'`` respectively. Other non-string/non-unicode data will be converted
to strings using Python :func:`str` function.

Plugin's settings can also be retrieved via a :class:`Plugin<simpleplugin.Plugin>` instance properties,
i.e. ``plugin.setting`` is equal to ``plugin.get_setting('setting')``.

..note:: It is not possible assign settings value to properties.
 To store a setting you need to use :meth:`set_setting<simpleplugin.Addon.set_seting>` method.

You can store any settings in Plugin's configuration, not only those that have visual controls
in the Plugin's "Settings" panel.
