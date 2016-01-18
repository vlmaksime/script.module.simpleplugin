Misc. Actions
=============

A misc action may perform any operations except for creating a virtual folder listing or resolving a playable URL.
Such action must not have a :keyword:`return` statement.
The respective item in the upper level virtual folder must have its ``is_folder`` property set to ``False``.

Example::

  def misc_action(params):
      xbcmgui.Dialog().notification('Hello', 'Hello world!')

This action will show a pop-up message in Kodi.
