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
from collections import defaultdict
import mock

cwd = os.path.dirname(os.path.abspath(__file__))
configdir = os.path.join(cwd, 'config')


# Fake test objects

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
        elif info_id == 'version':
            return '0.0.1'
        else:
            return ''

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
mock_xbmc.translatePath.side_effect = lambda path: path
# mock_xbmc.log = lambda msg, level: print(msg)

mock_xbmcgui = mock.MagicMock()
mock_xbmcgui.Window = FakeWindow

sys.modules['xbmcaddon'] = mock_xbmcaddon
sys.modules['xbmc'] = mock_xbmc
sys.modules['xbmcgui'] = mock_xbmcgui

# Import our module being tested
sys.path.append(os.path.join(cwd, 'script.module.simpleplugin3', 'libs'))
from simpleplugin import (Storage, Addon, Plugin, RoutedPlugin,
                          SimplePluginError, MemStorage, debug_exception)


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
            for key, value in storage.items():
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
            return str(time.time())

        test1 = tester('arg1')
        time.sleep(0.5)
        self.assertEqual(tester('arg1'), test1)
        self.assertNotEqual(tester('arg2'), test1)

    def test_mem_cached_decorator(self):
        with mock.patch.object(Addon, 'get_mem_storage', return_value={}):
            addon = Addon()

            @addon.mem_cached()
            def tester(*args):
                return str(time.time())

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
        self.assertEqual(_('Hello World!'), u'Привет, мир!')
        self.assertEqual(_('I love you.'), u'Я тебя люблю.')
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
        mock_actions = mock.MagicMock()
        mock_actions.root.return_value = None
        mock_actions.foo.return_value = None
        plugin.actions['root'] = mock_actions.root
        plugin.actions['foo'] = mock_actions.foo
        # Test calling 'root' action
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '']):
            plugin.run()
            mock_actions.root.assert_called_with({})
        # Test calling an action with parameters
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '?action=foo&param=bar']):
            plugin.run()
            mock_actions.foo.assert_called_with({'action': 'foo', 'param': 'bar'})

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
            self.assertEqual(param1, 'ham')
            self.assertEqual(param2, u'спам')

        with mock.patch('simpleplugin.sys.argv',
                        ['plugin://test.plugin/foo/ham/%D1%81%D0%BF%D0%B0%D0%BC/', '1', '']):
            plugin.run()

    def test_passing_int_and_float(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/foo/<int:param1>/<float:param2>')
        def test_func(param1, param2):
            self.assertEqual(param1, 28)
            self.assertEqual(param2, 3.1416)

        with mock.patch('simpleplugin.sys.argv', ['plugin://test.plugin/foo/28/3.1416/', '1', '']):
            plugin.run()

    def test_multiple_routes(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/foo', name='foo_route')
        @plugin.route('/bar/<param>')
        def test_func(param='ham'):
            self.assertEqual(param, 'ham')

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

        url = plugin.url_for('test', 'foo', u'тест')
        self.assertEqual(url, u'plugin://test.plugin/foo/%D1%82%D0%B5%D1%81%D1%82/')

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

    def test_building_url_int_float(self):
        plugin = RoutedPlugin('test.plugin')

        @plugin.route('/<int:param1>/<float:param2>/')
        def test():
            pass

        url = plugin.url_for('test', param1=1, param2=3.14)
        self.assertEqual(url, 'plugin://test.plugin/1/3.14/')


class DebugExceptionTestCase(unittest.TestCase):
    def test_debug_exception(self):
        def test_func():
            with debug_exception():
                raise RuntimeError

        self.assertRaises(RuntimeError, test_func)


if __name__ == '__main__':
    unittest.main()
