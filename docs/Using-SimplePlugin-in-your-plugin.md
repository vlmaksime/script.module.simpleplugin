To use SimplePlugin in your plugin first you need to install SimplePlugin module addon in Kodi. An installable ZIP can be downloaded from [Releases](https://github.com/romanvm/script.module.simpleplugin/releases/latest) tab of this repository. I also plan to submit SimplePlugin module addon to the Kodi official repo.

Then you need to add the module in the [requires](http://kodi.wiki/view/Addon.xml#.3Crequires.3E) section of your plugin's **addon.xml** file as a dependency:
```xml
<requires>
  ...
  <import addon="script.module.simpleplugin" version="1.4"/>
  ...
</requires>
```
After that you can import SimplePlugin classes in your plugin's Python code and use them as you see fit.
