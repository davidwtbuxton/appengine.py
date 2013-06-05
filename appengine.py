#!/usr/bin/env python
from cStringIO import StringIO
import itertools
import logging
import os
import stat
import sys
import urllib2
import zipfile


__version__ = '0.1'
USER_AGENT = 'appengine.py/'+ __version__
VERSION_URL = 'https://appengine.google.com/api/updatecheck'
DOWNLOAD_URL = 'http://googleappengine.googlecode.com/files/google_appengine_{0}.zip'
_progress_chars = itertools.cycle('-\|/')
sdk_version_key = 'APPENGINEPY_SDK_VERSION'


def _print_progress(filename):
    filename.write('\b' + next(_progress_chars))


def get(url):
    request = urllib2.Request(url, headers={'User-Agent': USER_AGENT})

    return urllib2.urlopen(request)


def check_version(url=VERSION_URL):
    """Returns the version string for the latest SDK."""
    for line in urllib2.urlopen(url):
        if 'release:' in line:
            return line.split(':')[-1].strip(' \'"\r\n')


def download_sdk(version=None):
    if version is None:
        version = check_version()

    url = DOWNLOAD_URL.format(version)

    return get(url)


def install_sdk(filename, dest='.'):
    zip = zipfile.ZipFile(filename)
    zip.extractall(path=dest)

    return dest


def install_tools(src, dest):
    tools = [name for name in os.listdir(src) if name.endswith('.py')]
    all_x = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

    for name in tools:
        src_name = os.path.join(src, name)
        new_mode = os.stat(src_name).st_mode | all_x
        os.chmod(src_name, new_mode)
        dest_name = os.path.join(dest, name)
        os.symlink(src_name, dest_name)

    return tools


def main(version=None):
    if not version:
        version = check_version()

    try:
        os.environ['VIRTUAL_ENV']
    except KeyError:
        sys.stderr.write('Installation requires a virtual environment to be active.\n')
        return 1

    archive = StringIO()
    for line in download_sdk(version=version):
        archive.write(line)
    # zipfile wants a seek() method.
    archive.seek(0)

    install_path = install_sdk(archive, dest=sys.prefix)

    src = os.path.join(install_path, 'google_appengine')
    dest = os.path.join(os.environ['VIRTUAL_ENV'], 'bin')
    install_tools(src, dest)


if __name__ == "__main__":
    try:
        version = sys.argv[1]
    except IndexError:
        version = os.environ.get(sdk_version_key, None)

    sys.exit(main(version=version))
