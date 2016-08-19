Minimal Example
===============

This is a minimal example of a SimplePlugin-based plugin:

.. code-block:: python

  from simpleplugin import Plugin

  plugin = Plugin()

  # Free video sample is provided by www.vidsplay.com

  @plugin.action()
  def root(params):
      """
      Root virtual folder

      This action is mandatory.
      """
      # Create 1-item list with a link to subfolder item
      return [{'label': 'Subfolder',
              'url': plugin.get_url(action='subfolder')}]


  @plugin.action()
  def subfolder(params):
      """Virtual subfolder"""
      # Create 1-item list with a link to a playable video.
      return [{'label': 'Ocean Birds',
              'thumb': 'http://www.vidsplay.com/vids/ocean_birds.jpg',
              'url': plugin.get_url(action='play', url='http://www.vidsplay.com/vids/ocean_birds.mp4'),
              'is_playable': True}]


  @plugin.action()
  def play(params):
      """Play video"""
      # Return a string containing a playable video URL
      return params.url


  if __name__ == '__main__':
      plugin.run()  # Start plugin

An extended example of a video plugin for Kodi based on SimplePlugin micro-framework is available `here`_.

.. _here: https://github.com/romanvm/plugin.video.simpleplugin.example
