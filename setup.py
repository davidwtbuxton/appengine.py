from distutils.core import Command, setup
from distutils.command.install import install as distutils_install


__version__ = '1.8.0'


class install(distutils_install):
    sub_commands = distutils_install.sub_commands + [('install_appengine', None)]


class install_appengine(Command):
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import appengine

        appengine.main(version=__version__)


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
