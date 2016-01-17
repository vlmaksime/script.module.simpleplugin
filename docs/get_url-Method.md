[get_url](http://romanvm.github.io/script.module.simpleplugin/docs/simpleplugin.Plugin-class.html#get_url) convenience method helps you create callback URLs for your virtual folder items. It takes a base plugin URL with trailing `/` and a set of `param='value'` parameter pairs that are then passed to the child action. If a plugin URL is omitted then the current plugin URL is used. In this case `action` parameter needs to be provided to define the necessary child action.

To illustrate the principle let's assume that our plugin's ID is `plugin.video.foo`. Then this call
```python
plugin.get_url(action='bar', param1='baz', param2='blah')
```
will return the following URL:
```
plugin://plugin.video.foo/?action=bar&param1=baz&param2=blah
```
Parameter values must be ASCII strings (Python `str` objects). Unicode characters needs to be encoded with [base64](https://docs.python.org/2/library/base64.html) encoding and then decoded back to Unicode in a child action.

Note: `plugin.get_url()` without any parameters returns the plugin's root action URL.