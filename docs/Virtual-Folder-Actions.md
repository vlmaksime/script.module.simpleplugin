A virtual folder action creates in the Kodi UI a listing of items representing various child actions: virtual sub-folders, playable items or misc. tasks. The listing is a Python `list` object where each item is a Python `dict` which defines item's properties. Each item can have the following properties:

* **label** - item's label (default: '').
* **label2** - item's label2 (default: '').
* **thumb** - item's thumbnail (default: '').
* **icon** - item's icon (default: '').
* **fanart** - item's fanart (optional).
* **art** - a dict containing all item's graphic (see [ListItem.setArt](http://romanvm.github.io/xbmcstubs/docs/xbmcgui.ListItem-class.html#setArt) for more info) - optional.
* **stream_info** - a dictionary of `{stream_type: {param: value}}` items (see [ListItem.addStreamInfo](http://romanvm.github.io/xbmcstubs/docs/xbmcgui.ListItem-class.html#addStreamInfo)) - optional.
* **info** -  a dictionary of `{media: {param: value}}` items (see [ListItem.setInfo](http://romanvm.github.io/xbmcstubs/docs/xbmcgui.ListItem-class.html#setInfo)) - optional
* **context_menu** - a `list` or a `tuple`. A `list` must contain 2-item tuples `('Menu label', 'Built-in function')` where `'Built-in function'` is a [Kodi built-in function](http://kodi.wiki/view/List_of_built-in_functions). If a `list` is provided then the items from the tuples are added to the item's context menu. Alternatively, context_menu can be a 2-item `tuple`. The 1-st item is a `list` as described above, and the 2-nd is a boolean value for replacing items. If `True`, context menu will contain only the provided items, if `False` - the items are added to the existing context menu. **context_menu** property is optional.
* **url** - a callback URL for this list item. This is a mandatory item. A **url** can be provided directly as a `str` or created using [[get_url()|get_url method]] method of a Plugin class instance.
* **is_playable** - if `True`, then this item is playable and must return a playable path or
    be resolved via [Plugin.resolve_url()](http://romanvm.github.io/script.module.simpleplugin/docs/simpleplugin.Plugin-class.html#resolve_url) static method (default: `False`).
* **is_folder** - if `True` then the item will open a lower-level sub-listing. if `False`,
    the item either is a playable media or a general-purpose script
    which neither creates a virtual folder nor points to a playable media (default: `True`).
    if **is_playable** is set to `True`, then **is_folder** value implicitly assumed to be `False`.
* **subtitles** - the list of paths to subtitle files (optional).
* **mime** - item's mime type (optional).
* **list_item** - an [xbmcgui.ListItem](http://romanvm.github.io/xbmcstubs/docs/xbmcgui.ListItem-class.html) instance (optional). It is used when you want to set all list item properties by yourself. If **list_item** property is present, all other properties, except for **url** and **is_folder**, are ignored. 

An example of 1-item listing:
```python
listing = [{    'label': 'Label',
                'label2': 'Label 2',
                'thumb': 'thumb.png',
                'icon': 'icon.png',
                'fanart': 'fanart.jpg',
                'art': {'clearart': 'clearart.png'},
                'stream_info': {'video': {'codec': 'h264', 'duration': 1200},
                                'audio': {'codec': 'ac3', 'language': 'en'}},
                'info': {'video': {'genre': 'Comedy', 'year': 2005}},
                'context_menu': ([('Menu Item', 'Action')], True),
                'url': 'plugin:/plugin.video.foo/?action=play&video=bar.mp4',
                'is_playable': True,
                'subtitles': ['/path/to/subtitles.en.srt', '/path/to/subtitles.uk.srt'],
                'mime': 'video/mp4'
                }]
```
A virtual folder action must return either the `list` described above, or a context `dict` created with [Plugin.create_listing](http://romanvm.github.io/script.module.simpleplugin/docs/simpleplugin.Plugin-class.html#create_listing) static method. This method is used to pass additional properties to Kodi. `create_listing()` method takes the following parameters:
* **listing**: list - the list of the plugin virtual folder items.
* **succeeded**: bool - if `False` Kodi won't open a new listing and stays on the current level.
* **update_listing**: bool - if `True`, Kodi won't open a sub-listing but refresh the current one.
* **cache_to_disk**: bool - if `False`, Kodi won't cache this listing to disk.
* **sort_methods**: - a `tuple` of integer constants representing virtual folder sort methods. See [xbmcplugin](http://romanvm.github.io/xbmcstubs/docs/xbmcplugin-module.html) module documentation for more info.
* **view_mode**: int - a numeric code for a skin view mode. View mode codes are different in different skins except for `50` (basic listing), so you need to set a custom view mode depending on the current skin.
* **content**: string - current plugin content, e.g. 'movies' or 'episodes'. See [xbmcplugin.setContent()](http://romanvm.github.io/xbmcstubs/docs/xbmcplugin-module.html#setContent) for more info.

All parameters, except for **listing**, are optional.

Example:
```python
def virtual_folder_action(params):
    listing = get_listing(params)  # Some external function to create listing
    return Plugin.create_listing(listing,
                                 sort_methods=(SORT_METHOD_LABEL_IGNORE_THE,
                                               SORT_METHOD_TITLE_IGNORE_THE,
                                               SORT_METHOD_VIDEO_YEAR),
                                 view_mode=500)
```