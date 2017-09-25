# SimplePlugin micro-framework for Kodi plugins

[![Build Status](https://travis-ci.org/romanvm/script.module.simpleplugin.svg?branch=master)](https://travis-ci.org/romanvm/script.module.simpleplugin)
[![codecov.io](https://codecov.io/github/romanvm/script.module.simpleplugin/coverage.svg?branch=master)](https://codecov.io/github/romanvm/script.module.simpleplugin?branch=master)

SimplePlugin micro-framework simplifies creating addons and content plugins for [Kodi](www.kodi.tv) mediacenter.
It was inspired by [xbmcswift2](https://github.com/jbeluch/xbmcswift2) and has some similar features
but SimplePlugin has different concept. Its 2 main goals are simplicity and support for
both content plugins and general purpose addons. SimplePlugin consists of one module
with no third-party dependencies, so you can simply include it in your plugin/addon.
Or you can install it in Kodi as a library module addon.


## Main Features

* Simplified creating of content lists: each list item is defined as a dictionary and the properties of the list item
  are set as dictionary `key: value` pairs.
* Automated plugin callback routing based on actions, that is, functions marked with
  a special decorator.
* Convenience methods for simplified access to addon/plugin parameters and settings.
* Persistent dictionary-like storage for storing addon's data.
* Caching decorator that allows to cache function return data for a specified amount time,
  for example, to reduce the frequency of polling data from some website.
* GNU Gettext emulation for simplified addon GUI localization: you can use English source strings in your Python code
  instead of non-obvious numeric string codes.

## Minimal Plugin Example

```python
from simpleplugin import Plugin

plugin = Plugin()

# Free video sample is provided by www.vidsplay.com

@plugin.action()
def root():
    """
    Root virtual folder
    
    This is mandatory item.
    """
    # Create 1-item list with a link to subfolder item
    return [{'label': 'Subfolder',
            'url': plugin.get_url(action='subfolder')}]


@plugin.action()
def subfolder():
    """Virtual subfolder"""
    # Create 1-item list with a link to a playable video.
    return [{'label': 'Ocean Birds',
            'thumb': 'http://www.vidsplay.com/vids/ocean_birds.jpg',
            'url': plugin.get_url(action='play', url='http://www.vidsplay.com/vids/ocean_birds.mp4'),
            'is_playable': True}]


# An action can take an optional argument that contain
# plugin call parameters parsed into a dict-like object.
# The params object allows to access parameters by key or by attribute
@plugin.action()
def play(params):
    """Play video"""
    # Return a string containing a playable video URL
    return params.url


if __name__ == '__main__':
    plugin.run()  # Start plugin
```

Read the [project documentation](http://romanvm.github.io/script.module.simpleplugin/) for more info about
SimplePlugin and its usage.

License: [GPL v.3](https://www.gnu.org/copyleft/gpl.html)
