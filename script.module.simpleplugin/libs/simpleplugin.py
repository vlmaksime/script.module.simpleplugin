# -*- coding: utf-8 -*-
# Created on: 03.06.2015
"""
SimplePlugin micro-framework for Kodi content plugins

**Author**: Roman Miroshnychenko aka Roman V.M.

**License**: `GPL v.3 <https://www.gnu.org/copyleft/gpl.html>`_
"""

import os
import sys
import re
from datetime import datetime, timedelta
import cPickle as pickle
from urlparse import urlparse, parse_qs
from urllib import urlencode, quote_plus, unquote_plus
from functools import wraps
from collections import MutableMapping, namedtuple
from copy import deepcopy
from types import GeneratorType
from hashlib import md5
import xbmcaddon
import xbmc
import xbmcplugin
import xbmcgui

__all__ = ['SimplePluginError', 'Storage', 'Addon', 'Plugin']

Route = namedtuple('Route', ['pattern', 'func'])
ListContext = namedtuple('ListContext', ['listing', 'succeeded', 'update_listing', 'cache_to_disk',
                                         'sort_methods', 'view_mode', 'content'])
PlayContext = namedtuple('PlayContext', ['path', 'play_item', 'succeeded'])


class SimplePluginError(Exception):
    """Custom exception"""
    pass


class Storage(MutableMapping):
    """
    Persistent storage for arbitrary data with a dictionary-like interface

    It is designed as a context manager and better be used
    with 'with' statement.

    :param storage_dir: directory for storage
    :type storage_dir: str
    :param filename: the name of a storage file (optional)
    :type filename: str

    Usage::

        with Storage('/foo/bar/storage/') as storage:
            storage['key1'] = value1
            value2 = storage['key2']

    .. note:: After exiting :keyword:`with` block a :class:`Storage` instance is invalidated.
        Storage contents are saved to disk only for a new storage or if the contents have been changed.
    """
    def __init__(self, storage_dir, filename='storage.pcl'):
        """
        Class constructor
        """
        self._storage = {}
        self._hash = None
        self._filename = os.path.join(storage_dir, filename)
        try:
            with open(self._filename, 'rb') as fo:
                contents = fo.read()
            self._storage = pickle.loads(contents)
            self._hash = md5(contents).hexdigest()
        except (IOError, pickle.PickleError, EOFError):
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()

    def __getitem__(self, key):
        return self._storage[key]

    def __setitem__(self, key, value):
        self._storage[key] = value

    def __delitem__(self, key):
        del self._storage[key]

    def __iter__(self):
        return self._storage.__iter__()

    def __len__(self):
        return len(self._storage)

    def __str__(self):
        return '<Storage {0}>'.format(self._storage)

    def __repr__(self):
        return '<simpleplugin.Storage object {0}>'.format(self._storage)

    def flush(self):
        """
        Save storage contents to disk

        This method saves new and changed :class:`Storage` contents to disk
        and invalidates the Storage instance. Unchanged Storage is not saved
        but simply invalidated.
        """
        contents = pickle.dumps(self._storage)
        if self._hash is None or md5(contents).hexdigest() != self._hash:
            with open(self._filename, 'wb') as fo:
                fo.write(contents)
        del self._storage

    def copy(self):
        """
        Make a copy of storage contents

        .. note:: this method performs a *deep* copy operation.

        :return: a copy of storage contents
        :rtype: dict
        """
        return deepcopy(self._storage)


class Addon(object):
    """
    Base addon class

    Provides access to basic addon parameters

    :param id_: addon id, e.g. 'plugin.video.foo' (optional)
    :type id_: str
    """
    def __init__(self, id_=''):
        """
        Class constructor
        """
        self._addon = xbmcaddon.Addon(id_)
        self._configdir = xbmc.translatePath(self._addon.getAddonInfo('profile')).decode('utf-8')
        self._ui_strings_map = None
        if not os.path.exists(self._configdir):
            os.mkdir(self._configdir)

    def __getattr__(self, item):
        """
        Get addon setting as an Addon instance attribute

        E.g. addon.my_setting is equal to addon.get_setting('my_setting')

        :param item:
        :type item: str
        """
        return self.get_setting(item)

    def __str__(self):
        return '<Addon [{0}]>'.format(self.id)

    def __repr__(self):
        return '<simpleplugin.Addon object [{0}]>'.format(self.id)

    @property
    def addon(self):
        """
        Kodi Addon instance that represents this Addon

        :return: Addon instance
        :rtype: xbmcaddon.Addon
        """
        return self._addon

    @property
    def id(self):
        """
        Addon ID

        :return: Addon ID, e.g. 'plugin.video.foo'
        :rtype: str
        """
        return self._addon.getAddonInfo('id')

    @property
    def path(self):
        """
        Addon path

        :return: path to the addon folder
        :rtype: str
        """
        return self._addon.getAddonInfo('path').decode('utf-8')

    @property
    def icon(self):
        """
        Addon icon

        :return: path to the addon icon image
        :rtype: str
        """
        icon = os.path.join(self.path, 'icon.png')
        if os.path.exists(icon):
            return icon
        else:
            return ''

    @property
    def fanart(self):
        """
        Addon fanart

        :return: path to the addon fanart image
        :rtype: str
        """
        fanart = os.path.join(self.path, 'fanart.jpg')
        if os.path.exists(fanart):
            return fanart
        else:
            return ''

    @property
    def config_dir(self):
        """
        Addon config dir

        :return: path to the addon config dir
        :rtype: str
        """
        return self._configdir

    def get_localized_string(self, id_):
        """
        Get localized UI string

        :param id_: UI string ID
        :type id_: int
        :return: UI string in the current language
        :rtype: unicode
        """
        return self._addon.getLocalizedString(id_).encode('utf-8')

    def get_setting(self, id_, convert=True):
        """
        Get addon setting

        If ``convert=True``, 'bool' settings are converted to Python :class:`bool` values,
        and numeric strings to Python :class:`long` or :class:`float` depending on their format.

        .. note:: Settings can also be read via :class:`Addon` instance poperties named as the respective settings.
            I.e. ``addon.foo`` is equal to ``addon.get_setting('foo')``.

        :param id_: setting ID
        :type id_: str
        :param convert: try to guess and convert the setting to an appropriate type
            E.g. ``'1.0'`` will be converted to float ``1.0`` number, ``'true'`` to ``True`` and so on.
        :type convert: bool
        :return: setting value
        """
        setting = self._addon.getSetting(id_)
        if convert:
            if setting == 'true':
                return True  # Convert boolean strings to bool
            elif setting == 'false':
                return False
            elif re.search(r'^\-?\d+$', setting) is not None:
                return long(setting)  # Convert numeric strings to long
            elif re.search(r'^\-?\d+\.\d+$', setting) is not None:
                return float(setting)  # Convert numeric strings with a dot to float
        return setting

    def set_setting(self, id_, value):
        """
        Set addon setting

        Python :class:`bool` type are converted to ``'true'`` or ``'false'``
        Non-string/non-unicode values are converted to strings.

        .. warning:: Setting values via :class:`Addon` instance properties is not supported!
            Values can only be set using :meth:`Addon.set_setting` method.

        :param id_: setting ID
        :type id_: str
        :param value: setting value
        """
        if isinstance(value, bool):
            value = 'true' if value else 'false'
        elif not isinstance(value, basestring):
            value = str(value)
        self._addon.setSetting(id_, value)

    def log(self, message, level=0):
        """
        Add message to Kodi log starting with Addon ID

        :param message: message to be written into the Kodi log
        :type message: str
        :param level: log level. :mod:`xbmc` module provides the necessary symbolic constants.
            Default: ``xbmc.LOGDEBUG``
        :type level: int
        """
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        xbmc.log('{0}: {1}'.format(self.id, message), level)

    def log_notice(self, message):
        """
        Add NOTICE message to the Kodi log

        :param message: message to write to the Kodi log
        :type message: str
        """
        self.log(message, xbmc.LOGINFO)

    def log_warning(self, message):
        """
        Add WARNING message to the Kodi log

        :param message: message to write to the Kodi log
        :type message: str
        """
        self.log(message, xbmc.LOGWARNING)

    def log_error(self, message):
        """
        Add ERROR message to the Kodi log

        :param message: message to write to the Kodi log
        :type message: str
        """
        self.log(message, xbmc.LOGERROR)

    def log_debug(self, message):
        """
        Add debug message to the Kodi log

        :param message: message to write to the Kodi log
        :type message: str
        """
        self.log(message, xbmc.LOGDEBUG)

    def get_storage(self, filename='storage.pcl'):
        """
        Get a persistent :class:`Storage` instance for storing arbitrary values between addon calls.

        A :class:`Storage` instance can be used as a context manager.

        Example::

            with plugin.get_storage() as storage:
                storage['param1'] = value1
                value2 = storage['param2']

        .. note:: After exiting :keyword:`with` block a :class:`Storage` instance is invalidated.

        :param filename: the name of a storage file (optional)
        :type filename: str
        :return: Storage object
        :rtype: Storage
        """
        return Storage(self.config_dir, filename)

    def cached(self, duration=10):
        """
        Cached decorator

        Used to cache function return data

        Usage::

            @plugin.cached(30)
            def my_func(*args, **kwargs):
                # Do some stuff
                return value

        :param duration: cache time in min, negative value -- cache indefinitely
        :type duration: int
        """
        def outer_wrapper(func):
            @wraps(func)
            def inner_wrapper(*args, **kwargs):
                with self.get_storage('__cache__.pcl') as cache:
                    current_time = datetime.now()
                    key = func.__name__ + str(args) + str(kwargs)
                    try:
                        data, timestamp = cache[key]
                        if duration > 0 and current_time - timestamp > timedelta(minutes=duration):
                            raise KeyError
                        self.log_debug('Cache hit: {0}'.format(key))
                    except KeyError:
                        self.log_debug('Cache miss: {0}'.format(key))
                        data = func(*args, **kwargs)
                        cache[key] = (data, current_time)
                return data
            return inner_wrapper
        return outer_wrapper

    def gettext(self, ui_string):
        """
        Get a translated UI string from addon localization files.

        This function emulates GNU Gettext for more convenient access
        to localized addon UI strings. To reduce typing this method object
        can be assigned to a ``_`` (single underscore) variable.

        For using gettext emulation :meth:`Addon.initialize_gettext` method
        needs to be called first. See documentation for that method for more info
        about Gettext emulation.

        :param ui_string: a UI string from English :file:`strings.po`.
        :type ui_string: str
        :return: a UI string from translated :file:`strings.po`.
        :rtype: unicode
        :raises simpleplugin.SimplePluginError: if :meth:`Addon.initialize_gettext` wasn't called first
            or if a string is not found in English :file:`strings.po`.
        """
        if self._ui_strings_map is not None:
            try:
                return self.get_localized_string(self._ui_strings_map['strings'][ui_string])
            except KeyError:
                raise SimplePluginError('UI string "{0}" is not found in strings.po!'.format(ui_string))
        else:
            raise SimplePluginError('Addon localization is not initialized!')

    def initialize_gettext(self):
        """
        Initialize GNU gettext emulation in addon

        Kodi localization system for addons is not very convenient
        because you need to operate with numeric string codes instead
        of UI strings themselves which reduces code readability and
        may lead to errors. The :class:`Addon` class provides facilities
        for emulating GNU Gettext localization system.

        This allows to use UI strings from addon's English :file:`strings.po`
        file instead of numeric codes to return localized strings from
        respective localized :file:`.po` files.

        This method returns :meth:`Addon.gettext` method object that
        can be assigned to a short alias to reduce typing. Traditionally,
        ``_`` (a single underscore) is used for this purpose.

        Example::

            addon = simpleplugin.Addon()
            _ = addon.initialize_gettext()

            xbmcgui.Dialog().notification(_('Warning!'), _('Something happened'))

        In the preceding example the notification strings will be replaced
        with localized versions if these strings are translated.

        :return: :meth:`Addon.gettext` method object
        :raises simpleplugin.SimplePluginError: if the addon's English :file:`strings.po` file is missing
        """
        strings_po = os.path.join(self.path, 'resources', 'language', 'English', 'strings.po')
        if os.path.exists(strings_po):
            with open(strings_po, 'rb') as fo:
                raw_strings = fo.read()
            raw_strings_hash = md5(raw_strings).hexdigest()
            gettext_pcl = '__gettext__.pcl'
            with self.get_storage(gettext_pcl) as ui_strings_map:
                if (not os.path.exists(os.path.join(self._configdir, gettext_pcl)) or
                        raw_strings_hash != ui_strings_map['hash']):
                    ui_strings = self._parse_po(raw_strings.split('\n'))
                    self._ui_strings_map = {
                        'hash': raw_strings_hash,
                        'strings': ui_strings
                    }
                    ui_strings_map['hash'] = raw_strings_hash
                    ui_strings_map['strings'] = ui_strings.copy()
                else:
                    self._ui_strings_map = deepcopy(ui_strings_map)
        else:
            raise SimplePluginError('Unable to initialize localization because of missing English strings.po!')
        return self.gettext

    def _parse_po(self, strings):
        """
        Parses ``strings.po`` file into a dict of {'string': id} items.
        """
        ui_strings = {}
        string_id = None
        for string in strings:
            if string_id is None and 'msgctxt' in string:
                string_id = int(re.search(r'"#(\d+)"', string).group(1))
            elif string_id is not None and 'msgid' in string:
                ui_strings[re.search(r'"(.*?)"', string, re.U).group(1)] = string_id
                string_id = None
        return ui_strings


class Plugin(Addon):
    """
    Plugin class

    :param id_: plugin's id, e.g. 'plugin.video.foo' (optional)
    :type id_: str

    This class provides a simplified API to create virtual directories of playable items
    for Kodi content plugins.
    :class:`simpleplugin.Plugin` uses a concept of callable plugin actions (functions or methods)
    that are mapped to 'action' parameters via actions instance property.
    A Plugin instance must have at least one action for its root section
    mapped to 'root' string.

    Minimal example::

        from simpleplugin import Plugin

        plugin = Plugin()

        def root_action(params):
            return [{'label': 'Foo',
                    'url': plugin.get_url(action='some_action', param='Foo')},
                    {'label': 'Bar',
                    'url': plugin.get_url(action='some_action', param='Bar')}]

        def some_action(params):
            return [{'label': params['param']}]

        plugin.actions['root'] = root_action  # Mandatory item!
        plugin.actions['some_action'] = some_action
        plugin.run()

    .. warning:: You need to map function or method objects without round brackets!

    E.g.::

        plugin.actions['some_action'] = some_action  # Correct :)
        plugin.actions['some_action'] = some_action()  # Wrong! :(

    An action callable receives 1 parameter -- params.
    params is a dict containing plugin call parameters (including action string)
    The action callable can return
    either a list/generator of dictionaries representing Kodi virtual directory items
    or a resolved playable path (:class:`str` or :obj:`unicode`) for Kodi to play.

    Example 1::

        def list_action(params):
            listing = get_listing(params)  # Some external function to create listing
            return listing

    The ``listing`` variable is a Python list/generator of dict items.
    Example 2::

        def play_action(params):
            path = get_path(params)  # Some external function to get a playable path
            return path

    Each dict item can contain the following properties:

    - label -- item's label (default: ``''``).
    - label2 -- item's label2 (default: ``''``).
    - thumb -- item's thumbnail (default: ``''``).
    - icon -- item's icon (default: ``''``).
    - path -- item's path (default: ``''``).
    - fanart -- item's fanart (optional).
    - art -- a dict containing all item's graphic (see :meth:`xbmcgui.ListItem.setArt` for more info) -- optional.
    - stream_info -- a dictionary of ``{stream_type: {param: value}}`` items
      (see :meth:`xbmcgui.ListItem.addStreamInfo`) -- optional.
    - info --  a dictionary of ``{media: {param: value}}`` items
      (see :meth:`xbmcgui.ListItem.setInfo`) -- optional
    - context_menu - a list that contains 2-item tuples ``('Menu label', 'Action')``.
      The items from the tuples are added to the item's context menu.
    - url -- a callback URL for this list item.
    - is_playable -- if ``True``, then this item is playable and must return a playable path or
     be resolved via :meth:`Plugin.resolve_url` (default: ``False``).
    - is_folder -- if ``True`` then the item will open a lower-level sub-listing. if ``False``,
      the item either is a playable media or a general-purpose script
      which neither creates a virtual folder nor points to a playable media (default: C{True}).
      if ``'is_playable'`` is set to ``True``, then ``'is_folder'`` value automatically assumed to be ``False``.
    - subtitles -- the list of paths to subtitle files (optional).
    - mime -- item's mime type (optional).
    - list_item -- an 'class:`xbmcgui.ListItem` instance (optional).
      It is used when you want to set all list item properties by yourself.
      If ``'list_item'`` property is present, all other properties,
      except for ``'url'`` and ``'is_folder'``, are ignored.
    - properties -- a dictionary of list item properties
      (see :meth:`xbmcgui.ListItem.setProperty`) -- optional.

    Example::

        listing = [{    'label': 'Label',
                        'label2': 'Label 2',
                        'thumb': 'thumb.png',
                        'icon': 'icon.png',
                        'fanart': 'fanart.jpg',
                        'art': {'clearart': 'clearart.png'},
                        'stream_info': {'video': {'codec': 'h264', 'duration': 1200},
                                        'audio': {'codec': 'ac3', 'language': 'en'}},
                        'info': {'video': {'genre': 'Comedy', 'year': 2005}},
                        'context_menu': [('Menu Item', 'Action')],
                        'url': 'plugin:/plugin.video.test/?action=play',
                        'is_playable': True,
                        'is_folder': False,
                        'subtitles': ['/path/to/subtitles.en.srt', '/path/to/subtitles.uk.srt'],
                        'mime': 'video/mp4'
                        }]

    Alternatively, an action callable can use :meth:`Plugin.create_listing` and :meth:`Plugin.resolve_url`
    static methods to pass additional parameters to Kodi.

    Example 3::

        def list_action(params):
            listing = get_listing(params)  # Some external function to create listing
            return Plugin.create_listing(listing, sort_methods=(2, 10, 17), view_mode=500)

    Example 4::

        def play_action(params):
            path = get_path(params)  # Some external function to get a playable path
            return Plugin.resolve_url(path, succeeded=True)

    If an action callable performs any actions other than creating a listing or
    resolving a playable URL, it must return ``None``.
    """
    def __init__(self, id_=''):
        """
        Class constructor
        """
        super(Plugin, self).__init__(id_)
        self._url = 'plugin://{0}/'.format(self.id)
        self._handle = None
        self.actions = {}
        self._routes = {}
        self._params = None
        self.log_debug('{0} called'.format(self))

    def __str__(self):
        return '<Plugin {0}>'.format(sys.argv)

    def __repr__(self):
        return '<simpleplugin.Plugin object {0}>'.format(sys.argv)

    @property
    def params(self):
        """
        Get parsed plugin paramstring as a :class:`dict`

        .. note:: It will return ``None`` if :meth:`Plugin.run` has not been called yet.

        :return: parsed paramstring
        :rtype: dict
        """
        return self._params

    @staticmethod
    def get_params(paramstring):
        """
        Convert a URL-encoded paramstring to a Python dict

        :param paramstring: URL-encoded paramstring
        :type paramstring: str
        :return: parsed paramstring
        :rtype: dict
        """
        params = parse_qs(paramstring)
        for key, value in params.iteritems():
            params[key] = value[0] if len(value) == 1 else value
        return params

    def get_url(self, plugin_url='', **kwargs):
        """
        Construct a callable URL for a virtual directory item

        If plugin_url is empty, a current plugin URL is used.
        kwargs are converted to a URL-encoded string of plugin call parameters
        To call a plugin action, 'action' parameter must be used,
        if 'action' parameter is missing, then the plugin root action is called
        If the action is not added to :class:`Plugin` actions, :class:`PluginError` will be raised.

        :param plugin_url: plugin URL with trailing / (optional)
        :type plugin_url: str
        :param kwargs: pairs of key=value items
        :return: a full plugin callback URL
        :rtype: str
        """
        url = plugin_url or self._url
        if kwargs:
            return '{0}?{1}'.format(url, urlencode(kwargs, doseq=True))
        return url

    def url_for(self, name_, *args, **kwargs):
        """
        Build a URL for a plugin route

        This method reverse-builds an URL for the named route. If a route has no explicit name, then
        the name of the decorated function is used as route's name.

        The method can optionally take positional args and kwargs.
        If any positional args are provided their values replace variable placeholders by position.

        .. warning:: The number of positional args must not exceed the number of variable placeholders!

        If any kwargs are provided their values replace variable placeholders by name.
        If the number of kwargs provided exceeds the number of variable placeholders,
        then the rest of the kwargs are added to the URL as a query string.

        Example: let's assume that we have a plugin ``plugin.acme`` with the following route::

            @plugin.route('/foo/<bar>/')
            def foo(bar):
                pass

        In this case the call ``plugin.url_for('foo', bar='Python', ham='spam')`` will produce the URL:
        ``'plugin://plugin.acme/foo/Python/?ham=spam'``.

        :param name_: route's name.
        :type name_: str
        :return: full plugin callback URL for the route.
        :rtype: str
        :raises simpleplugin.SimplePluginError: if a route with such name does not exist
            or on arguments mismatch.
        """
        try:
            pattern = self._routes[name_].pattern
        except KeyError:
            raise SimplePluginError('There is no route with such name: "{0}"!'.format(name_))
        matches = re.findall(r'/(<.+?>)', pattern)
        if len(args) + len(kwargs) < len(matches):
            raise SimplePluginError('The number of arguments is less than the number of placeholders!')
        if matches:
            for arg, match in zip(args, matches):
                pattern = pattern.replace(match, quote_plus(str(arg)))
            for key, value in kwargs.items():
                for match in matches[len(args):]:
                    if key in match:
                        pattern = pattern.replace(match, quote_plus(str(value)))
                        del kwargs[key]
        url = 'plugin://{0}{1}'.format(self.id, pattern)
        if kwargs:
            url += '?' + urlencode(kwargs, doseq=True)
        return url

    def route(self, pattern, name=None):
        """
        Route decorator for plugin callback routes

        The route decorator is used to define plugin callback routes
        similar to a URL routing mechanism in Flask and Bottle Python web-frameworks.

        The plugin routing mechanism calls decorated functions by matching a path
        in a plugin callback URL (passed as ``sys.argv[0]``) to a route pattern.

        .. note:: A route pattern *must* start with a forward slash ``/``.
            An end slash is optional. A plugin must include
            at least the root route with ``'/'`` pattern.

        Example 1::

            @plugin.route('/foo')
            def foo_function():
                # Do something

        In the preceding example ``foo_function`` will be called when the plugin is invoked
        with ``plugin://plugin.acme/foo`` callback URL.

        A route pattern can contain variable placeholders (marked with angular brackets ``<>``)
        that are used to pass arguments to a route function.

        Example 2::

            @plugin.route('/foo/<param>')
            def foo_function(param):
                # Do something

        In the preceding example the part of a callback path marked with ``<param>`` placeholder
        will be passed to the function as an argument. The name of a placeholder must be the same
        as the name of the corresponding parameter. By default arguments are passed as strings.
        The ``int`` and ``float`` prefixes can be used to pass arguments
        as :class:`int` and :class:`float` numbers, for example ``<int:foo>`` or ``<float:bar>``.

        Example 3::

            @plugin.route('/add/<int:param1>/<int:param2>')
            def addition(param1, param2):
                sum = param1 + param2

        A function can have multiple route decorators. In this case additional routes
        must have explicitly defined names. If a route has less variable placeholders
        than function parameters, "missing" function parameters must have default values.

        Example 4::

            @plugin.route('/foo/<param>', name='foo_route')
            @plugin.route('/bar')
            def some_function(param='spam'):
                # Do something

        In the preceding example ``some_function`` can be called through 2 possible routes.
        If the function is called through the 1st route (``'foo_route'``)
        ``<param>`` value will be passed as an argument. The 2nd route will call the function
        with the default argument ``'spam'`` because this route has no variable placeholders
        to pass arguments to the function.

        :param pattern: route matching pattern
        :type pattern: str
        :param name: route's name (optional). If no name is provided,
            the route is named after the decorated function.
            The name must be unique.
        :type name: str
        """
        def wrap(func, pattern=pattern, name=name):
            if name is None:
                name = func.__name__
            if name in self._routes:
                raise SimplePluginError('The route with the name "{0}" already exists!'.format(name))
            if not pattern.endswith('/'):
                pattern += '/'
            pattern = pattern.replace('int:', 'int__').replace('float:', 'float__')
            self._routes[name] = Route(pattern, func)
            return func
        return wrap

    def run(self, category=''):
        """
        Run plugin

        :param category: str - plugin sub-category, e.g. 'Comedy'.
            See :func:`xbmcplugin.setPluginCategory` for more info.
        :type category: str
        """
        self._handle = int(sys.argv[1])
        if category:
            xbmcplugin.setPluginCategory(self._handle, category)
        self._params = self.get_params(sys.argv[2][1:])
        if self.actions:
            result = self._resolve_action()
        else:
            result = self._resolve_route()
        self.log_debug('Function return value: {0}'.format(str(result)))
        if isinstance(result, (list, GeneratorType)):
            self._add_directory_items(self.create_listing(result))
        elif isinstance(result, basestring):
            self._set_resolved_url(self.resolve_url(result))
        elif isinstance(result, tuple) and hasattr(result, 'listing'):
            self._add_directory_items(result)
        elif isinstance(result, tuple) and hasattr(result, 'path'):
            self._set_resolved_url(result)
        else:
            self.log_warning('The function has not returned any valid data to process.')

    def _resolve_action(self):
        """
        Resolve action from plugin call params and call the respective callable function

        :return: action callable's return value
        """
        self.log_warning('Routing via plugin actions is depreciated. Use plugin.route decorator instead.')
        action = self._params.get('action', 'root')
        self.log_debug('Actions: {0}'.format(str(self.actions.keys())))
        self.log_debug('Call action "{0}" with params "{1}"'.format(action, str(self._params)))
        try:
            return self.actions[action](self.params)
        except KeyError:
            raise SimplePluginError('Invalid action: "{0}"!'.format(action))

    def _resolve_route(self):
        """
        Resolve route from plugin callback path and call the respective route function

        :return: route function's return value
        """
        path = urlparse(sys.argv[0]).path
        self.log_debug('Routes: {0}'.format(self._routes))
        for route in self._routes.itervalues():
            pattern = route.pattern
            while True:
                pattern, count = re.subn(r'/(<.+?>)/', r'/(?P\1.+?)/', pattern)
                if not count:
                    break
            match = re.search(pattern, path)
            if match is not None:
                kwargs = match.groupdict()
                for key, value in kwargs.items():
                    if key.startswith('int__') or key.startswith('float__'):
                        del kwargs[key]
                        if key.startswith('int__'):
                            key = key.lstrip('int__')
                            value = int(value)
                        else:
                            key = key.lstrip('float__')
                            value = float(value)
                        kwargs[key] = value
                    else:
                        kwargs[key] = unquote_plus(value)
                self.log_debug('Calling route {0} with kwargs {1}'.format(route, kwargs))
                return route.func(**kwargs)
        raise SimplePluginError('No route matches the path {0}!'.format(repr(path)))

    @staticmethod
    def create_listing(listing, succeeded=True, update_listing=False, cache_to_disk=False, sort_methods=None,
                       view_mode=None, content=None):
        """
        Create and return a context dict for a virtual folder listing

        :param listing: the list of the plugin virtual folder items
        :type listing: :class:`list` or :class:`types.GeneratorType`
        :param succeeded: if ``False`` Kodi won't open a new listing and stays on the current level.
        :type succeeded: bool
        :param update_listing: if ``True``, Kodi won't open a sub-listing but refresh the current one.
        :type update_listing: bool
        :param cache_to_disk: cache this view to disk.
        :type cache_to_disk: bool
        :param sort_methods: the list of integer constants representing virtual folder sort methods.
        :type sort_methods: tuple
        :param view_mode: a numeric code for a skin view mode.
            View mode codes are different in different skins except for ``50`` (basic listing).
        :type view_mode: int
        :param content: string - current plugin content, e.g. 'movies' or 'episodes'.
            See :func:`xbmcplugin.setContent` for more info.
        :type content: str
        :return: context object containing necessary parameters
            to create virtual folder listing in Kodi UI.
        :rtype: ListContext
        """
        return ListContext(listing, succeeded, update_listing, cache_to_disk, sort_methods, view_mode, content)

    @staticmethod
    def resolve_url(path='', play_item=None, succeeded=True):
        """
        Create and return a context dict to resolve a playable URL

        :param path: the path to a playable media.
        :type path: str or unicode
        :param play_item: a dict of item properties as described in the class docstring.
            It allows to set additional properties for the item being played, like graphics, metadata etc.
            if ``play_item`` parameter is present, then ``path`` value is ignored, and the path must be set via
            ``'path'`` property of a ``play_item`` dict.
        :type play_item: dict
        :param succeeded: if ``False``, Kodi won't play anything
        :type succeeded: bool
        :return: context object containing necessary parameters
            for Kodi to play the selected media.
        :rtype: PlayContext
        """
        return PlayContext(path, play_item, succeeded)

    @staticmethod
    def create_list_item(item):
        """
        Create an :class:`xbmcgui.ListItem` instance from an item dict

        :param item: a dict of ListItem properties
        :type item: dict
        :return: ListItem instance
        :rtype: xbmcgui.ListItem
        """
        list_item = xbmcgui.ListItem(label=item.get('label', ''),
                                     label2=item.get('label2', ''),
                                     path=item.get('path', ''))
        if int(xbmc.getInfoLabel('System.BuildVersion')[:2]) >= 16:
            art = item.get('art', {})
            art['thumb'] = item.get('thumb', '')
            art['icon'] = item.get('icon', '')
            art['fanart'] = item.get('fanart', '')
            item['art'] = art
        else:
            list_item.setThumbnailImage(item.get('thumb', ''))
            list_item.setIconImage(item.get('icon', ''))
            list_item.setProperty('fanart_image', item.get('fanart', ''))
        if item.get('art'):
            list_item.setArt(item['art'])
        if item.get('stream_info'):
            for stream, stream_info in item['stream_info'].iteritems():
                list_item.addStreamInfo(stream, stream_info)
        if item.get('info'):
            for media, info in item['info'].iteritems():
                list_item.setInfo(media, info)
        if item.get('context_menu') is not None:
            list_item.addContextMenuItems(item['context_menu'])
        if item.get('subtitles'):
            list_item.setSubtitles(item['subtitles'])
        if item.get('mime'):
            list_item.setMimeType(item['mime'])
        if item.get('properties'):
            for key, value in item['properties'].iteritems():
                list_item.setProperty(key, value)
        return list_item

    def _add_directory_items(self, context):
        """
        Create a virtual folder listing

        :param context: context object
        :type context: ListContext
        """
        self.log_debug('Creating listing from {0}'.format(str(context)))
        if context.content is not None:
            xbmcplugin.setContent(self._handle, context.content)  # This must be at the beginning
        listing = []
        for item in context.listing:
            is_folder = item.get('is_folder', True)
            if item.get('list_item') is not None:
                list_item = item['list_item']
            else:
                list_item = self.create_list_item(item)
                if item.get('is_playable'):
                    list_item.setProperty('IsPlayable', 'true')
                    is_folder = False
            listing.append((item['url'], list_item, is_folder))
        xbmcplugin.addDirectoryItems(self._handle, listing, len(listing))
        if context.sort_methods is not None:
            [xbmcplugin.addSortMethod(self._handle, method) for method in context.sort_methods]
        xbmcplugin.endOfDirectory(self._handle,
                                  context.succeeded,
                                  context.update_listing,
                                  context.cache_to_disk)
        if context.view_mode is not None:
            xbmc.executebuiltin('Container.SetViewMode({0})'.format(context.view_mode))

    def _set_resolved_url(self, context):
        """
        Resolve a playable URL

        :param context: context object
        :type context: PlayContext
        """
        self.log_debug('Resolving URL from {0}'.format(str(context)))
        if context.play_item is None:
            list_item = xbmcgui.ListItem(path=context.path)
        else:
            list_item = self.create_list_item(context.play_item)
        xbmcplugin.setResolvedUrl(self._handle, context.succeeded, list_item)
