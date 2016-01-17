A playback action must resolve a playable URL (a path to a media file), i.e. obtain this URL one way or another and return the URL as a `str` or `unicode` object to Kodi. E.g.:
```python
def play_action(params):
    path = '/path/foo/bar.mp4'
    return path
```
In the upper-level virtual folder the respective item must have its **is_playable** property set to `True`.

Alternatively, [resolve_url()](http://romanvm.github.io/script.module.simpleplugin/docs/simpleplugin.Plugin-class.html#resolve_url) static method can be used to return a context dictionary with an additional `succeeded` Boolean parameter indicating whether the URL is resolved succesfully, e.g.:
```python
def play_action(params):
    path = get_path(params)  # Some external function to get a playable path
    return Plugin.resolve_url(path, succeeded=True)
```
