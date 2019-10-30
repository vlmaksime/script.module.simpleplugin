# SimplePlugin micro-framework for Kodi plugins

## The Project Is Suspended!

Unfortunately, at this moment I have don't have time or desire to develop
or maintain this project.
This may change in the future but now I suspend the project until further notice.
It means that from now on the project won't receive any updates and any new issues
will be ignored. Fell free to do with the code whatever you like within GPL v.3
terms and conditions.

[![Build Status](https://travis-ci.org/romanvm/script.module.simpleplugin.svg?branch=master)](https://travis-ci.org/romanvm/script.module.simpleplugin)
[![codecov.io](https://codecov.io/github/romanvm/script.module.simpleplugin/coverage.svg?branch=master)](https://codecov.io/github/romanvm/script.module.simpleplugin?branch=master)

SimplePlugin micro-framework simplifies creating addons and content plugins for [Kodi](www.kodi.tv) mediacenter.
It was inspired by [xbmcswift2](https://github.com/jbeluch/xbmcswift2) and has some similar features
but SimplePlugin has different concept. Its 2 main goals are simplicity and support for
both content plugins and general purpose addons. It supports routing plugin
calls using "pretty" URLs or URL query strings.

## Important Information!

`Plugin` class in SimplePlugin v.3.x is not compatible with earlier versions!
Previously `Plugin` class supported defining content listings as Python lists
of dictionaries with necessary properties. However, such excessive abstraction has
proved to be brittle and prone to breakage with Kodi Python API changes. So
now this abstraction has been removed and media content listings must be defined
with `xbmcplugin` module functions. That is why SimplePlugin v.3.x has
a different addon ID (`script.module.simpleplugin3`) sot that
not to break existing plugins that depend on it.
For SimplePlugin v.2.x code see `legacy` branch.

## Main Features

* Automated plugin call routing based on "pretty" URLs or URL query strings
  using function decorators.
* Convenience methods for simplified access to addon/plugin parameters and settings.
* Persistent dictionary-like storage for storing addon's data.
* Caching decorator that allows to cache function return data for a specified amount time,
  for example, to reduce the frequency of polling data from some website.
* GNU Gettext emulation for simplified addon GUI localization: you can use
  English source strings in your Python code instead of non-obvious numeric string codes.
* Compatible with Python 3 for future Kodi versions.
  
## Minimal Plugin Example with "Pretty" URL Routing

```python
import xbmcgui
import xbmcplugin
from simpleplugin import RoutedPlugin

plugin = RoutedPlugin()

# Free video sample is provided by www.vidsplay.com

@plugin.route('/')
def root():
    """
    Root virtual folder
    
    This is a mandatory item.
    """
    li = xbmcgui.ListItem('My Videos')
    li.setArt({'thumb': 'DefaultFolder.png'})
    # URL: plugin://plugin.video.foo/subfolder/
    url = plugin.url_for('subfolder')
    xbmcplugin.addDirectoryItem(plugin.handle, url, li, isFolder=True)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route('/subfolder')
def subfolder():
    """Virtual subfolder"""
    li = xbmcgui.ListItem('Ocean Birds')
    li.setArt({'thumb': 'http://www.vidsplay.com/vids/ocean_birds.jpg'})
    li.setProperty('isPlayable', 'true')
    url = plugin.url_for('play', video='http://www.vidsplay.com/vids/ocean_birds.mp4')
    xbmcplugin.addDirectoryItem(plugin.handle, url, li, isFolder=False)
    xbmcplugin.endOfDirectory(plugin.handle)


# An action can take an optional argument.
@plugin.route('/play/<video>')
def play(video):
    """Play video"""
    li = xbmcgui.ListItem(path=video)
    xbmcplugin.setResolvedUrl(plugin.handle, True, li)


if __name__ == '__main__':
    plugin.run()  # Start plugin
```

## Minimal Plugin Example with URL Query String Routing

```python
import xbmcgui
import xbmcplugin
from simpleplugin import Plugin

plugin = Plugin()

# Free video sample is provided by www.vidsplay.com

@plugin.action()
def root():
    """
    Root virtual folder
    
    This is a mandatory item.
    """
    li = xbmcgui.ListItem('My Videos')
    li.setArt({'thumb': 'DefaultFolder.png'})
    # URL: plugin://plugin.video.foo/?action=subfolder
    url = plugin.get_url(action=subfolder)
    xbmcplugin.addDirectoryItem(plugin.handle, url, li, isFolder=True)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.action()
def subfolder():
    """Virtual subfolder"""
    li = xbmcgui.ListItem('Ocean Birds')
    li.setArt({'thumb': 'http://www.vidsplay.com/vids/ocean_birds.jpg'})
    li.setProperty('isPlayable', 'true')
    url = plugin.get_url(action=play, video='http://www.vidsplay.com/vids/ocean_birds.mp4')
    xbmcplugin.addDirectoryItem(plugin.handle, url, li, isFolder=False)
    xbmcplugin.endOfDirectory(plugin.handle)


# An action can take an optional argument that contain
# plugin call parameters parsed into a dict-like object.
# The params object allows to access parameters by key or by attribute
@plugin.action()
def play(params):
    """Play video"""
    li = xbmcgui.ListItem(path=params.video)
    xbmcplugin.setResolvedUrl(plugin.handle, True, li)


if __name__ == '__main__':
    plugin.run()  # Start plugin
```

Read the [project documentation](http://romanvm.github.io/script.module.simpleplugin/) for more info about
SimplePlugin and its usage.

License: [GPL v.3](https://www.gnu.org/copyleft/gpl.html)
