#!/usr/bin/env python
from __future__ import with_statement

from cStringIO import StringIO
import itertools
import logging
import optparse
import os
import stat
import sys
import urllib2
import urlparse
import zipfile


__version__ = '0.2'
USER_AGENT = 'appengine.py/' + __version__
VERSION_URL = 'https://appengine.google.com/api/updatecheck'
DOWNLOAD_URL = 'https://storage.googleapis.com/appengine-sdks/featured/google_appengine_{0}.zip'
sdk_version_key = 'APPENGINEPY_SDK_VERSION'


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
    if target[:1] == '/':
        target = target[1:]

    target = os.path.join(dest, target)

    # It's a directory.
    if target[-1:] == '/':
        parent = target[:-1]
        target = ''
    else:
        target = os.path.normpath(target)
        parent = os.path.dirname(target)

    if not os.path.exists(parent):
        os.makedirs(parent)

    if target:
        with open(target, 'w') as fh:
            fh.write(archive.read(member.filename))


def make_parser():
    """Returns a new option parser."""
    p = optparse.OptionParser()
    p.add_option('--prefix', metavar='DIR', help='install SDK in DIR')
    p.add_option('--bindir', metavar='DIR', help='install tools in DIR')
    p.add_option('--force', action='store_true', default=False,
        help='over-write existing installation')
    p.add_option('--no-bindir', action='store_true', default=False,
        help='do not install tools on DIR')

    return p


def parse_args(argv):
    """Returns a tuple of (opts, args) for arguments."""
    parser = make_parser()

    opts, args = parser.parse_args(argv[1:])

    # Use APPENGINEPY_SDK_VERSION if set.
    if not args and (sdk_version_key in os.environ):
        args = (os.environ[sdk_version_key],)

    return opts, args


def get(url):
    request = urllib2.Request(url, headers={'User-Agent': USER_AGENT})

    return urllib2.urlopen(request)


def check_version(url=VERSION_URL):
    """Returns the version string for the latest SDK."""
    for line in get(url):
        if 'release:' in line:
            return line.split(':')[-1].strip(' \'"\r\n')


def parse_sdk_name(name):
    """Returns a filename or URL for the SDK name.

    The name can be a version string, a remote URL or a local path.
    """
    # Version like x.y.z, return as-is.
    if all(part.isdigit() for part in name.split('.', 2)):
        return DOWNLOAD_URL % name

    # A network location.
    url = urlparse.urlparse(name)
    if url.scheme:
        return name

    # Else must be a filename.
    return os.path.abspath(name)


def open_sdk(url):
    """Open the SDK from the URL, which can be either a network location or
    a filename path. Returns a file-like object open for reading.
    """
    if urlparse.urlparse(url).scheme:
        return _download(url)
    else:
        return open(url)


def _download(url):
    """Downloads an URL and returns a file-like object open for reading,
    compatible with zipping.ZipFile (it has a seek() method).
    """
    fh = StringIO()

    for line in get(url):
        fh.write(line)

    fh.seek(0)
    return fh


def install_sdk(filename, dest='.', overwrite=False):
    zip = zipfile.ZipFile(filename)
    _extract_zip(zip, dest=dest)

    return dest


def install_tools(src, dest, overwrite=False):
    tools = [name for name in os.listdir(src) if name.endswith('.py')]
    all_x = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

    for name in tools:
        src_name = os.path.join(src, name)
        new_mode = os.stat(src_name).st_mode | all_x
        os.chmod(src_name, new_mode)
        dest_name = os.path.join(dest, name)

        if overwrite:
            try:
                os.unlink(dest_name)
            except OSError:
                pass

        os.symlink(src_name, dest_name)

    return tools


def main(argv):
    opts, args = parse_args(argv)
    version = args[0] if args else check_version()
    sdk_url = parse_sdk_name(version)

    archive = open_sdk(sdk_url)
    install_path = install_sdk(archive, dest=sys.prefix, overwrite=opts.force)

    src = os.path.join(install_path, 'google_appengine')
    dest = os.path.join(os.environ['VIRTUAL_ENV'], 'bin')
    install_tools(src, dest, overwrite=opts.force)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
