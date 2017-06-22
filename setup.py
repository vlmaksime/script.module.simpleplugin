#!/usr/bin/env python
# coding: utf-8
# Author: Roman Miroshnychenko aka Roman V.M.
# E-mail: romanvm@yandex.ua

import re
import os
import shutil
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

this_dir = os.path.dirname(os.path.abspath(__file__))
addon_dir = os.path.join(this_dir, 'script.module.simpleplugin')


def get_version():
    with open(os.path.join(addon_dir, 'addon.xml'), 'rb') as addon_xml:
        return re.search(r'(?<!xml )version="(.+?)"', addon_xml.read()).group(1)


shutil.copy(os.path.join(addon_dir, 'libs', 'simpleplugin.py'), this_dir)
try:
    setup(name='SimplePlugin',
          version=get_version(),
          description='SimplePlugin library for Kodi addons',
          author='Roman V.M.',
          author_email='romanvm@yandex.ua',
          url='https://github.com/romanvm/script.module.simpleplugin',
          license='GPL v.3',
          py_modules=['simpleplugin'],
          zip_safe=False,
         )
finally:
    os.remove(os.path.join(this_dir, 'simpleplugin.py'))
