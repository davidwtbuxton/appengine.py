import os
import subprocess
import sys

from setuptools import Command, setup
from setuptools.command.install import install as _install

import appengine


class install(_install):
    # Custom setuptools install command which will run `appengine.py install` if
    # INSTALL_APPENGINE=1 or if `setup.py install --install-appengine`.
    user_options = _install.user_options + [('install-appengine', None, 'install the App Engine SDK')]
    boolean_options = _install.boolean_options + ['install-appengine']

    def initialize_options(self):
        _install.initialize_options(self)

        self.install_appengine = None

    def finalize_options(self):
        _install.finalize_options(self)

        if self.install_appengine is None:
            value = os.environ.get('INSTALL_APPENGINE', None)
            self.install_appengine = value.lower() in ('yes', 'true', '1') or False

    def run(self):
        _install.run(self)

        if self.install_appengine:
            filename = os.path.join(os.path.dirname(__file__), 'appengine.py')
            subprocess.call([sys.executable, filename, 'install'])


setup(
    name = 'appengine',
    version = appengine.__version__,
    description = 'Google App Engine re-packaged for PyPI',
    author = 'David Buxton',
    author_email = 'david@gasmark6.com',
    url = 'https://github.com/davidwtbuxton/appengine.py',
    scripts = ['appengine.py'],
    cmdclass = {'install': install},
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
    ],
)
