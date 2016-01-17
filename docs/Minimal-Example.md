Minimal working example of a plugin based on SimplePlugin is provided below:
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

An extended example of the usage of SimplePlugin micro-framework in a video plugin for Kodi can be found [here](https://github.com/romanvm/plugin.video.simpleplugin.example).