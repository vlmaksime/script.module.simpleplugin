Logging
=======

The :class:`Addon <simpleplugin.Addon>` class provides 4 methods for simplified logging:
:meth:`log_notice <simpleplugin.Addon.log_notice>`, :meth:`log_warning <simpleplugin.Addon.log_warning>`,
:meth:`log_error <simpleplugin.Addon.log_error>` and :meth:`log_debug <simpleplugin.Addon.log_debug>`.
Those methods write messages to the Kodi log with the respective levels. The messages include
the addon ID to help distinguish messages belonging to the current addon. All methods accept
both :class:`str` and :obj:`unicode` strings.
