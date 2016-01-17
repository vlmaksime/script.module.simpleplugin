# SimplePlugin Micro Framework

SimplePlugin micro-framework simplifies creating content plugins for [Kodi mediacenter](www.kodi.tv). It was inspired by [xbmcswift2 micro-framework](https://github.com/jbeluch/xbmcswift2) for the same purpose and has similar features like item lists containing dictionaries with item properties, persistent storage and cache decorator for functions.

But unlike xbmcswift2 which uses decorator-based callback routing mechanism similar to Bottle or Flask web-frameworks, SimplePlugin uses [[Actions]] which are Python callable objects mapped to plugin call parameters. A plugin based on SimplePlugin must have at least a "root" action which displays the plugin root virtual folder. Other actions are called via "action" call parameter, e.g. the URL
`
plugin://plugin.foo.bar/?action=foo
`
will call a function mapped to "foo" string.

In addition to simplifying creation of content lists in Kodi interface, SimplePlugin also provides [[Persistent Storage]] with dictionary-like interface to store arbitrary parameters.

SimplePlugin also provides function [[Cache Decorator]] similar to that of xbmcswift2 which allows to cache function return data for a specified amount of time.

Please select Wiki pages at the right **Contents** panel to get familiar with various SimplePlugin features.