# coding: utf-8
# Module: tests
# Created on: 27.01.2016
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import sys
import unittest
import shutil
import time
from datetime import datetime
import mock

cwd = os.path.dirname(__file__)
configdir = os.path.join(cwd, 'config')


# Fake test objects

def fake_translate_path(path):
    return path


def fake_log(msg, level=0):
    print msg


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

# Mock Kodi Python API

mock_xbmcaddon = mock.MagicMock()
mock_xbmcaddon.Addon.side_effect = FakeAddon

mock_xbmc = mock.MagicMock()
mock_xbmc.LOGDEBUG = 0
mock_xbmc.LOGNOTICE = 2
mock_xbmc.log.side_effect = fake_log
mock_xbmc.translatePath.side_effect = fake_translate_path

mock_xbmcplugin = mock.MagicMock()
mock_xbmcgui = mock.MagicMock()

sys.modules['xbmcaddon'] = mock_xbmcaddon
sys.modules['xbmc'] = mock_xbmc
sys.modules['xbmcplugin'] = mock_xbmcplugin
sys.modules['xbmcgui'] = mock_xbmcgui

# Import our module being tested
sys.path.append(os.path.join(cwd, 'script.module.simpleplugin', 'libs'))
from simpleplugin import Storage, Addon, Plugin, PluginError


# Begin tests

class StorageTestCase(unittest.TestCase):
    """
    Test Storage class
    """
    def tearDown(self):
        os.remove(os.path.join(cwd, 'storage.pcl'))

    def test_storage_initialization(self):
        Storage(cwd)
        self.assertTrue(os.path.exists(os.path.join(cwd, 'storage.pcl')))

    def test_storing_value_in_storage_(self):
        with Storage(cwd) as storage1:
            storage1['key'] = 'value'
        del storage1
        with Storage(cwd) as storage2:
            self.assertEqual(storage2['key'], 'value')
        del storage2


class AddonTestCase(unittest.TestCase):
    """
    Test Addon class
    """
    def tearDown(self):
        shutil.rmtree(configdir, True)

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
        # Test calling a child action returning list
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '?action=foo&param=bar']):
            plugin.create_listing.reset_mock()
            mock_actions.foo.return_value = [{'label': 'foo'}]
            plugin.actions['foo'] = mock_actions.foo
            plugin.run()
            mock_actions.foo.assert_called_with({'action': 'foo', 'param': 'bar'})
            plugin.create_listing.assert_called_with([{'label': 'foo'}])
        # Test calling a child action returning a str
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '?action=play_str']):
            mock_actions.play_str.return_value = '/play/path'
            plugin.actions['play_str'] = mock_actions.play_str
            plugin.run()
            plugin.resolve_url.assert_called_with('/play/path')
        # Test calling a child action returning listing dict
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '?action=dict_listing']):
            plugin._add_directory_items.reset_mock()
            mock_actions.dict_listing.return_value = {'listing': 'test'}
            plugin.actions['dict_listing'] = mock_actions.dict_listing
            plugin.run()
            plugin._add_directory_items.assert_called_with({'listing': 'test'})
        # Test calling a child action returning play dict
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '?action=dict_play']):
            plugin._set_resolved_url.reset_mock()
            mock_actions.dict_play.return_value = {'path': 'test'}
            plugin.actions['dict_play'] = mock_actions.dict_play
            plugin.run()
            plugin._set_resolved_url.assert_called_with({'path': 'test'})
        # Test unregistered action
        with mock.patch('simpleplugin.sys.argv', ['test.plugin', '1', '?action=invalid']):
            self.assertRaises(PluginError, plugin.run)

if __name__ == '__main__':
    unittest.main()
