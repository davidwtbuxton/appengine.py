appengine.py
============

An MIT-licensed command-line tool to install the Google App Engine SDK.

Install from PyPI using::

    pip install appengine

Once installed, download and install the current version of the App Engine SDK::

    appengine.py install

appengine.py will find the current release of the SDK, download it to a temporary directory, then unzip the SDK to the default prefix directory and install symlinks for the development tools on the PATH.

You can update the installed SDK using::

    appengine.py update

appengine.py will check the installed version and update it if there is a newer version.


Usage
-----

Get help::

    appengine.py help


Check the current version::

    appengine.py check


Download the current version::

    appengine.py download [SDK] [--cache=DIR]


Install an SDK::

    appengine.py install [SDK] [--force] [--prefix=DIR] [--bindir=DIR]


When downloading/installing/updating you can optionally specify an SDK version. If you omit the SDK version appengine.py defaults to checking for the current version.

The SDK version can be specified as:

    - a version number in x.y.z format, e.g. `1.8.0`
    - an URL pointing to the zipped SDK to download / install
    - a local path to the zipped SDK


Environment variables
---------------------

If you don't specify an SDK version on the command line appengine.py will read the SDK version from the environment variable ``APPENGINEPY_SDK_VERSION`` (if set).

Thus the command `appengine.py install 1.8.0` is equivalent to setting the environment variable and installing like so::

    export APPENGINEPY_SDK_VERSION=1.8.0
    appengine.py install


Contributers
------------

Florian Rathgeber <florian.rathgeber@gmail.com>
