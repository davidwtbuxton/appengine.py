appengine.py
============

A command-line tool to install the Google App Engine SDK.

Usage
-----

appengine.py [sdk]

Where sdk can be one of

 - a version number in x.y.z form
 - an URL pointing to a zipped SDK to download
 - a local path to a zipped SDK

Options:

    --prefix=<prefix>

Where to install the unzipped SDK. Defaults to sys.prefix.

    --bindir=<bindir>

Where to create symlinks for the SDK tools Defaults to $prefix/bin.

    --no-bindir
    
Do not create symlinks for the SDK tools. Defaults to false (i.e. default creates symlinks).

    --force

Overwrite existing SDK installation and tools.
