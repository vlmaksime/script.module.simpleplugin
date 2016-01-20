Virtual Fodler Actions
======================

A virtual folder action creates in the Kodi UI a listing of items representing various child actions:
virtual sub-folders, playable items or misc. tasks. The listing is a Python :class:`list` object
where each item is a Python :class:`dict` which defines item's properties.
Each item can have the following properties:

* **label** -- item's label (default: ``''``).
* **label2** -- item's label2 (default: ``''``).
* **thumb** -- item's thumbnail (default: ``''``).
* **icon** -- item's icon (default: ``''``).
* **fanart** -- item's fanart (optional).
* **art** -- a :class:`dict` containing all item's graphic (see :meth:`xbmcgui.ListItem.setArt` for more info) --
  optional.
* **stream_info** -- a :class:`dict` of ``{stream_type: {param: value}}`` items
  (see :meth:`xbmcgui.ListItem.addStreamInfo`) -- optional.
* **info** --  a :class:`dict` of ``{media: {param: value}}`` items
  (see :meth:`xbmcgui.ListItem.setInfo`) -- optional.
* **context_menu** -- a :class:`list` or a :obj:`tuple`.
  A :class:`list` must contain 2-item tuples ``('Menu label', '<Built-in function>')`` where "Built-in function"
  is a `Kodi built-in function`_. If a :class:`list` is provided then the items from the tuples
  are added to the item's context menu. Alternatively, context_menu can be a 2-item :obj:`tuple`.
  The 1-st item is a :class:`list` as described above, and the 2-nd is a :class:`bool` value for replacing items.
  If ``True``, context menu will contain only the provided items.
  If ``False``, the items are added to the existing context menu. **context_menu** property is optional.
* **url** -- a callback URL for this list item. This is a mandatory item.
  A **url** can be provided directly as a :class:`str` or created using
  :meth:`get_url<simpleplugin.Plugin.get_url>` method.
* **is_playable** -- if ``True``, then this item is playable and must return a playable path or
  be resolved via :meth:`resolve_url<simpleplugin.Plugin.resolve_url>` static method (default: ``False``).
* **is_folder** -- if ``True`` then the item will open a lower-level sub-listing. if ``False``,
  the item either is a playable media or a general-purpose script
  which neither creates a virtual folder nor points to a playable media (default: ``True``).
  if **is_playable** is set to ``True``, then **is_folder** value implicitly assumed to be ``False``.
* **subtitles** -- the list of paths to subtitle files (optional).
* **mime** -- item's mime type (optional).
* **list_item** -- an :class:`xbmcgui.ListItem` instance (optional). It is used when you want to set all list item
  properties by yourself. If **list_item** property is present, all other properties,
  except for **url** and **is_folder**, are ignored.

An example of a listing that contains 1 item::

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

A virtual folder action must return either the :class:`list` described above, or a context :class:`dict`
created with :meth:`create_listing<simpleplugin.Plugin.create_listing>` static method.
This method is used to pass additional properties to Kodi.

:meth:`create_listing<simpleplugin.Plugin.create_listing>` method takes the following parameters:

* **listing**: :class:`list` -- the list of the plugin virtual folder items.
* **succeeded**: :class:`bool` -- if ``False`` Kodi won't open a new listing and stays on the current level.
* **update_listing**: :class:`bool` -- if ``True``, Kodi won't open a sub-listing but refresh the current one.
* **cache_to_disk**: :class:`bool` -- if ``False``, Kodi won't cache this listing to disk.
* **sort_methods**: -- a :obj:`tuple` of integer constants representing virtual folder sort methods.
  See :mod:`xbmcplugin` module documentation for more info.
* **view_mode**: :class:`int` -- a numeric code for a skin view mode.
  View mode codes are different in different skins except for ``50`` (basic listing),
  so you need to set a custom view mode depending on the current skin.
* **content**: :class:`str` -- current plugin content, e.g. 'movies' or 'episodes'.
  See :func:`xbmcplugin.setContent` for more info.

All parameters, except for **listing**, are optional.

Example::

  def virtual_folder_action(params):
      listing = get_listing(params)  # Some external function to create listing
      return Plugin.create_listing(listing,
                                   sort_methods=(SORT_METHOD_LABEL_IGNORE_THE,
                                                 SORT_METHOD_TITLE_IGNORE_THE,
                                                 SORT_METHOD_VIDEO_YEAR),
                                   view_mode=500)

.. _Kodi built-in function: http://kodi.wiki/view/List_of_built-in_functions
