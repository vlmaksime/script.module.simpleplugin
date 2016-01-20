Using SimplePlugin
==================

To use SimplePlugin in your plugin, first you need to install SimplePlugin module addon in Kodi.
An installable ZIP can be downloaded from `Releases`_ tab of this repository.
I also plan to submit SimplePlugin module addon to the Kodi official repo.

Then you need to add the module in the `requires`_ section of your plugin's :file:`addon.xml` file as a dependency:

.. code-block:: xml

  <requires>
    ...
    <import addon="script.module.simpleplugin" version="1.6"/>
    ...
  </requires>

After that you can import SimplePlugin classes in your plugin's Python code and use them as necessary.

.. _Releases: https://github.com/romanvm/script.module.simpleplugin/releases/latest
.. _requires: http://kodi.wiki/view/Addon.xml#.3Crequires.3E
