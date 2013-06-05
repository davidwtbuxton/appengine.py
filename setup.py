import os
import subprocess
import sys

from setuptools import Command, setup
from setuptools.command.install import install as _install


__version__ = '1.8.0'


class install(_install):
    sub_commands = _install.sub_commands + [('install_appengine', None)]


class install_appengine(Command):
    user_options = [('skip-install', None, 'skip installing the App Engine SDK')]
    boolean_options = ['skip-install']

    def initialize_options(self):
        self.skip_install = False

    def finalize_options(self):
        pass

    def get_outputs(self):
        return []

    def run(self):
        if not self.skip_install:
            os.environ.setdefault('APPENGINEPY_SDK_VERSION', __version__)
            filename = os.path.join(os.path.dirname(__file__), 'appengine.py')
            subprocess.call([sys.executable, filename])


setup(
    name = 'appengine',
    version = __version__,
    description = 'Google App Engine re-packaged for PyPI',
    author = 'David Buxton',
    author_email = 'david@gasmark6.com',
    url = 'https://github.com/davidwtbuxton/appengine.py',
    scripts = ['appengine.py'],
    cmdclass = {'install': install, 'install_appengine': install_appengine},
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
    ],
)
