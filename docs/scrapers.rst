Python Scrapers and Subtitle Addons
===================================

In addition to content plugins, SimplePlugin can be used for subtitle addons,
and metadata scrapers written in Python (as of Kodi 18 "Leia").
Those types of addons also use :mod:`xbmcplugin` API and routing with ``'action'``
keyword in a paramstring so they can be implemented with
:class:`Plugin <simpleplugin.Plugin>` class.

Below is a simplified example based on a `demo Python movie scraper`_:

.. code-block:: python

  from simpleplugin import Plugin

  plugin = Plugin()


  @plugin.action()
  def find(params):
      title = params.title
      year = params.get('year', 0)
      print 'Find movie with title %s from year %i' %(title, int(year))
      yield {
          'label': 'Demo movie 1',
          'thumb': 'DevaultVideo.png',
          'offscreen': True,
          'properties': {'relevance': '0.5'},
      }
      yield {
          'label': 'Demo movie 2',
          'thumb': 'DevaultVideo.png',
          'offscreen': True,
          'properties': {'relevance': '0.3'},
      }


  @plugin.action()
  def getdetails(params):
      url = params.url
      if url == '/path/to/movie':
          li = {
              'label': 'Demo movie 1',
              'offscreen': True,
              'properties': {
                  'video.original.title': 'Original Title',
                  'video.sort_title': '2',
                  'video.ratings', '1',
              }
          }
      return plugin.resolve_url(play_item=li)


  @plugin.action()
  def getartwork(params):
      url = params.url
      if url == '456':
          li = {
              'label': 'Demo movie 1',
              'offscreen': True,
              'properties' {
                  'video.thumbs': '2',
                  'video.thumb1.url': 'DefaultBackFanart.png',
                  'video.thumb1.aspect': 'poster',
                  'video.thumb2.url': '/home/akva/Pictures/hawaii-shirt.png',
                  'video.thumb2.aspect': 'banner',
              }
          }
      return plugin.resolve_url(play_item=li)


  plugin.run()


.. _demo Python movie scraper: https://github.com/xbmc/xbmc/blob/master/addons/metadata.demo.movies/demo.py
