Plugin Localization
===================

Kodi has its own specific `localization system`_ that is also used for addons. This system uses numeric codes for
extracting respective localized :abbr:`GUI (Graphical User Interface)` strings from addon localization :file:`.po`
files using :meth:`getLocalizedString<xbmcaddon.Addon.getLocalizedString>` method. For example::

  import xbmcaddon
  import xbmcgui

  addon = xbmcaddon.Addon()
  xbmcgui.Dialog().ok(addon.getLocalizedString(32000), addon.getLocalizedString(32001))

As you can see, this is neither intuitive nor convenient and may lead to errors. To improve code readability the
**SimplePlugin** library can emulate a popular `GNU Gettext`_ localization system that is also standard for Python
programs. This emulation layer is implemented through
:class:`initialize_gettext()<simpleplugin.Addon.initialize_gettext>` and
:class:`gettext()<simpleplugin.Addon.gettext>` methods that allow to access localized addon GUI strings using
English source strings instead of numeric codes. For example::

  import xbmcgui
  from simpleplugin import Plugin

  plugin = Plugin()
  _ = plugin.initialize_gettext()

  xbmcgui.Dialog().ok(_('Hello World!'), _('This is sample text.'))

The :class:`initialize_gettext()<simpleplugin.Addon.initialize_gettext>` method returns
:class:`gettext<simpleplugin.Addon.gettext>` method object that is used to extract localized GUI stirngs.
The name of this method (or function) object can be any but traditionally it is named with a single underscore ``_`` to
reduce typing. In the preceding example you can clearly see which strings or their localized versions are used in
addon/plugin GUI elements and this code is much more readable than in the first example.

.. warning:: To use the Gettext emulation you need to call
  :class:`initialize_gettext()<simpleplugin.Addon.initialize_gettext>` method first.
  All GUI strings obtained using the emulation feature must be present at least in English :file:`strings.po`
  file. Attempting to access a missing string will result in :exc:`simpleplugin.SimplePluginError` exception.

.. _localization system: http://kodi.wiki/view/Language_support
.. _GNU Gettext: https://www.gnu.org/software/gettext
