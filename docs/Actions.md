In SimplePlugin **actions** are Python callable objects - functions or methods - that are called when a SimplePlugin-based plugin is invoked in Kodi. "root" action is called when a user opens the plugin from Kodi UI, e.g. from "Video Addons" or "Music Addons" section. Child actions are called via a plugin callback URL containing "action" parameter in its paramstring, e.g. `plugin://plugin.video.foo/?action=bar` URL will call the action mapped to "bar" action string.

Actions are mapped to action strings via `actions` property of a Plugin class instance, e.g.:
```python
from simpleplugin import Plugin

plugin = Plugin()

def root(params):
    # Do some things
    ...
    return listing


def foo(params):
    # Do some other things
    ...
    return listing


plugin.actions['root'] = root  # Mandatory!
plugin.actions['foo'] = foo
plugin.run()
```
The "root" action is mandatory, i.e. a SimplePlugin based plugin **must** have at least a "root" action. Do note that we **map function objects without brackets ()!**

`plugin.actions['foo'] = foo` - Correct! :smile: 

`plugin.actions['foo'] = foo()` - **Wrong!!!** :rage:

An action callable automatically receives `params` parameter which is a Python `dict` containing a parsed plugin callback URL paramstring, e.g. for URL `plugin://plugin.video.foo/?action=bar&param=baz` `params` parameter will be `{'action': 'bar', 'param': 'baz'}`. For "root" action `params` will be an empty dict `{}`. Note that an action always receives `params` parameter even it does not use it. If `params` is missing from an action signature, a plugin will be terminated with an exception.

Kodi supports 3 types of actions: [[virtual folder actions|Virtual Folder Actions]], [[playback actions|Playback Actions]] and [[misc. actions|Misc Actions]].