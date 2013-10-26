import os

from setuptools import setup
from setuptools.command.install import install as _install

import appengine


class install(_install):
    """Custom install command which will run ``appengine.py install <version>``
    if the environment variable INSTALL_APPENGINE is set to the version string
    to install or when passing ``--install-appengine <version>`` to
    ``setup.py install``."""

    user_options = _install.user_options + [('install-appengine=', None,
        'install the given version of the App Engine SDK')]

    def initialize_options(self):
        _install.initialize_options(self)

        self.install_appengine = os.environ.get('INSTALL_APPENGINE', False)

    def run(self):
        _install.run(self)

        if self.install_appengine:
            appengine.install(self.install_appengine)


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
