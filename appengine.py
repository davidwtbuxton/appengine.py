#!/usr/bin/env python
from __future__ import with_statement

from cStringIO import StringIO
import logging
import urlparse
import sys
import os
import optparse
import stat
import urllib2
import zipfile


__version__ = 'dev'
DOWNLOAD_URL = 'http://googleappengine.googlecode.com/files/google_appengine_%s.zip'
USER_AGENT = 'appengine.py/' + __version__
VERSION_URL = 'https://appengine.google.com/api/updatecheck'
SDK_DIRECTORY = 'google_appengine'
SDK_VERSION_KEY = 'APPENGINEPY_SDK_VERSION'


logging.basicConfig(level=logging.DEBUG)


class SDKCache(object):
    def __init__(self, path):
        self.path = os.path.abspath(path)

    def get_version(self, version):
        path = self._version_path(version)
        return open(path, 'rb')

    def add_version(self, version, filename):
        path = self._version_path(version)

        parent = os.path.dirname(path)
        if not os.path.exists(parent):
            os.makedirs(parent)

        chunk = 4096

        with open(path, 'w') as fh:
            buffer = ''

            while buffer:
                buffer = filename.read(chunk)
                fh.write(buffer)

    def _version_path(self, version):
        url = _download_url_for_version(version)
        name = os.path.basename(urlparse.urlparse(url).path)
        name = name.replace('/', '_')

        return os.path.join(self.path, name)


def _extract_zip(archive, dest):
    """Extract the ZipInfo object to a real file on the path targetpath."""
    # Python 2.5 compatibility.
    logging.debug('Extracting contents of %r', archive)
    members = archive.infolist()

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


def _download_url_for_version(version):
    return DOWNLOAD_URL % version


def _parse_spec(spec):
    """Returns a pair of URL and version for the given SDK version specification.
    """
    try:
        map(int, spec.split('.', 2))
    except ValueError:
        pass
    else:
        return _download_url_for_version(spec), spec

    if is_path(spec):
        return os.path.abspath(spec), None
    else:
        return spec, None


def is_path(value):
    """Returns True if the value is a filename."""
    parts = urlparse.urlparse(value)
    return parts.path == value


def is_url(value):
    return not is_path(value)


def _open(url):
    """Returns a file-like object open for reading, downloading if needed."""
    logging.debug('Opening %r', url)

    if is_url(url):
        return get(url)
    else:
        return open(url, 'rb')


def _install(filename, force=False, prefix=None, bindir=None):
    prefix = prefix or sys.prefix
    bindir = bindir or os.path.join(prefix, 'bin')
    zip = zipfile.ZipFile(filename)
    _extract_zip(zip, prefix)
    return _install_bin(os.path.join(prefix, SDK_DIRECTORY), dest=bindir)


def _install_bin(src, dest=None, force=False):
    dest = dest or os.path.join(sys.prefix, 'bin')
    tools = [name for name in os.listdir(src) if name.endswith('.py')]
    all_x = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

    for name in tools:
        logging.debug('Installing tool %r', name)

        src_name = os.path.join(src, name)
        new_mode = os.stat(src_name).st_mode | all_x
        os.chmod(src_name, new_mode)
        dest_name = os.path.join(dest, name)

        if force:
            try:
                os.unlink(dest_name)
            except OSError:
                pass

        os.symlink(src_name, dest_name)

    return tools


def get(url):
    """Returns a file-like object open for reading. For compatibility with
    zipfile, the object has a .seek() method.
    """
    headers = {'User-Agent': USER_AGENT}
    request = urllib2.Request(url, headers=headers)

    logging.debug('Downloading %r', url)
    return StringIO(urllib2.urlopen(request, timeout=30).read())


def _version(filename):
    for line in _open(filename):
        if 'release:' in line:
            return line.split(':')[-1].strip(' \'"\r\n')


def check_latest_version(url):
    """Returns the version string for the latest SDK."""
    return _version(url)


def check_installed_version(prefix):
    """Returns the version string for the installed SDK (if any)."""
    filename = os.path.join(prefix, SDK_DIRECTORY, 'VERSION')

    try:
        return _version(filename)
    except IOError:
        return None


def make_parser():
    usage = (
        'usage: %prog action [sdk] [options]\n\n'
        'Where action is one of install,download,check and sdk is an SDK version\n'
        'or an URL or a path to a zipped SDK distribution.'
    )
    prefix = os.path.abspath(sys.prefix)

    p = optparse.OptionParser(usage=usage)
    p.add_option('-c', '--cache', metavar='DIR',
        help='find previously cached SDK versions in DIR')
    p.add_option('-p', '--prefix', default=prefix, metavar='DIR',
        help='unzip the SDK in DIR')
    p.add_option('-b', '--bindir', default=os.path.join(prefix, 'bin'),
        metavar='DIR', help='install SDK tools in DIR')
    p.add_option('-f', '--force', action='store_true', default=False,
        help='overwrite a previously installed SDK')

    return p


def parse_args(argv):
    """Returns (action, sdk_version, opts). sdk_version is the 2nd positional
    argument, or the envrionment variable APPENGINEPY_SDK_VERSION or None.
    """
    parser = make_parser()
    opts, args = parser.parse_args()

    action = args[0]

    try:
        sdk = args[1]
    except IndexError:
        sdk = os.environ.get(SDK_VERSION_KEY, None)

    # Normalize paths.
    for name in ('cache', 'prefix', 'bindir'):
        value = getattr(opts, name)
        if value:
            value = os.path.abspath(os.path.expanduser(value))
            setattr(opts, name, value)

    return action, sdk, opts


def install(sdk, cache=None, prefix=None, bindir=None, force=None):
    if not hasattr(sdk, 'read'):
        sdk = _download(sdk, cache=cache)

    return _install(sdk, force=force, prefix=prefix, bindir=bindir)


def check(prefix):
    """Returns a tuple of the latest SDK version and the local installed SDK
    version (if any).
    """
    latest = check_latest_version(VERSION_URL)
    installed = check_installed_version(prefix)

    logging.info('Latest version is %r', latest)
    logging.info('Installed version is %r (%r)', installed, prefix)

    return latest, installed


def _download(sdk, cache=None):
    """Returns a file-like object open for reading, which may have been opened
    from the cache.
    """
    url, version = _parse_spec(sdk)

    # No cache, then download it and open directly.
    if not cache:
        return _open(url)

    cache = SDKCache(path=cache)

    try:
        return cache.get_version(version)
    except IOError:
        return _open(url)


def download(sdk, cache=None):
    filename = _download(sdk, cache=cache)

    # Not cached, so save to current directory.
    if not cache:
        url = filename.geturl()
        path = urlparse.urlparse(url).path
        name = os.path.basename(path)
        dest = os.path.join(os.getcwd(), name)

        with open(dest, 'wb') as fh:
            fh.write(filename.read())


def main(argv):
    try:
        action, sdk, opts = parse_args(argv[1:])
    except IndexError:
        parser = make_parser()
        parser.print_help()
        return 1

    if action == 'check' or sdk is None:
        check(opts.prefix)

    if action == 'install':
        install(sdk, cache=opts.cache, prefix=opts.prefix, bindir=opts.bindir, force=opts.force)

    elif action == 'download':
        download(sdk, cache=opts.cache)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
