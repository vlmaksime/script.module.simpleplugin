Playback Actions
================

A playback action must resolve a playable URL (a path to a media file),
i.e. obtain this URL one way or another and return the URL as a :class:`str` or :obj:`unicode` object to Kodi.
E.g.::

  def play_action(params):
      path = '/path/foo/bar.mp4'
      return path

In the upper-level virtual folder the respective item must have its **is_playable** property set to ``True``.

Alternatively, :meth:`resolve_url<simpleplugin.Plugin.resolve_url>` static method can be used to return
a context dictionary with an additional ``succeeded`` :class:`bool` parameter indicating
whether the URL is resolved succesfully, e.g.::

  def play_action(params):
      path = get_path(params)  # Some external function to get a playable path
      return Plugin.resolve_url(path, succeeded=True)
