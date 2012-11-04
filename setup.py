#!/usr/bin/env python

from distutils.core import setup

setup ( name='xbmcwebremote',
        version='1.0',
        description='XBMC Web Remote Server',
        author='Gerald Nilles',
        author_email='geraldnilles@gmail.com',
        scripts=["bin/xbmcwebremote"], # Move Main Script to /bin/ folder 
        data_files=[
#                ("/etc/init.d",["init/xbmcwebremote"]), # Init script for stating/stopping
                ("/etc/xbmcwebremote",["config.json"]), # Config File
                ("xbmcwebremote",["main.html"]) # HTML files
            ]
    )
