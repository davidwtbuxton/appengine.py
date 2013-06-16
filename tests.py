from __future__ import with_statement

from cStringIO import StringIO
import os
import unittest
import sys
import zipfile

import mock


def make_zip(members):
    """Creates a new ZipFile and returns a file-like object open for reading.

    For each tuple (name, bytes) in members, an archive member with the name
    and bytes is added to the zipfile.
    """
    filename = StringIO()
    archive = zipfile.ZipFile(filename, 'w')

    for name, bytes in members:
        archive.writestr(name, bytes)

    archive.close()
    filename.seek(0)

    return filename


class ExtractZipTestCase(unittest.TestCase):
    def test_extract_zip(self):
        from appengine import _extract_zip

        filename = make_zip([
            ('/foo', 'contents of foo'),
        ])
        zip = zipfile.ZipFile(filename)

        with mock.patch('appengine._extract_zip_member') as mock_extract:
            _extract_zip(zip, 'destination')

        self.assertEqual(mock_extract.call_count, 1)
        self.assertEqual(mock_extract.call_args_list[0][0][0], zip)
        self.assertEqual(mock_extract.call_args_list[0][0][1].filename, '/foo')


class ArgvParsingTestCase(unittest.TestCase):
    def test_opts(self):
        # Argument option parsing.
        from appengine import make_parser

        argv = '--prefix /foo/local --bindir /foo/local/bin --force'
        parser = make_parser()
        opts, args = parser.parse_args(argv.split())

        self.assertEqual(opts.force, True)
        self.assertEqual(opts.prefix, '/foo/local')
        self.assertEqual(opts.bindir, '/foo/local/bin')

    def test_default_opts(self):
        # Default values for missing options.
        from appengine import make_parser

        prefix = os.path.abspath(sys.prefix)

        parser = make_parser()
        opts, args = parser.parse_args(''.split())

        self.assertEqual(opts.force, False)
        self.assertEqual(opts.prefix, prefix)
        self.assertEqual(opts.bindir, os.path.join(prefix, 'bin'))


class ParseSpecTestCase(unittest.TestCase):
    def test_version(self):
        from appengine import _parse_spec

        url, version = _parse_spec('1.8.0')

        self.assertEqual(url, 'http://googleappengine.googlecode.com/files/google_appengine_1.8.0.zip')
        self.assertEqual(version, '1.8.0')

    def test_absolute_path(self):
        from appengine import _parse_spec

        url, version = _parse_spec('/foo/bar/google_appengine_1.8.0.zip')

        self.assertEqual(url, '/foo/bar/google_appengine_1.8.0.zip')
        self.assertEqual(version, None)


class IsURLPathTestCase(unittest.TestCase):
    def test_is_url(self):
        from appengine import is_url, is_path

        values = [
            'http://example.com/',
            'https://example.com/thing',
        ]

        for value in values:
            self.assertTrue(is_url(value))
            self.assertFalse(is_path(value))

    def test_is_path(self):
        from appengine import is_path, is_url

        values = [
            '/foo/bar',
            '/',
            'foo',
            'foo/bar/',
        ]

        for value in values:
            self.assertTrue(is_path(value))
            self.assertFalse(is_url(value))


if __name__ == "__main__":
    unittest.main()
