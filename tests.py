# coding: utf-8
# Module: tests
# Created on: 27.01.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

from __future__ import print_function
import os
import sys
import unittest
import shutil
import time
from datetime import datetime
from collections import defaultdict
from urllib import quote_plus
import mock

cwd = os.path.dirname(os.path.abspath(__file__))
configdir = os.path.join(cwd, 'config')


# Fake test objects

def fake_translate_path(path):
    return path


def test_generator():
    for i in xrange(6):
        yield {'label': 'item {0}'.format(i)}


class FakeAddon(object):
    def __init__(self, id_='test.addon'):
        self._id = id_
        self._settings = {}

    def getAddonInfo(self, info_id):
        if info_id == 'path':
            return cwd
        elif info_id == 'profile':
            return configdir
        elif info_id == 'id':
            return self._id

    def getSetting(self, setting_id):
        return self._settings.get(setting_id, '')

    def setSetting(self, setting_id, value):
        self._settings[setting_id] = value

    def getLocalizedString(self, id_):
        return {32000: u'Привет, мир!', 32001: u'Я тебя люблю.'}[id_]


class FakeWindow(object):
    def __init__(self, id_=-1):
        self._contents = defaultdict(str)

    def getProperty(self, key):
        return self._contents[key]

    def setProperty(self, key, value):
        self._contents[key] = value

    def clearProperty(self, key):
        del self._contents[key]

# Mock Kodi Python API

mock_xbmcaddon = mock.MagicMock()
mock_xbmcaddon.Addon.side_effect = FakeAddon

mock_xbmc = mock.MagicMock()
mock_xbmc.LOGDEBUG = 0
mock_xbmc.LOGNOTICE = 2
mock_xbmc.translatePath.side_effect = fake_translate_path

mock_xbmcplugin = mock.MagicMock()

mock_xbmcgui = mock.MagicMock()
mock_ListItem = mock.MagicMock()
mock_xbmcgui.ListItem.return_value = mock_ListItem
mock_xbmcgui.Window = FakeWindow

sys.modules['xbmcaddon'] = mock_xbmcaddon
sys.modules['xbmc'] = mock_xbmc
sys.modules['xbmcplugin'] = mock_xbmcplugin
sys.modules['xbmcgui'] = mock_xbmcgui

# Import our module being tested
sys.path.append(os.path.join(cwd, 'script.module.simpleplugin', 'libs'))
from simpleplugin import (Storage, Addon, Plugin, RoutedPlugin, SimplePluginError,
                          ListContext, PlayContext, MemStorage)


# Begin tests

class StorageTestCase(unittest.TestCase):
    """
    Test Storage class
    """
    def tearDown(self):
        try:
            os.remove(os.path.join(cwd, 'storage.pcl'))
        except OSError:
            pass

    def test_storage_initialization(self):
        with Storage(cwd) as storage:
            storage['foo'] = 'bar'
        self.assertTrue(os.path.exists(os.path.join(cwd, 'storage.pcl')))

    def test_storing_value_in_storage_(self):
        with Storage(cwd) as storage1:
            storage1['foo'] = 'bar'
        with Storage(cwd) as storage2:
            self.assertEqual(storage2['foo'], 'bar')

    def test_reading_storage_without_changes(self):
        with Storage(cwd) as storage1:
            storage1['foo'] = 'bar'
        last_mod = os.path.getmtime('storage.pcl')
        with Storage(cwd) as storage2:
            bar = storage2['foo']
        self.assertEqual(os.path.getmtime('storage.pcl'), last_mod)

    def test_storage_iteration(self):
        with Storage(cwd) as storage:
            storage['foo'] = 'foo'
            storage['bar'] = 'bar'
            storage['baz'] = 'baz'
            i = 0
            for key, value in storage.iteritems():
                self.assertEqual(key, value)
                i += 1
            self.assertEqual(i, 3)


class MemStorageTestCase(unittest.TestCase):
    def test_mem_storage(self):
        storage = MemStorage('foo')
        storage['ham'] = 'spam'
        self.assertEqual(storage['ham'], 'spam')
        self.assertTrue('ham' in storage)
        del storage['ham']
        self.assertFalse('ham' in storage)
        self.assertRaises(KeyError, storage.__getitem__, 'bar')
        self.assertRaises(KeyError, storage.__delitem__, 'bar')
        self.assertRaises(TypeError, storage.__getitem__, 5)
        self.assertRaises(TypeError, storage.__setitem__, 5, 5)
        self.assertRaises(TypeError, storage.__delitem__, 5)
        self.assertRaises(TypeError, storage.__contains__, 5)


class AddonTestCase(unittest.TestCase):
    """
    Test Addon class
    """
    def tearDown(self):
        shutil.rmtree(configdir, True)
        try:
            os.remove('icon.png')
            os.remove('fanart.jpg')
        except OSError:
            pass

    def test_addon_instance_creation(self):
        addon = Addon('test.addon')
        self.assertEqual(addon.id, 'test.addon')
        self.assertTrue(os.path.exists(os.path.join(cwd, 'config')))

    def test_addon_get_setting(self):
        """
        Test addon settings normalization
        """
        addon = Addon()
        addon.addon.setSetting('test', 'true')
        self.assertEqual(addon.get_setting('test'), True)
        addon.addon.setSetting('test', 'false')
        self.assertEqual(addon.get_setting('test'), False)
        addon.addon.setSetting('test', '10')
        self.assertEqual(addon.get_setting('test'), 10)
        addon.addon.setSetting('test', '1.0')
        self.assertEqual(addon.get_setting('test'), 1.0)
        addon.addon.setSetting('test', 'foo')
        self.assertEqual(addon.get_setting('test'), 'foo')

    def test_addon_set_setting(self):
        """
        Test saving addon settings
        """
        addon = Addon()
        addon.set_setting('test', True)
        self.assertEqual(addon.addon.getSetting('test'), 'true')
        addon.set_setting('test', False)
        self.assertEqual(addon.addon.getSetting('test'), 'false')
        addon.set_setting('test', 10)
        self.assertEqual(addon.addon.getSetting('test'), '10')

    def test_cached_decorator(self):
        addon = Addon()

        @addon.cached()
        def tester(*args):
            return str(datetime.now())

        test1 = tester('arg1')
        time.sleep(0.5)
        self.assertEqual(tester('arg1'), test1)
        self.assertNotEqual(tester('arg2'), test1)

    def test_mem_cached_decorator(self):
        with mock.patch.object(Addon, 'get_mem_storage', return_value={}):
            addon = Addon()

            @addon.mem_cached()
            def tester(*args):
                return str(datetime.now())

            test1 = tester('arg1')
            time.sleep(0.5)
            self.assertEqual(tester('arg1'), test1)
            self.assertNotEqual(tester('arg2'), test1)

    def test_icon_fanart_properties(self):
        addon = Addon()
        self.assertEqual(addon.icon, '')
        self.assertEqual(addon.fanart, '')
        open('icon.png', 'w').close()
        open('fanart.jpg', 'w').close()
        self.assertTrue('icon.png' in addon.icon)
        self.assertTrue('fanart.jpg' in addon.fanart)

    def test_gettext_not_initialized(self):
        addon = Addon()
        self.assertRaises(SimplePluginError, addon.gettext, 'Hello World!')

    def test_gettext_initialized(self):
        addon = Addon()
        _ = addon.initialize_gettext()
        self.assertEqual(_('Hello World!'), u'Привет, мир!'.encode('utf-8'))
        self.assertEqual(_('I love you.'), u'Я тебя люблю.'.encode('utf-8'))
        self.assertRaises(SimplePluginError, _, 'Foo Bar')


class PluginTestCase(unittest.TestCase):
    """
    Test Plugin class
    """
    def tearDown(self):
        shutil.rmtree(configdir, True)

    def test_get_params(self, *args):
        params = Plugin.get_params('param1=value1&param1=value2&param3=value3')
        self.assertEqual(params['param1'], ['value1', 'value2'])
        self.assertEqual(params['param3'], 'value3')

    def test_get_url(self, *args):
        plugin = Plugin('test.plugin')
        self.assertEqual(plugin.get_url(), 'plugin://test.plugin/')
        self.assertEqual(plugin.get_url(action='test'), 'plugin://test.plugin/?action=test')
        self.assertEqual(plugin.get_url('plugin://other.plugin/', param='value'), 'plugin://other.plugin/?param=value')

    def test_run(self):
        plugin = Plugin('test.plugin')
        plugin.create_listing = mock.MagicMock()
        plugin.resolve_url = mock.MagicMock()
        plugin._add_directory_items = mock.MagicMock()
        plugin._set_resolved_url = mock.MagicMock()
        mock_actions = mock.MagicMock()
        # Test calling 'root' action
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '']):
            mock_actions.root.return_value = [{'label': 'root'}]
            plugin.actions['root'] = mock_actions.root
            plugin.run()
            mock_actions.root.assert_called_with({})
            plugin.create_listing.assert_called_with([{'label': 'root'}])
        # Test calling 'root' action with no params
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '']):
            plugin.actions['root'] = lambda: [{'label': 'root'}]
            plugin.run()
            plugin.create_listing.assert_called_with([{'label': 'root'}])
        # Test calling a child action returning list or generator
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '?action=foo&param=bar']):
            plugin.create_listing.reset_mock()
            mock_actions.foo.return_value = [{'label': 'foo'}]
            plugin.actions['foo'] = mock_actions.foo
            plugin.run()
            mock_actions.foo.assert_called_with({'action': 'foo', 'param': 'bar'})
            plugin.create_listing.assert_called_with([{'label': 'foo'}])
            plugin.create_listing.reset_mock()
            generator = test_generator()
            mock_actions.foo.return_value = generator
            plugin.run()
            mock_actions.foo.assert_called_with({'action': 'foo', 'param': 'bar'})
            plugin.create_listing.assert_called_with(generator)
        # Test calling a child action returning a str
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '?action=play_str']):
            mock_actions.play_str.return_value = '/play/path'
            plugin.actions['play_str'] = mock_actions.play_str
            plugin.run()
            plugin.resolve_url.assert_called_with('/play/path')
        # Test calling a child action returning ListContext namedtuple
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '?action=tuple_listing']):
            plugin._add_directory_items.reset_mock()
            list_context = ListContext(
                [{
                    'url': 'plugin://foo',
                    'label': 'Foo',
                    'is_folder': True
                }],
                True,
                True,
                True,
                (0,),
                50,
                'movies',
                'Comedy'
            )

            mock_actions.dict_listing.return_value = list_context
            plugin.actions['tuple_listing'] = mock_actions.dict_listing
            plugin.run()
            plugin._add_directory_items.assert_called_with(list_context)
        # Test calling a child action returning PlayContext namedtuple
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '?action=tuple_play']):
            plugin._set_resolved_url.reset_mock()
            play_context = PlayContext('http://foo.bar', None, True)
            mock_actions.dict_play.return_value = play_context
            plugin.actions['tuple_play'] = mock_actions.dict_play
            plugin.run()
            plugin._set_resolved_url.assert_called_with(play_context)
        # Test unregistered action
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '?action=invalid']):
            self.assertRaises(SimplePluginError, plugin.run)

    def test_create_list_item(self):
        item = {
            'label': 'Label',
            'label2': 'Label2',
            'path': '/path/foo',
            'thumb': 'thumb.png',
            'icon': 'icon.png',
            'fanart': 'fanart.jpg',
            'art': {'poster': 'poster.jpg', 'banner': 'banner.jpg'},
            'stream_info': {'video': {'codec': 'h264'}},
            'info': {'video': {'genre': 'Comedy'}},
            'context_menu': ['item1', 'item2'],
            'subtitles': 'subs.srt',
            'mime': 'video/x-matroska',
            'content_lookup': True,
            'cast': [{
                'name': 'Michael C. Hall',
                'role': 'Dexter',
                'thumbnail': '/foo/dexter.jpg'
            }],
            'online_db_ids': {'imdb': 'tt12345', 'tvdb': '12345'},
            'ratings': [
                {'type': 'imdb', 'rating': 8.8},
                {'type': 'tvdb', 'rating': 9.9}
            ]
        }
        mock_xbmc.getInfoLabel.return_value = '15.0'
        Plugin.create_list_item(item)
        mock_xbmcgui.ListItem.assert_called_with(label='Label', label2='Label2', path='/path/foo')
        mock_ListItem.setThumbnailImage.assert_called_with('thumb.png')
        mock_ListItem.setIconImage.assert_called_with('icon.png')
        mock_ListItem.setProperty.assert_called_with('fanart_image', 'fanart.jpg')
        mock_ListItem.setArt.assert_called_with(item['art'])
        mock_ListItem.addStreamInfo.assert_called_with('video', {'codec': 'h264'})
        mock_ListItem.setInfo('video', {'genre': 'Comedy'})
        mock_ListItem.addContextMenuItems.assert_called_with(['item1', 'item2'])
        mock_ListItem.setSubtitles.assert_called_with('subs.srt')
        mock_ListItem.setMimeType.assert_called_with('video/x-matroska')
        # Test for Kodi Jarvis API
        mock_xbmc.getInfoLabel.return_value = '18.0'
        mock_ListItem.setArt.reset_mock()
        Plugin.create_list_item(item)
        mock_ListItem.setArt.assert_called_with({'icon': 'icon.png',
                                                 'thumb': 'thumb.png',
                                                 'fanart': 'fanart.jpg',
                                                 'poster': 'poster.jpg',
                                                 'banner': 'banner.jpg'})

    def test_add_directory_items(self):
        list_item1 = mock.MagicMock()
        context1 = ListContext(
            [{
                'url': 'plugin://foo',
                'list_item': list_item1,
                'is_folder': True
            }],
            True,
            True,
            True,
            (0,),
            50,
            'movies',
            'Action',
        )
        plugin = Plugin('test.plugin')
        plugin._handle = 1
        plugin.create_list_item = mock.MagicMock()
        plugin._add_directory_items(context1)
        mock_xbmcplugin.setContent.assert_called_with(1, 'movies')
        mock_xbmcplugin.addDirectoryItem.assert_called_with(1, 'plugin://foo', list_item1, True)
        mock_xbmcplugin.addSortMethod.assert_called_with(1, 0)
        mock_xbmcplugin.endOfDirectory.assert_called_with(1, True, True, True)
        mock_xbmc.executebuiltin.assert_called_with('Container.SetViewMode(50)')
        mock_xbmcplugin.addDirectoryItems.reset_mock()
        context2 = ListContext(
            [{
                'url' : 'plugin://foo',
                'label': 'Foo',
                'is_folder': True
            }],
            True,
            True,
            True,
            (0,),
            50,
            'movies',
            'Action'
        )
        list_item2 = mock.MagicMock()
        plugin.create_list_item.return_value = list_item2
        plugin._add_directory_items(context2)
        mock_xbmcplugin.addDirectoryItem.assert_called_with(1, 'plugin://foo', list_item2, True)
        mock_xbmcplugin.addDirectoryItems.reset_mock()
        list_item2.reset_mock()
        context3 = ListContext(
            [{
                'url' : 'plugin://foo',
                'label': 'Foo',
                'is_playable': True
            }],
            True,
            True,
            True,
            (0,),
            50,
            'movies',
            'Action'
        )
        plugin._add_directory_items(context3)
        list_item2.setProperty.assert_called_with('IsPlayable', 'true')
        mock_xbmcplugin.addDirectoryItem.assert_called_with(1, 'plugin://foo', list_item2, False)

    def test_set_resolved_url(self):
        context1 = PlayContext('http://foo.bar', None, True)
        plugin = Plugin('test.plugin')
        plugin._handle = 1
        mock_xbmcgui.ListItem.reset_mock()
        plugin._set_resolved_url(context1)
        mock_xbmcgui.ListItem.assert_called_with(path='http://foo.bar')
        mock_xbmcplugin.setResolvedUrl.assert_called_with(1, True, mock_ListItem)
        mock_xbmcplugin.setResolvedUrl.reset_mock()
        play_item = mock.MagicMock()
        context2 = PlayContext('http://foo.bar', play_item, True)
        list_item = mock.MagicMock()
        plugin.create_list_item = mock.MagicMock()
        plugin.create_list_item.return_value = list_item
        plugin._set_resolved_url(context2)
        plugin.create_list_item.assert_called_with(play_item)
        mock_xbmcplugin.setResolvedUrl.assert_called_with(1, True, list_item)

    def test_action_decorator(self):
        plugin = Plugin('test.plugin')

        @plugin.action()
        def foo(params):
            raise AssertionError('Test passed!')

        try:
            @plugin.action('foo')
            def bar(params):
                pass
        except SimplePluginError:
            pass
        else:
            self.fail('Duplicate action names test failed!')

        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '?action=foo']):
            self.assertRaises(AssertionError, plugin.run)


class RoutedPluginTestCase(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(configdir, True)

    def test_simple_routing(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/foo')
        def test_func():
            raise AssertionError('Test passed!')

        with mock.patch('simpleplugin.sys.argv', ['plugin://test.plugin/foo/', '1', '']):
            self.assertRaises(AssertionError, plugin.run)

    def test_passing_arguments(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/foo/<param1>/<param2>')
        def test_func(param1, param2):
            assert param1 == 'ham'
            assert param2 == 'spam'
            return []

        with mock.patch('simpleplugin.sys.argv', ['plugin://test.plugin/foo/ham/spam/', '1', '']):
            plugin.run()

    def test_passing_int_and_float(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/foo/<int:param1>/<float:param2>')
        def test_func(param1, param2):
            assert param1 == 28
            assert param2 == 3.1416
            return []

        with mock.patch('simpleplugin.sys.argv', ['plugin://test.plugin/foo/28/3.1416/', '1', '']):
            plugin.run()

    def test_passing_unicode(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/foo/<unicode:param>')
        def test_func(param):
            assert param == u'Тест'
            return []

        with mock.patch('simpleplugin.sys.argv',
                        ['plugin://test.plugin/foo/{0}/'.format(u'Тест'.encode('utf-8')),
                        '1',
                        '']):
            plugin.run()

    def test_multiple_routes(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/foo', name='foo_route')
        @plugin.route('/bar/<param>')
        def test_func(param='ham'):
            assert param == 'ham'
            return []

        with mock.patch('simpleplugin.sys.argv', ['plugin://test.plugin/foo/', '1', '']):
            plugin.run()
        with mock.patch('simpleplugin.sys.argv', ['plugin://test.plugin/bar/spam/', '1', '']):
            self.assertRaises(AssertionError, plugin.run)

    def test_routes_with_same_name(self):
        plugin = RoutedPlugin('test.plugin')
        try:
            @plugin.route('/foo')
            @plugin.route('/bar')
            def test_func():
                pass
        except SimplePluginError:
            pass
        else:
            self.fail('Added 2 routes with the same name!')


class PluginUrlForTestCase(unittest.TestCase):
    def tearDown(self):
        shutil.rmtree(configdir, True)

    def test_building_simple_url(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/foo')
        def test():
            pass

        self.assertEqual(plugin.url_for('test'), 'plugin://test.plugin/foo/')

    def test_building_url_args(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/<param1>/<param2>')
        def test():
            pass

        url = plugin.url_for('test', 'foo', 'bar')
        self.assertEqual(url, 'plugin://test.plugin/foo/bar/')

    def test_building_url_kwargs(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/<param1>/<param2>')
        def test():
            pass

        url = plugin.url_for('test', param1='foo', param2='bar')
        self.assertEqual(url, 'plugin://test.plugin/foo/bar/')

    def test_building_url_args_kwargs(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/<param1>/<param2>/<param3>')
        def test():
            pass

        url = plugin.url_for('test', 'foo', param2='bar', param3='spam')
        self.assertEqual(url, 'plugin://test.plugin/foo/bar/spam/')

    def test_building_url_args_kwargs_query(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/<param1>/<param2>/<param3>')
        def test():
            pass

        url = plugin.url_for('test', 'foo', param2='bar', param3='spam', param4='ham')
        self.assertEqual(url, 'plugin://test.plugin/foo/bar/spam/?param4=ham')

    def test_building_url_int_float_unicode(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/<int:param1>/<float:param2>/<unicode:param3>')
        def test():
            pass

        url = plugin.url_for('test', param1=1, param2=3.14, param3=u'Тест')
        self.assertEqual(url, 'plugin://test.plugin/1/3.14/{0}/'.format(quote_plus(u'Тест'.encode('utf-8'))))


if __name__ == '__main__':
    unittest.main()
