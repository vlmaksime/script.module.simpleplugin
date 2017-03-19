Debugging Addons
================

SimplePlugin offers :func:`debug_exception <simplelugin.debug_exception>`
context manager that allows to log diagnostic info about exceptions raised within its scope.
This diagnostic info helps to better understand the root cause of a possible error
by providing data about execution context at the moment when an exception happens.
The diagnostic info includes the following items:

- Module path.
- Code context.
- Global variables.
- Local variables.

After logging the diagnostic info the exception is re-raised.

Usage example:

.. code-block:: python

        with debug_exception():
            # Some error-prone code
            raise RuntimeError('Fatal error!')

The :func:`debug_exception <simplelugin.debug_exception>` context manager takes
an optional parameter that is a logger function which allows to customize log messages.
For example:

.. code-block:: python

  from simpleplugin import Plugin, debug_exception

  plugin = Plugin()

  ...

  with debug_exception(plugin.log_error):
      plugin.run()

Output example::

  19:13:20 T:11060   ERROR: plugin.video.simpleplugin.example [v.1.0.0]: Unhandled exception detected!
  19:13:20 T:11060   ERROR: plugin.video.simpleplugin.example [v.1.0.0]: *** Start diagnostic info ***
  19:13:20 T:11060   ERROR: plugin.video.simpleplugin.example [v.1.0.0]: File: D:\Kodi\portable_data\addons\plugin.video.simpleplugin.example\main.py
  19:13:20 T:11060   ERROR: plugin.video.simpleplugin.example [v.1.0.0]: Code context:
                                                 74:     # Get video categories
                                                 75:     categories = get_categories()
                                                 76:>    raise RuntimeError('Fatal error!')
                                                 77:     # Iterate through categories and yield list items for Kodi to display
                                                 78:     for category in categories:
  19:13:20 T:11060   ERROR: plugin.video.simpleplugin.example [v.1.0.0]: Global variables:
                                              Plugin = <class 'simpleplugin.Plugin'>
                                              VIDEOS = {'Animals': [{'name': 'Crab',
                                                            'thumb': 'http://www.vidsplay.com/vids/crab.jpg',
                                                            'video': 'http://www.vidsplay.com/vids/crab.mp4'},
                                                           {'name': 'Alligator',
                                                            'thumb': 'http://www.vidsplay.com/vids/alligator.jpg',
                                                            'video': 'http://www.vidsplay.com/vids/alligator.mp4'},
                                                           {'name': 'Turtle',
                                                            'thumb': 'http://www.vidsplay.com/vids/turtle.jpg',
                                                            'video': 'http://www.vidsplay.com/vids/turtle.mp4'}],
                                               'Cars': [{'name': 'Postal Truck',
                                                         'thumb': 'http://www.vidsplay.com/vids/us_postal.jpg',
                                                         'video': 'http://www.vidsplay.com/vids/us_postal.mp4'},
                                                        {'name': 'Traffic',
                                                         'thumb': 'http://www.vidsplay.com/vids/traffic1.jpg',
                                                         'video': 'http://www.vidsplay.com/vids/traffic1.avi'},
                                                        {'name': 'Traffic Arrows',
                                                         'thumb': 'http://www.vidsplay.com/vids/traffic_arrows.jpg',
                                                         'video': 'http://www.vidsplay.com/vids/traffic_arrows.mp4'}],
                                               'Food': [{'name': 'Chicken',
                                                         'thumb': 'http://www.vidsplay.com/vids/chicken.jpg',
                                                         'video': 'http://www.vidsplay.com/vids/bbqchicken.mp4'},
                                                        {'name': 'Hamburger',
                                                         'thumb': 'http://www.vidsplay.com/vids/hamburger.jpg',
                                                         'video': 'http://www.vidsplay.com/vids/hamburger.mp4'},
                                                        {'name': 'Pizza',
                                                         'thumb': 'http://www.vidsplay.com/vids/pizza.jpg',
                                                         'video': 'http://www.vidsplay.com/vids/pizza.mp4'}]}
                                              get_categories = <function get_categories at 0x129764B0>
                                              get_videos = <function get_videos at 0x129764F0>
                                              list_videos = <function list_videos at 0x129765B0>
                                              play = <function play at 0x129765F0>
                                              plugin = <simpleplugin.Plugin object ['plugin://plugin.video.simpleplugin.example/', '8', '']>
                                              root = <function root at 0x12976570>
                                              sys = <module 'sys' (built-in)>
                                              xbmc = <module 'xbmc' (built-in)>
                                              xbmcout = <class __main__.xbmcout at 0x134E8228>
  19:13:20 T:11060   ERROR: plugin.video.simpleplugin.example [v.1.0.0]: Local variables:
                                              categories = ['Food', 'Cars', 'Animals']
  19:13:20 T:11060   ERROR: plugin.video.simpleplugin.example [v.1.0.0]: **** End diagnostic info ****
  19:13:20 T:11060   ERROR: EXCEPTION Thrown (PythonToCppException) : -->Python callback/script returned the following error<--
                                               - NOTE: IGNORING THIS CAN LEAD TO MEMORY LEAKS!
                                              Error Type: <type 'exceptions.RuntimeError'>
                                              Error Contents: Fatal error!
                                              Traceback (most recent call last):
                                                File "D:\Kodi\portable_data\addons\plugin.video.simpleplugin.example\main.py", line 132, in <module>
                                                  plugin.run()
                                                File "D:\Kodi\portable_data\addons\script.module.simpleplugin\libs\simpleplugin.py", line 986, in run
                                                  self._add_directory_items(self.create_listing(result))
                                                File "D:\Kodi\portable_data\addons\script.module.simpleplugin\libs\simpleplugin.py", line 1108, in _add_directory_items
                                                  for item in context.listing:
                                                File "D:\Kodi\portable_data\addons\plugin.video.simpleplugin.example\main.py", line 76, in root
                                                  raise RuntimeError('Fatal error!')
                                              RuntimeError: Fatal error!
                                              -->End of Python script error report<--

