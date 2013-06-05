#!/usr/bin/env python
from __future__ import with_statement

from cStringIO import StringIO
import itertools
import logging
import os
import stat
import sys
import urllib2
import zipfile


__version__ = '0.2'
USER_AGENT = 'appengine.py/' + __version__
VERSION_URL = 'https://appengine.google.com/api/updatecheck'
DOWNLOAD_URL = 'http://googleappengine.googlecode.com/files/google_appengine_%s.zip'
_progress_chars = itertools.cycle('-\|/')
sdk_version_key = 'APPENGINEPY_SDK_VERSION'


def _print_progress(filename):
    filename.write('\b' + next(_progress_chars))


def _extract_zip(archive, dest=None, members=None):
    """Extract the ZipInfo object to a real file on the path targetpath."""
    # Python 2.5 compatibility.
    dest = dest or os.getcwd()
    members = members or archive.infolist()

    for member in members:
        if isinstance(member, basestring):
            member = archive.getinfo(member)

        _extract_zip_member(archive, member, dest)


def _extract_zip_member(archive, member, dest):
    # Python 2.5 compatibility.
    target = member.filename
    if target[0] == '/':
        target = target[1:]

    target = os.path.join(dest, target)
    target = os.path.normpath(target)

    parent_name = os.path.dirname(target)
    if not os.path.exists(parent_name):
        os.makedirs(parent_name)

    with open(target, 'w') as fh:
        fh.write(archive.read(member.filename))


def get(url):
    request = urllib2.Request(url, headers={'User-Agent': USER_AGENT})

    return urllib2.urlopen(request)


def check_version(url=VERSION_URL):
    """Returns the version string for the latest SDK."""
    for line in get(url):
        if 'release:' in line:
            return line.split(':')[-1].strip(' \'"\r\n')


def download_sdk(version=None):
    if version is None:
        version = check_version()

    url = DOWNLOAD_URL % version

    return get(url)


def install_sdk(filename, dest='.'):
    zip = zipfile.ZipFile(filename)
    _extract_zip(zip, dest=dest)

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
