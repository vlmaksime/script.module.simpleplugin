# SimplePlugin micro-framework for Kodi plugins

[![Build Status](https://travis-ci.org/romanvm/script.module.simpleplugin.svg?branch=master)](https://travis-ci.org/romanvm/script.module.simpleplugin)
[![codecov.io](https://codecov.io/github/romanvm/script.module.simpleplugin/coverage.svg?branch=master)](https://codecov.io/github/romanvm/script.module.simpleplugin?branch=master)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/0b11ece4ae73463ba3ce0b5836214ee6/badge.svg)](https://www.quantifiedcode.com/app/project/0b11ece4ae73463ba3ce0b5836214ee6)

SimplePlugin micro-framework simplifies creating addons and content plugins for [Kodi](www.kodi.tv) mediacenter.

## Main Features

* Simplified creating of content lists: each list item is defined as a dictionary and the properties of the list item
  are set as dictionary `key: value` pairs.
* Convenience methods for simplified access to addon/plugin parameters and settings.
* Persistent dictionary-like storage for storing permanent data.
* Caching decorator that allows to cache function return data for a specified amount time,
  for example, to reduce the frequency of polling data from some website.
* GNU Gettext emulation for simplified addon GUI localization: you can use English source strings in your Python code
  instead of non-obvious numeric string codes.

## Minimal Plugin Example

```python
from simpleplugin import Plugin

plugin = Plugin()

# Free video sample is provided by www.vidsplay.com

def root(params):
    """Root virtual folder"""
    # Create 1-item list with a link to subfolder item
    return [{'label': 'Subfolder',
            'url': plugin.get_url(action='subfolder')}]


def subfolder(params):
    """Virtual subfolder"""
    # Create 1-item list with a link to a playable video.
    return [{'label': 'Ocean Birds',
            'thumb': 'http://www.vidsplay.com/vids/ocean_birds.jpg',
            'url': plugin.get_url(action='play', url='http://www.vidsplay.com/vids/ocean_birds.mp4'),
            'is_playable': True}]


def play(params):
    """Play video"""
    # Return a string containing a playable video URL
    return params['url']

# Note that we map function objects *without* brackets ()!!!
plugin.actions['root'] = root  # Mandatory item
plugin.actions['subfolder'] = subfolder  # Subfolder action
plugin.actions['play'] = play  # Play action
if __name__ == '__main__':
    plugin.run()  # Start plugin
```

Read the [project documentation](http://romanvm.github.io/script.module.simpleplugin/) for more info about
SimplePlugin and its usage.

License: [GPL v.3](https://www.gnu.org/copyleft/gpl.html)
